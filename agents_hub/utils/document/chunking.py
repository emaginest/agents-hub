"""
Text chunking utilities for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import re
import logging
import nltk
from nltk.tokenize import sent_tokenize

# Initialize logger
logger = logging.getLogger(__name__)

# Download NLTK data if needed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    chunk_method: str = "token",
) -> List[str]:
    """
    Split text into chunks of specified size.
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        chunk_method: Chunking method ("token", "character", "sentence")
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    try:
        if chunk_method == "token":
            return _chunk_by_tokens(text, chunk_size, chunk_overlap)
        elif chunk_method == "character":
            return _chunk_by_characters(text, chunk_size, chunk_overlap)
        elif chunk_method == "sentence":
            return _chunk_by_sentences(text, chunk_size, chunk_overlap)
        else:
            logger.warning(f"Unknown chunk method: {chunk_method}, using token method")
            return _chunk_by_tokens(text, chunk_size, chunk_overlap)
    
    except Exception as e:
        logger.exception(f"Error chunking text: {e}")
        # Fallback to simple character chunking
        return _chunk_by_characters(text, chunk_size, chunk_overlap)


def _chunk_by_tokens(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Split text into chunks based on token count.
    
    Args:
        text: Text to split
        chunk_size: Maximum tokens per chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Simple tokenization by splitting on whitespace
    tokens = text.split()
    
    if not tokens:
        return []
    
    chunks = []
    i = 0
    
    while i < len(tokens):
        # Get chunk tokens
        chunk_tokens = tokens[i:i + chunk_size]
        chunks.append(" ".join(chunk_tokens))
        
        # Move to next chunk, considering overlap
        i += chunk_size - chunk_overlap
    
    return chunks


def _chunk_by_characters(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Split text into chunks based on character count.
    
    Args:
        text: Text to split
        chunk_size: Maximum characters per chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    i = 0
    
    while i < len(text):
        # Get chunk
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
        
        # Move to next chunk, considering overlap
        i += chunk_size - chunk_overlap
    
    return chunks


def _chunk_by_sentences(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Split text into chunks based on sentences, respecting chunk size.
    
    Args:
        text: Text to split
        chunk_size: Maximum characters per chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Split text into sentences
    sentences = sent_tokenize(text)
    
    if not sentences:
        return []
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence)
        
        # If adding this sentence would exceed the chunk size and we already have content,
        # finalize the current chunk and start a new one
        if current_size + sentence_size > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            # Keep some sentences for overlap
            overlap_size = 0
            overlap_sentences = []
            
            # Add sentences from the end of the current chunk for overlap
            for s in reversed(current_chunk):
                overlap_size += len(s)
                overlap_sentences.insert(0, s)
                
                if overlap_size >= chunk_overlap:
                    break
            
            # Start new chunk with overlap sentences
            current_chunk = overlap_sentences
            current_size = overlap_size
        
        # Add the sentence to the current chunk
        current_chunk.append(sentence)
        current_size += sentence_size
    
    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks
