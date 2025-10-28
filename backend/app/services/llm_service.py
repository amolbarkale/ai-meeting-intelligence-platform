import logging
from langchain_community.llms.ollama import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.core.config import settings
from . import prompts

logger = logging.getLogger(__name__)

def generate_meeting_insights(transcript: str) -> dict:
    """
    Generates a comprehensive set of insights from a transcript using Ollama.
    
    Returns a dictionary containing:
    - abstract_summary
    - key_points
    - action_items
    - sentiment_analysis
    """
    logger.info(f"Initializing Ollama with model: {settings.OLLAMA_MODEL}")
    llm = Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)

    insights = {}

    # --- 1. Generate Abstract Summary ---
    try:
        logger.info("Generating abstract summary...")
        prompt_template = PromptTemplate(template=prompts.abstract_summary_prompt, input_variables=["transcript"])
        chain = LLMChain(llm=llm, prompt=prompt_template)
        insights['abstract_summary'] = chain.run(transcript=transcript)
    except Exception as e:
        logger.error(f"Error generating abstract summary: {e}")
        insights['abstract_summary'] = "Error: Could not generate summary."

    # --- 2. Generate Key Points ---
    try:
        logger.info("Generating key points...")
        prompt_template = PromptTemplate(template=prompts.key_points_prompt, input_variables=["transcript"])
        chain = LLMChain(llm=llm, prompt=prompt_template)
        insights['key_points'] = chain.run(transcript=transcript)
    except Exception as e:
        logger.error(f"Error generating key points: {e}")
        insights['key_points'] = "Error: Could not generate key points."

    # --- 3. Generate Action Items ---
    try:
        logger.info("Generating action items...")
        prompt_template = PromptTemplate(template=prompts.action_items_prompt, input_variables=["transcript"])
        chain = LLMChain(llm=llm, prompt=prompt_template)
        insights['action_items'] = chain.run(transcript=transcript)
    except Exception as e:
        logger.error(f"Error generating action items: {e}")
        insights['action_items'] = "Error: Could not generate action items."

    # --- 4. Generate Sentiment Analysis ---
    try:
        logger.info("Generating sentiment analysis...")
        prompt_template = PromptTemplate(template=prompts.sentiment_analysis_prompt, input_variables=["transcript"])
        chain = LLMChain(llm=llm, prompt=prompt_template)
        insights['sentiment_analysis'] = chain.run(transcript=transcript)
    except Exception as e:
        logger.error(f"Error generating sentiment analysis: {e}")
        insights['sentiment_analysis'] = "Error: Could not generate sentiment analysis."

    logger.info("All insights generated successfully.")
    return insights