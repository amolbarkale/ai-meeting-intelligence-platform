import json
import logging
import re
from functools import lru_cache
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase, basic_auth, Driver
from neo4j.exceptions import Neo4jError

from app.core.config import settings

logger = logging.getLogger(__name__)


class Neo4jNotConfigured(Exception):
    pass


@lru_cache(maxsize=1)
def _get_driver() -> Driver:
    if not settings.NEO4J_URI:
        raise Neo4jNotConfigured("NEO4J_URI is not configured")

    auth = None
    if settings.NEO4J_USERNAME and settings.NEO4J_PASSWORD:
        auth = basic_auth(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)

    logger.info("Initialising Neo4j driver for %s", settings.NEO4J_URI)
    return GraphDatabase.driver(settings.NEO4J_URI, auth=auth)


def close_driver():
    try:
        driver = _get_driver()
    except Neo4jNotConfigured:
        return
    driver.close()
    _get_driver.cache_clear()


def check_connection() -> bool:
    try:
        driver = _get_driver()
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            session.run("RETURN 1 AS ok").single()
        return True
    except Neo4jNotConfigured:
        logger.warning("Neo4j connection not configured")
        return False
    except Exception as exc:
        logger.error("Neo4j readiness check failed: %s", exc)
        return False


def _slugify(value: str, prefix: str, fallback: str = "item") -> str:
    if not value:
        return f"{prefix}-{fallback}"
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    cleaned = cleaned or fallback
    return f"{prefix}-{cleaned}"


def _parse_markdown_sections(markdown_text: Optional[str]) -> List[Dict[str, str]]:
    """
    Converts markdown heading sections to structured items.
    Input is expected in the form:

    ### Heading
    - detail
    - detail
    """
    if not markdown_text:
        return []

    items: List[Dict[str, str]] = []
    current_title = None
    current_details: List[str] = []

    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("###"):
            if current_title:
                items.append(
                    {
                        "title": current_title,
                        "details": "\n".join(current_details).strip(),
                    }
                )
            current_title = stripped.lstrip("#").strip()
            current_details = []
        elif stripped.startswith("-"):
            current_details.append(stripped.lstrip("-").strip())

    if current_title:
        items.append(
            {
                "title": current_title,
                "details": "\n".join(current_details).strip(),
            }
        )

    return [item for item in items if item["title"]]


def _parse_tags(tags_text: Optional[str]) -> List[str]:
    if not tags_text:
        return []
    return [tag.strip() for tag in tags_text.split(",") if tag.strip()]


def _parse_knowledge_graph(raw_kg: Optional[str]) -> Dict[str, List[Dict[str, Any]]]:
    default: Dict[str, List[Dict[str, Any]]] = {
        "nodes": [],
        "edges": [],
        "participants": [],
        "decisions": [],
        "timeline": [],
        "topics": [],
    }
    if not raw_kg:
        return default
    try:
        parsed = json.loads(raw_kg)
        if not isinstance(parsed, dict):
            return default

        def _safe_list(key: str) -> List[Dict[str, Any]]:
            value = parsed.get(key, [])
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
            return []

        def _safe_str_list(key: str) -> List[str]:
            value = parsed.get(key, [])
            if isinstance(value, list):
                return [str(item).strip() for item in value if str(item).strip()]
            return []

        nodes_raw = parsed.get("nodes", [])
        edges_raw = parsed.get("edges", [])

        safe_nodes = []
        for node in nodes_raw if isinstance(nodes_raw, list) else []:
            node_id = str(node.get("id") or node.get("name") or "").strip()
            label = str(node.get("label") or node.get("name") or node_id).strip()
            if node_id:
                safe_nodes.append({"id": node_id, "label": label})

        safe_edges = []
        for edge in edges_raw if isinstance(edges_raw, list) else []:
            source = str(edge.get("from") or edge.get("source") or "").strip()
            target = str(edge.get("to") or edge.get("target") or "").strip()
            relation = str(edge.get("label") or edge.get("type") or "related").strip()
            if source and target:
                safe_edges.append({"from": source, "to": target, "label": relation})

        participants = []
        for participant in _safe_list("participants"):
            name = str(participant.get("name") or "").strip()
            if not name:
                continue
            participants.append(
                {
                    "id": participant.get("id") or _slugify(name, "participant"),
                    "name": name,
                    "role": participant.get("role"),
                    "organization": participant.get("organization"),
                }
            )

        decisions = []
        for decision in _safe_list("decisions"):
            title = str(decision.get("title") or decision.get("summary") or "").strip()
            description = str(decision.get("description") or decision.get("detail") or "").strip()
            if not title and not description:
                continue
            decisions.append(
                {
                    "id": decision.get("id") or _slugify(title or description, "decision"),
                    "title": title or description[:80],
                    "description": description,
                    "owner": decision.get("owner"),
                    "due_date": decision.get("due_date"),
                }
            )

        timeline = []
        for entry in _safe_list("timeline"):
            label = str(entry.get("label") or entry.get("title") or "").strip()
            summary = str(entry.get("summary") or entry.get("details") or "").strip()
            start_time = entry.get("start_time") or entry.get("timecode")
            if not label and not summary:
                continue
            timeline.append(
                {
                    "id": entry.get("id") or _slugify(label or summary, "timeline"),
                    "label": label or summary[:40],
                    "summary": summary,
                    "start_time": start_time,
                }
            )

        topics = _safe_str_list("topics")

        return {
            "nodes": safe_nodes,
            "edges": safe_edges,
            "participants": participants,
            "decisions": decisions,
            "timeline": timeline,
            "topics": [{"id": _slugify(topic, "topic"), "name": topic} for topic in topics],
        }
    except json.JSONDecodeError:
        logger.warning("Invalid knowledge graph JSON; skipping")
        return default


def upsert_meeting_graph(meeting: Dict[str, Any]) -> None:
    """
    Persist meeting level data to Neo4j.

    meeting dict should contain:
        - id
        - original_filename
        - created_at / updated_at
        - summary, key_points, action_items, sentiment, tags, transcript, knowledge_graph
    """
    try:
        driver = _get_driver()
    except Neo4jNotConfigured:
        logger.info("Neo4j not configured - skipping graph persistence for meeting %s", meeting.get("id"))
        return

    tags = _parse_tags(meeting.get("tags"))
    key_points = _parse_markdown_sections(meeting.get("key_points"))
    action_items = _parse_markdown_sections(meeting.get("action_items"))
    graph_payload = _parse_knowledge_graph(meeting.get("knowledge_graph"))
    nodes = graph_payload["nodes"]
    edges = graph_payload["edges"]
    participants = graph_payload["participants"]
    decisions = graph_payload["decisions"]
    timeline = graph_payload["timeline"]
    topics = graph_payload["topics"]

    summary = meeting.get("summary") or ""
    transcript = meeting.get("transcript") or ""
    sentiment = meeting.get("sentiment") or ""

    # Extract title from summary if prefixed with markdown header
    meeting_title = meeting.get("summary_title")
    if not meeting_title and summary.startswith("##"):
        first_line = summary.splitlines()[0]
        meeting_title = first_line.lstrip("#").strip()

    payload = {
        "id": meeting.get("id"),
        "original_filename": meeting.get("original_filename"),
        "saved_filename": meeting.get("saved_filename"),
        "created_at": meeting.get("created_at"),
        "updated_at": meeting.get("updated_at"),
        "status": meeting.get("status"),
        "summary": summary,
        "key_points": meeting.get("key_points") or "",
        "action_items": meeting.get("action_items") or "",
        "sentiment": sentiment,
        "transcript": transcript,
        "tags_text": meeting.get("tags") or "",
        "title": meeting_title,
    }

    cypher = """
    MERGE (m:Meeting {id: $id})
    SET m += {
        original_filename: $original_filename,
        saved_filename: $saved_filename,
        created_at: $created_at,
        updated_at: $updated_at,
        status: $status,
        summary: $summary,
        key_points_markdown: $key_points,
        action_items_markdown: $action_items,
        sentiment: $sentiment,
        transcript: $transcript,
        tags_text: $tags_text,
        title: $title
    }
    """

    with driver.session(database=settings.NEO4J_DATABASE) as session:
        session.execute_write(lambda tx: tx.run(cypher, **payload))

        if tags:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (m:Meeting {id: $meeting_id})-[rel:HAS_TAG]->(:Tag)
                    DELETE rel
                    """,
                    meeting_id=meeting["id"],
                )
            )
            session.execute_write(
                lambda tx: tx.run(
                    """
                    UNWIND $tags AS tag
                    MERGE (t:Tag {name: tag})
                    MERGE (m:Meeting {id: $meeting_id})
                    MERGE (m)-[:HAS_TAG]->(t)
                    """,
                    tags=tags,
                    meeting_id=meeting["id"],
                )
            )

        if key_points:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (m:Meeting {id: $meeting_id})
                    MERGE (c:InsightCollection {meeting_id: $meeting_id, type: 'KEY_POINTS'})
                    MERGE (m)-[:HAS_INSIGHTS]->(c)
                    WITH c, $items AS items
                    FOREACH (item IN items |
                        MERGE (kp:Insight {meeting_id: $meeting_id, type: 'KEY_POINT', title: item.title})
                        SET kp.details = item.details
                        MERGE (c)-[:INCLUDES]->(kp)
                    )
                    """,
                    meeting_id=meeting["id"],
                    items=key_points,
                )
            )

        if action_items:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (m:Meeting {id: $meeting_id})
                    MERGE (c:InsightCollection {meeting_id: $meeting_id, type: 'ACTION_ITEMS'})
                    MERGE (m)-[:HAS_INSIGHTS]->(c)
                    WITH c, $items AS items
                    FOREACH (item IN items |
                        MERGE (ai:Insight {meeting_id: $meeting_id, type: 'ACTION_ITEM', title: item.title})
                        SET ai.details = item.details
                        MERGE (c)-[:INCLUDES]->(ai)
                    )
                    """,
                    meeting_id=meeting["id"],
                    items=action_items,
                )
            )

        # Clear existing participant/decision/timeline subgraphs to avoid duplication
        session.execute_write(
            lambda tx: tx.run(
                """
                MATCH (m:Meeting {id: $meeting_id})
                OPTIONAL MATCH (m)-[r:HAS_PARTICIPANT]->(p:Participant)
                DETACH DELETE p
                """,
                meeting_id=meeting["id"],
            )
        )
        session.execute_write(
            lambda tx: tx.run(
                """
                MATCH (m:Meeting {id: $meeting_id})
                OPTIONAL MATCH (m)-[r:HAS_DECISION]->(d:Decision)
                DETACH DELETE d
                """,
                meeting_id=meeting["id"],
            )
        )
        session.execute_write(
            lambda tx: tx.run(
                """
                MATCH (m:Meeting {id: $meeting_id})
                OPTIONAL MATCH (m)-[r:HAS_TIMELINE]->(t:TimelineEvent)
                DETACH DELETE t
                """,
                meeting_id=meeting["id"],
            )
        )

        if topics:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (m:Meeting {id: $meeting_id})-[rel:HAS_TOPIC]->(:Topic)
                    DELETE rel
                    """,
                    meeting_id=meeting["id"],
                )
            )

        if nodes:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    UNWIND $nodes AS node
                    MERGE (c:Concept {meeting_id: $meeting_id, node_id: node.id})
                    SET c.label = node.label
                    MERGE (m:Meeting {id: $meeting_id})
                    MERGE (m)-[:MENTIONS]->(c)
                    """,
                    meeting_id=meeting["id"],
                    nodes=nodes,
                )
            )

        if edges:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    UNWIND $edges AS edge
                    MATCH (source:Concept {meeting_id: $meeting_id, node_id: edge.from})
                    MATCH (target:Concept {meeting_id: $meeting_id, node_id: edge.to})
                    MERGE (source)-[r:RELATED_TO {meeting_id: $meeting_id}]->(target)
                    SET r.label = edge.label
                    """,
                    meeting_id=meeting["id"],
                    edges=edges,
                )
            )

        if participants:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (m:Meeting {id: $meeting_id})
                    UNWIND $participants AS participant
                    MERGE (p:Participant {participant_id: participant.id, meeting_id: $meeting_id})
                    SET p.name = participant.name,
                        p.role = participant.role,
                        p.organization = participant.organization
                    MERGE (m)-[:HAS_PARTICIPANT]->(p)
                    """,
                    meeting_id=meeting["id"],
                    participants=participants,
                )
            )

        if decisions:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (m:Meeting {id: $meeting_id})
                    UNWIND $decisions AS decision
                    MERGE (d:Decision {decision_id: decision.id, meeting_id: $meeting_id})
                    SET d.title = decision.title,
                        d.description = decision.description,
                        d.owner = decision.owner,
                        d.due_date = decision.due_date
                    MERGE (m)-[:HAS_DECISION]->(d)
                    """,
                    meeting_id=meeting["id"],
                    decisions=decisions,
                )
            )

        if timeline:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (m:Meeting {id: $meeting_id})
                    UNWIND $timeline AS entry
                    MERGE (t:TimelineEvent {timeline_id: entry.id, meeting_id: $meeting_id})
                    SET t.label = entry.label,
                        t.summary = entry.summary,
                        t.start_time = entry.start_time
                    MERGE (m)-[:HAS_TIMELINE]->(t)
                    """,
                    meeting_id=meeting["id"],
                    timeline=timeline,
                )
            )

        if topics:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (m:Meeting {id: $meeting_id})
                    UNWIND $topics AS topic
                    MERGE (t:Topic {name: topic.name})
                    MERGE (m)-[:HAS_TOPIC]->(t)
                    """,
                    meeting_id=meeting["id"],
                    topics=topics,
                )
            )


def search_meetings(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a simple text search across meeting summaries, tags, key points.
    """
    try:
        driver = _get_driver()
    except Neo4jNotConfigured:
        logger.info("Neo4j not configured - returning empty search results")
        return []

    query_lower = query.lower()
    cypher = """
    MATCH (m:Meeting)
    WHERE
        toLower(coalesce(m.summary, '')) CONTAINS $query
        OR toLower(coalesce(m.tags_text, '')) CONTAINS $query
        OR toLower(coalesce(m.transcript, '')) CONTAINS $query
    RETURN m.id AS id,
           m.title AS title,
           m.summary AS summary,
           m.created_at AS created_at,
           m.tags_text AS tags_text,
           m.original_filename AS original_filename
    ORDER BY m.created_at DESC
    LIMIT $limit
    """

    with driver.session(database=settings.NEO4J_DATABASE) as session:
        result = session.run(cypher, query=query_lower, limit=limit)
        records = []
        for record in result:
            records.append(
                {
                    "meeting_id": record.get("id"),
                    "title": record.get("title") or record.get("original_filename"),
                    "summary": record.get("summary"),
                    "created_at": record.get("created_at"),
                    "tags": record.get("tags_text"),
                }
            )
        return records


def fetch_meeting_context(meeting_id: str) -> Optional[Dict[str, Any]]:
    try:
        driver = _get_driver()
    except Neo4jNotConfigured:
        logger.info("Neo4j not configured - cannot fetch context")
        return None

    cypher = """
    MATCH (m:Meeting {id: $meeting_id})
    OPTIONAL MATCH (m)-[:HAS_TAG]->(t:Tag)
    WITH m, collect(DISTINCT t.name) AS tags
    OPTIONAL MATCH (m)-[:HAS_TOPIC]->(topic:Topic)
    WITH m, tags, collect(DISTINCT topic.name) AS topics
    OPTIONAL MATCH (m)-[:MENTIONS]->(c:Concept)
    WITH m, tags, topics, collect(DISTINCT c.label) AS concepts
    OPTIONAL MATCH (m)-[:HAS_PARTICIPANT]->(p:Participant)
    WITH m, tags, topics, concepts,
         collect(DISTINCT {
            participant_id: p.participant_id,
            name: p.name,
            role: p.role,
            organization: p.organization
         }) AS participants
    OPTIONAL MATCH (m)-[:HAS_DECISION]->(d:Decision)
    WITH m, tags, topics, concepts, participants,
         collect(DISTINCT {
            decision_id: d.decision_id,
            title: d.title,
            description: d.description,
            owner: d.owner,
            due_date: d.due_date
         }) AS decisions
    OPTIONAL MATCH (m)-[:HAS_TIMELINE]->(tl:TimelineEvent)
    WITH m, tags, topics, concepts, participants, decisions,
         collect(DISTINCT {
            timeline_id: tl.timeline_id,
            label: tl.label,
            summary: tl.summary,
            start_time: tl.start_time
         }) AS timeline
    OPTIONAL MATCH (m)-[:HAS_INSIGHTS]->(:InsightCollection {type: 'KEY_POINTS'})-[:INCLUDES]->(kp:Insight)
    WITH m, tags, topics, concepts, participants, decisions, timeline,
         collect(DISTINCT {title: kp.title, details: kp.details}) AS key_points
    OPTIONAL MATCH (m)-[:HAS_INSIGHTS]->(:InsightCollection {type: 'ACTION_ITEMS'})-[:INCLUDES]->(ai:Insight)
    RETURN
        m,
        tags,
        topics,
        concepts,
        participants,
        decisions,
        timeline,
        key_points,
        collect(DISTINCT {title: ai.title, details: ai.details}) AS action_items
    """

    with driver.session(database=settings.NEO4J_DATABASE) as session:
        record = session.run(cypher, meeting_id=meeting_id).single()
        if not record:
            return None
        meeting_node = record["m"]
        if not meeting_node:
            return None
        data = dict(meeting_node)
        data["tags"] = [tag for tag in record.get("tags", []) if tag]
        data["concepts"] = [concept for concept in record.get("concepts", []) if concept]
        data["topics"] = [topic for topic in record.get("topics", []) if topic]
        data["key_points_structured"] = [
            item for item in record.get("key_points", []) if item.get("title")
        ]
        data["action_items_structured"] = [
            item for item in record.get("action_items", []) if item.get("title")
        ]
        participants = record.get("participants", []) or []
        decisions = record.get("decisions", []) or []
        timeline = record.get("timeline", []) or []

        data["participants"] = [
            {
                "id": item.get("participant_id"),
                "name": item.get("name"),
                "role": item.get("role"),
                "organization": item.get("organization"),
            }
            for item in participants
            if item.get("name")
        ]
        data["decisions"] = [
            {
                "id": item.get("decision_id"),
                "title": item.get("title"),
                "description": item.get("description"),
                "owner": item.get("owner"),
                "due_date": item.get("due_date"),
            }
            for item in decisions
            if item.get("title") or item.get("description")
        ]
        data["timeline"] = sorted(
            [
                {
                    "id": item.get("timeline_id"),
                    "label": item.get("label"),
                    "summary": item.get("summary"),
                    "start_time": item.get("start_time"),
                }
                for item in timeline
                if item.get("label") or item.get("summary")
            ],
            key=lambda entry: entry.get("start_time") or "",
        )
        return data

