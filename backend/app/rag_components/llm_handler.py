"""
LLM Handler for communicating with external LLM service.
Handles HTTP requests to the LLM Docker service.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from ..core.config import settings

logger = logging.getLogger(__name__)

# HTTP client for reuse
_http_client = None

def get_http_client():
    """Get or create HTTP client for LLM service communication."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=30.0)
    return _http_client

async def generate_answer_from_context(
    prompt_text: str,
    max_tokens: int = 500,
    temperature: float = 0.7,
    stop_sequences: Optional[list] = None
) -> Optional[str]:
    """
    Generate an answer from the LLM service using the provided context.
    
    Args:
        prompt_text: The complete prompt including context and question
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        stop_sequences: List of stop sequences to end generation
        
    Returns:
        Generated text or None if error
    """
    try:
        client = get_http_client()
        
        # Construct the request payload for Ollama API
        payload = {
            "model": "tinyllama",  # We'll use tinyllama model in Ollama
            "prompt": prompt_text,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "stop": stop_sequences or ["\n\n", "Human:", "Question:"]
            },
            "stream": False
        }
        
        # Make request to LLM service
        url = f"{settings.LLM_SERVICE_URL}{settings.LLM_COMPLETION_ENDPOINT}"
        response = await client.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract text from Ollama response format
            if "response" in result:
                generated_text = result["response"].strip()
                
                # Post-process the response
                if generated_text:
                    # Remove any leading/trailing whitespace
                    generated_text = generated_text.strip()
                    
                    # If the response is too short or seems incomplete, return None
                    if len(generated_text) < 10:
                        logger.warning("Generated response too short, returning None")
                        return None
                    
                    logger.info(f"Successfully generated response of {len(generated_text)} characters")
                    return generated_text
                else:
                    logger.warning("Empty response from LLM service")
                    return None
            else:
                logger.error("Invalid response format from LLM service")
                return None
        else:
            logger.error(f"LLM service returned status {response.status_code}: {response.text}")
            return None
            
    except httpx.TimeoutException:
        logger.error("Timeout when communicating with LLM service")
        return None
    except httpx.ConnectError:
        logger.error("Could not connect to LLM service")
        return None
    except Exception as e:
        logger.error(f"Error communicating with LLM service: {str(e)}")
        return None

def construct_rag_prompt(question: str, context_chunks: list, collection_name: str = "") -> str:
    """
    Construct a RAG prompt with context and question.
    
    Args:
        question: The user's question
        context_chunks: List of relevant Chunk objects
        collection_name: Name of the collection being searched
        
    Returns:
        Formatted prompt string
    """
    # Prepare context from chunks
    context_text = ""
    if context_chunks:
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source_info = f"Source: {chunk.source_pdf_filename}"
            if chunk.page_numbers:
                source_info += f", Pages: {chunk.page_numbers}"
            if chunk.article_title:
                source_info += f", Title: {chunk.article_title}"
            
            context_parts.append(f"Context {i}: {chunk.text}\n[{source_info}]")
        
        context_text = "\n\n".join(context_parts)
    
    # Construct the prompt
    if context_text:
        collection_info = f" from the '{collection_name}' collection" if collection_name else ""
        prompt = f"""You are a helpful assistant that answers questions based on the provided context{collection_info}. 

Context:
{context_text}

Question: {question}

Instructions:
- Answer the question based solely on the provided context
- If the context doesn't contain enough information to answer the question, respond with "I don't have enough information in the provided context to answer this question."
- Be concise and accurate
- When possible, mention which source(s) your answer comes from

Answer:"""
    else:
        prompt = f"""You are a helpful assistant. The user asked a question but no relevant context was found.

Question: {question}

Please respond with: "I don't have enough information to answer this question."

Answer:"""
    
    return prompt

def extract_answer_with_fallback(generated_text: str) -> str:
    """
    Extract and clean the answer from generated text.
    Apply fallback logic for unclear responses.
    
    Args:
        generated_text: Raw text from LLM
        
    Returns:
        Cleaned answer text
    """
    if not generated_text:
        return "I don't have enough information to answer this question."
    
    # Clean up the response
    cleaned_text = generated_text.strip()
    
    # Check for common "I don't know" patterns
    dont_know_patterns = [
        "i don't have enough information",
        "i cannot answer",
        "i don't know",
        "no information provided",
        "not enough context",
        "unable to determine",
        "insufficient information"
    ]
    
    if any(pattern in cleaned_text.lower() for pattern in dont_know_patterns):
        return "I don't have enough information in the provided context to answer this question."
    
    # If response is very short and doesn't seem to contain an answer
    if len(cleaned_text) < 20 and not any(word in cleaned_text.lower() for word in ["yes", "no", "true", "false"]):
        return "I don't have enough information in the provided context to answer this question."
    
    return cleaned_text

async def health_check_llm_service() -> bool:
    """
    Check if the LLM service is healthy and responding.
    
    Returns:
        True if service is healthy, False otherwise
    """
    try:
        client = get_http_client()
        
        # Try a simple generation request for Ollama
        test_payload = {
            "model": "tinyllama",
            "prompt": "Hello",
            "options": {
                "num_predict": 5,
                "temperature": 0.1
            },
            "stream": False
        }
        
        url = f"{settings.LLM_SERVICE_URL}{settings.LLM_COMPLETION_ENDPOINT}"
        response = await client.post(url, json=test_payload)
        
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"LLM service health check failed: {str(e)}")
        return False

async def close_http_client():
    """Close the HTTP client if it exists."""
    global _http_client
    if _http_client:
        await _http_client.aclose()
        _http_client = None
