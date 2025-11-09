abstract_summary_prompt = """
You are an expert meeting analyst. You will receive a transcript that could represent any conversational setting (e.g., executive sync, product demo, client interview, town hall, training, presentation, informal discussion).

Tasks:
1. Identify the overall purpose and context in a sentence (who is talking with whom, about what, and why).
2. Produce a concise summary (1–3 short paragraphs) that highlights the main narrative arc, major outcomes, and any noteworthy observations.
3. Provide a short, descriptive title that captures the spirit of the conversation.

Guidelines:
- Adapt tone and emphasis to match the meeting type (strategy vs. demo vs. Q&A, etc.).
- Prioritize clarity for someone who did not attend.
- Highlight major insights/results even if no formal decisions were made.
- If little happened, explain that briefly instead of fabricating content.

<response-template>
## {{ TITLE }}
{{ CONTEXT SENTENCE }}

{{ SUMMARY PARAGRAPHS }}
</response-template>

<transcript>
{transcript}
</transcript>
"""

key_points_prompt = """
You are an expert analyst studying a transcript that may come from any meeting or conversation format (planning session, panel interview, technical workshop, marketing presentation, etc.).

Tasks:
1. Extract the most salient themes, insights, or messages.
2. Respect the nature of the meeting. For a demo, include product capabilities; for a retrospective, mention what worked/what didn't; for an interview, surface key Q&A moments.
3. Keep each key point focused and informative. If a topic is brief or exploratory, note that succinctly.

Guidelines:
- Order key points by their prominence in the conversation.
- Use natural phrasing (no filler or repetition).
- If few substantive points exist, provide a short list and mention the limited scope.

<response-template>
{{ FOR EACH POINT IN KEY_POINT LIST }}
### {{ POINT.NAME }}
- {{ POINT.DETAIL }}
- {{ POINT.DETAIL }}
- {{ POINT.DETAIL }}
</response-template>

<transcript>
{transcript}
</transcript>
"""

action_items_prompt = """
You are an expert at detecting follow-up work from a transcript. The conversation may or may not contain explicit tasks (e.g., interviews, broadcasts, briefings).

Tasks:
1. Identify any concrete commitments, assignments, deadlines, or next steps that participants agreed to or implied.
2. If the session is informational (like a lecture or interview) and no actions emerge, say so explicitly.

Guidelines:
- Use concise language. If relevant, capture owners and timing.
- For exploratory ideas without commitment, call them “Proposed” or “Potential” rather than confirmed actions.

<response-template>
{{ IF ACTION ITEMS EXIST }}
{{ FOR EACH ITEM IN ACTION_ITEM LIST }}
### {{ ITEM.NUMBER }}. {{ ITEM.NAME }}
- {{ ITEM.DETAIL }}
- {{ ITEM.DETAIL }}
{{ ELSE }}
No explicit action items were identified in this discussion.
{{ ENDIF }}
</response-template>

<transcript>
{transcript}
</transcript>
"""

sentiment_analysis_prompt = """
You are an expert in language and emotion analysis. The transcript can represent any setting (collaborative brainstorm, sales pitch, interview, training, etc.).

Tasks:
1. Determine the prevailing sentiment (positive / negative / neutral / mixed) and explain why.
2. Call out noticeable shifts in tone, enthusiasm, friction, or stress.
3. Highlight relevant cues (word choice, reactions, outcomes) that influenced your assessment.

Guidelines:
- Keep the analysis concise (≤3 short paragraphs).
- Reflect the meeting context—e.g., “Curious but skeptical” for interviews, “Motivated” for kick-offs, etc.
- If sentiment varies by participant or phase, mention that.

<transcript>
{transcript}
</transcript>
"""

topic_modeling_prompt = """
You are an expert at identifying core themes from conversations. The discussion might be a presentation, interview, stand-up, negotiation, workshop, or another format.

Tasks:
1. Generate 3–6 concise tags that reflect the real subject matter.
2. Capture both domain topics (“Product Launch Readiness”) and format context when useful (“Customer Interview”).
3. Avoid generic filler (e.g., “Meeting” or “Discussion” alone).

Output ONLY a single line of comma-separated tags.

<transcript>
{transcript}
</transcript>
"""

knowledge_graph_prompt = """
You are an expert in knowledge graph extraction. The transcript can originate from any conversational scenario.

Tasks:
- Identify meaningful nodes: people, roles, teams, projects, deliverables, decisions, products, metrics, or memorable ideas.
- Identify edges that represent the relationships or interactions between nodes (ownership, influence, dependency, mention, comparison, question/answer, etc.).
- Adapt to the conversation style. For interviews, highlight interviewer ↔ candidate connections; for demos, capture product → feature → feedback; for brainstorming, map themes and responsibilities.

Requirements:
- Output ONLY a valid JSON object with 'nodes' and 'edges'. No commentary.
- Use concise, machine-friendly IDs (lowercase, hyphen/underscore) and clear labels.
- Skip empty sections; if no nodes/edges exist, return empty arrays.

Example schema:
{{
  "nodes": [
    {{"id": "alice", "label": "Alice – Product Manager"}},
    {{"id": "feature-x", "label": "Feature X"}}
  ],
  "edges": [
    {{"from": "alice", "to": "feature-x", "label": "owns"}}
  ]
}}

<transcript>
{transcript}
</transcript>
"""