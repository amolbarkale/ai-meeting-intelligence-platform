abstract_summary_prompt = """
You are an expert in language comprehension and summarization.
Read the following meeting transcript and summarize it into two or three abstract paragraphs.
Each paragraph should be between 2 and 4 sentences long.
Also, come up with a short, descriptive title for the meeting.
Retain the most important points to help a person understand the meeting's essence without reading the full text.
Avoid unnecessary details, tangential points, and do not use bullet points or lists.

<response-template>
## {{ TITLE }}
{{ ABSTRACT PARAGRAPHS }}
</response-template>

<transcript>
{transcript}
</transcript>
"""

key_points_prompt = """
You are an expert analyst. Your task is to identify the main points from the meeting transcript.
First, identify the most important ideas, findings, and topics.
Second, sort these points so the most discussed topic is first.
Format your response using the template below.

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
You are an expert in task identification.
Review the meeting transcript and identify all tasks, assignments, or actions that were agreed upon or mentioned as needing to be done.
List these action items clearly.

<response-template>
{{ FOR EACH ITEM IN ACTION_ITEM LIST }}
### {{ ITEM.NUMBER }}. {{ ITEM.NAME }}
- {{ ITEM.DETAIL }}
- {{ ITEM.DETAIL }}
</response-template>

<transcript>
{transcript}
</transcript>
"""

sentiment_analysis_prompt = """
You are an expert in language and emotion analysis.
Review the meeting transcript and provide an analysis of the overall sentiment.
Consider the tone, the emotion conveyed, and the context.
Indicate if the sentiment is generally positive, negative, or neutral, and provide brief explanations for your analysis.
Your answer should be concise and no more than three paragraphs.

<transcript>
{transcript}
</transcript>
"""

topic_modeling_prompt = """
You are an expert at identifying the core themes of a conversation.
Read the following meeting transcript and generate 3 to 5 relevant topic tags.
These tags should be concise and representative of the main subjects discussed.
Examples of good tags include: "Quarterly Review", "Project Brainstorm", "Client Call", "Marketing Strategy", "Budget Planning".

Output ONLY a single line of comma-separated tags.

<transcript>
{transcript}
</transcript>
"""

knowledge_graph_prompt = """
You are an expert in knowledge graph extraction.
Your task is to analyze the meeting transcript and identify the key entities and their relationships.
- **Nodes:** Identify the main concepts, projects, people, or decisions. These are your 'nodes'.
- **Edges:** Describe the relationships between these nodes (e.g., "discusses", "is responsible for", "is a part of"). These are your 'edges'.

You must output ONLY a valid JSON object with a 'nodes' key and an 'edges' key. Do not include any other text or explanation.

The JSON schema should be:
{{
  "nodes": [
    {{"id": "node_name_1", "label": "Node Label 1"}},
    {{"id": "node_name_2", "label": "Node Label 2"}}
  ],
  "edges": [
    {{"from": "node_name_1", "to": "node_name_2", "label": "relationship"}}
  ]
}}

<transcript>
{transcript}
</transcript>
"""