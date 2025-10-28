import logging
from langchain.chains.llm import LLMChain
from langchain_community.llms.ollama import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.mapreduce import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.config import settings

logger = logging.getLogger(__name__)

def summarize_transcript(transcript: str) -> str:
    """
    Summarizes a long transcript using the LangChain Map-Reduce strategy with Ollama.
    """
    logger.info("Initializing Ollama for summarization.")
    
    # Initialize the Ollama LLM
    llm = Ollama(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)

    # --- Map Prompt ---
    # This prompt is applied to each chunk of the transcript.
    map_template = """
    The following is a chunk of a meeting transcript:
    "{docs}"
    Based on this, please create a concise summary of the key points, decisions, and action items discussed in this chunk.
    Helpful Summary:
    """
    map_prompt = PromptTemplate.from_template(map_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    # --- Reduce Prompt ---
    # This prompt is applied to the combined summaries from the map step.
    reduce_template = """
    The following is a set of summaries from a meeting transcript:
    "{doc_summaries}"
    Take these summaries and synthesize them into a single, final summary.
    The summary should be well-structured, easy to read, and cover the most important topics, decisions, and action items from the entire meeting.
    Final Summary:
    """
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    # Takes a list of documents, combines them, and passes to the reduce_chain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="doc_summaries"
    )

    # Combines and iteratively reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        combine_documents_chain=combine_documents_chain,
        collapse_documents_chain=combine_documents_chain,
        token_max=4000, # Adjust as needed for your model's context window
    )

    # The main Map-Reduce chain
    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_documents_chain,
        document_variable_name="docs",
        return_intermediate_steps=False,
    )

    # Split the transcript into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, chunk_overlap=100
    )
    split_docs = text_splitter.create_documents([transcript])

    logger.info(f"Starting Map-Reduce summarization with {len(split_docs)} chunks.")
    
    # Execute the chain
    final_summary = map_reduce_chain.run(split_docs)
    
    logger.info("Summarization completed successfully.")
    return final_summary