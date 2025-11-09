import logging
from typing import Dict, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from . import prompts

logger = logging.getLogger(__name__)

def generate_meeting_insights(transcript: str) -> dict:
    """
    Generates a comprehensive set of insights from a transcript using OpenAI API.
    
    Returns a dictionary containing:
    - abstract_summary
    - key_points
    - action_items
    - sentiment_analysis
    """
    logger.info("Initializing OpenAI ChatOpenAI")
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        openai_api_key=settings.OPENAI_API_KEY
    )

    insights = {}

    # --- 1. Generate Abstract Summary ---
    try:
        logger.info("Generating abstract summary...")
        prompt_template = PromptTemplate(template=prompts.abstract_summary_prompt, input_variables=["transcript"])
        formatted_prompt = prompt_template.format(transcript=transcript)
        result = llm.invoke(formatted_prompt)
        insights['abstract_summary'] = result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        logger.error(f"Error generating abstract summary: {e}")
        insights['abstract_summary'] = "Error: Could not generate summary."

    # --- 2. Generate Key Points ---
    try:
        logger.info("Generating key points...")
        prompt_template = PromptTemplate(template=prompts.key_points_prompt, input_variables=["transcript"])
        formatted_prompt = prompt_template.format(transcript=transcript)
        result = llm.invoke(formatted_prompt)
        insights['key_points'] = result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        logger.error(f"Error generating key points: {e}")
        insights['key_points'] = "Error: Could not generate key points."

    # --- 3. Generate Action Items ---
    try:
        logger.info("Generating action items...")
        prompt_template = PromptTemplate(template=prompts.action_items_prompt, input_variables=["transcript"])
        formatted_prompt = prompt_template.format(transcript=transcript)
        result = llm.invoke(formatted_prompt)
        insights['action_items'] = result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        logger.error(f"Error generating action items: {e}")
        insights['action_items'] = "Error: Could not generate action items."

    # --- 4. Generate Sentiment Analysis ---
    try:
        logger.info("Generating sentiment analysis...")
        prompt_template = PromptTemplate(template=prompts.sentiment_analysis_prompt, input_variables=["transcript"])
        formatted_prompt = prompt_template.format(transcript=transcript)
        result = llm.invoke(formatted_prompt)
        insights['sentiment_analysis'] = result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        logger.error(f"Error generating sentiment analysis: {e}")
        insights['sentiment_analysis'] = "Error: Could not generate sentiment analysis."

    logger.info("All insights generated successfully.")
    
    # --- 5. NEW: Topic Modeling (Tags) ---
    try:
        logger.info("Generating topic tags...")
        prompt = PromptTemplate(template=prompts.topic_modeling_prompt, input_variables=["transcript"])
        formatted_prompt = prompt.format(transcript=transcript)
        result = llm.invoke(formatted_prompt)
        insights['tags'] = result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        logger.error(f"Error generating topic tags: {e}")
        insights['tags'] = "Error: Could not generate tags."

    # --- 6. NEW: Knowledge Graph ---
    try:
        logger.info("Generating knowledge graph data...")
        prompt = PromptTemplate(template=prompts.knowledge_graph_prompt, input_variables=["transcript"])
        formatted_prompt = prompt.format(transcript=transcript)
        result = llm.invoke(formatted_prompt)
        insights['knowledge_graph'] = result.content if hasattr(result, 'content') else str(result)
    except Exception as e:
        logger.error(f"Error generating knowledge graph: {e}")
        insights['knowledge_graph'] = '{"nodes": [], "edges": []}' # Default to empty graph on error

    logger.info("All insights generated successfully.")
    
    return insights


def _format_chat_history(history: List[Dict[str, str]]) -> str:
    if not history:
        return "No prior conversation."

    lines = []
    for turn in history:
        role = turn.get("role", "user").capitalize()
        content = turn.get("content", "").strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "No prior conversation."


def generate_meeting_chat_response(
    question: str,
    meeting_context: Dict[str, str | List[Dict[str, str]]],
    history: List[Dict[str, str]] | None = None,
) -> str:
    """
    Generate a conversational response grounded in meeting context.
    """
    logger.info("Generating meeting chat response")
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    prompt_template = PromptTemplate(
        template=prompts.meeting_chat_prompt,
        input_variables=[
            "meeting_title",
            "original_filename",
            "created_at",
            "tags",
            "summary",
            "key_points",
            "action_items",
            "structured_concepts",
            "chat_history",
            "question",
        ],
    )

    chat_history = _format_chat_history(history or [])
    formatted_prompt = prompt_template.format(
        meeting_title=meeting_context.get("title") or meeting_context.get("original_filename") or "Untitled Meeting",
        original_filename=meeting_context.get("original_filename", "Unknown"),
        created_at=meeting_context.get("created_at") or meeting_context.get("date") or "Unknown date",
        tags=", ".join(meeting_context.get("tags", [])) if isinstance(meeting_context.get("tags"), list) else (meeting_context.get("tags") or "None"),
        summary=meeting_context.get("summary") or "No summary available.",
        key_points=meeting_context.get("key_points_markdown") or meeting_context.get("key_points") or "No key points documented.",
        action_items=meeting_context.get("action_items_markdown") or meeting_context.get("action_items") or "No action items recorded.",
        structured_concepts="\n".join(meeting_context.get("concepts", [])) or "No concepts captured.",
        chat_history=chat_history,
        question=question,
    )

    result = llm.invoke(formatted_prompt)
    return result.content if hasattr(result, "content") else str(result)