from pydantic import BaseModel
from typing import List, Optional

class Chunk(BaseModel):
    id: str
    text: str
    article_title: str
    source_pdf_filename: str
    page_numbers: List[int]
    chunk_sequence_id: int
    collection_id: str
    pdf_db_id: int


def chunk_text(
    text_content: str,
    article_title: str,
    pdf_filename: str,
    collection_id: str,
    pdf_db_id: int,
    page_info: dict,
    chunk_size: int = 600,  # Reduced for better token approximation
    chunk_overlap: int = 100
) -> List[Chunk]:
    """
    Splits text_content into chunks of chunk_size tokens with chunk_overlap.
    Returns a list of Chunk objects with metadata.
    
    Note: Uses word-based approximation (1 token ≈ 0.75 words for English text)
    """
    import re
    
    # Simple whitespace tokenizer with better token approximation
    words = text_content.split()
    chunks = []
    i = 0
    chunk_sequence_id = 0
    
    while i < len(words):
        chunk_words = words[i:i+chunk_size]
        chunk_text = ' '.join(chunk_words)
        
        # Improved page number inference
        page_numbers = []
        if page_info:
            # Try to map based on text position in document
            text_position_ratio = i / len(words) if len(words) > 0 else 0
            estimated_page = int(text_position_ratio * len(page_info)) if page_info else 0
            page_numbers = page_info.get(estimated_page, page_info.get(0, [1]))
        
        chunk_id = f"{pdf_filename}_chunk_{chunk_sequence_id}"
        chunk = Chunk(
            id=chunk_id,
            text=chunk_text,
            article_title=article_title,
            source_pdf_filename=pdf_filename,
            page_numbers=page_numbers,
            chunk_sequence_id=chunk_sequence_id,
            collection_id=collection_id,
            pdf_db_id=pdf_db_id
                )
        chunks.append(chunk)
        i += chunk_size - chunk_overlap
        chunk_sequence_id += 1
    return chunks
