import json
import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

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


def _parse_knowledge_graph(raw_kg: Optional[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if not raw_kg:
        return [], []
    try:
        parsed = json.loads(raw_kg)
        nodes = parsed.get("nodes", []) if isinstance(parsed, dict) else []
        edges = parsed.get("edges", []) if isinstance(parsed, dict) else []
        safe_nodes = []
        for node in nodes:
            node_id = str(node.get("id") or node.get("name") or "").strip()
            label = str(node.get("label") or node.get("name") or node_id).strip()
            if node_id:
                safe_nodes.append({"id": node_id, "label": label})
        safe_edges = []
        for edge in edges:
            source = str(edge.get("from") or edge.get("source") or "").strip()
            target = str(edge.get("to") or edge.get("target") or "").strip()
            relation = str(edge.get("label") or edge.get("type") or "related").strip()
            if source and target:
                safe_edges.append(
                    {"from": source, "to": target, "label": relation}
                )
        return safe_nodes, safe_edges
    except json.JSONDecodeError:
        logger.warning("Invalid knowledge graph JSON; skipping")
        return [], []


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
    nodes, edges = _parse_knowledge_graph(meeting.get("knowledge_graph"))

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
    OPTIONAL MATCH (m)-[:MENTIONS]->(c:Concept)
    OPTIONAL MATCH (m)-[:HAS_INSIGHTS]->(:InsightCollection {type: 'KEY_POINTS'})-[:INCLUDES]->(kp:Insight)
    OPTIONAL MATCH (m)-[:HAS_INSIGHTS]->(:InsightCollection {type: 'ACTION_ITEMS'})-[:INCLUDES]->(ai:Insight)
    RETURN
        m,
        collect(DISTINCT t.name) AS tags,
        collect(DISTINCT c.label) AS concepts,
        collect(DISTINCT {title: kp.title, details: kp.details}) AS key_points,
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
        data["key_points_structured"] = [
            item for item in record.get("key_points", []) if item.get("title")
        ]
        data["action_items_structured"] = [
            item for item in record.get("action_items", []) if item.get("title")
        ]
        return data

