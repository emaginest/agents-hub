"""
Text chunking utilities for the Agents Hub framework.
"""

from typing import List, Optional
import re
import logging
import nltk
from nltk.tokenize import sent_tokenize

# Initialize logger
logger = logging.getLogger(__name__)

# Download NLTK data if needed
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)


# Simple sentence tokenizer as fallback if NLTK fails
def simple_sentence_tokenize(text):
    """Split text into sentences using simple regex."""
    return re.split(r"(?<=[.!?])\s+", text)


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    chunk_method: str = "token",
    separators: Optional[List[str]] = None,
) -> List[str]:
    """
    Split text into chunks of specified size.

    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        chunk_method: Chunking method ("token", "character", "sentence", "recursive")
        separators: Optional list of custom separators for recursive chunking
                   (in order of priority, e.g. ["\n\n", "\n", " ", ""])

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
        elif chunk_method == "recursive":
            return _chunk_by_recursive_characters(
                text, chunk_size, chunk_overlap, separators
            )
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
        chunk_tokens = tokens[i : i + chunk_size]
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
        chunk = text[i : i + chunk_size]
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
    try:
        sentences = sent_tokenize(text)
    except Exception as e:
        logger.warning(
            f"NLTK sentence tokenization failed: {e}. Using fallback tokenizer."
        )
        sentences = simple_sentence_tokenize(text)

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


def _chunk_by_recursive_characters(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: Optional[List[str]] = None,
) -> List[str]:
    """
    Split text recursively using a list of separators.

    This is a recursive character text splitter that splits on a list of separators
    in order of priority. If the text doesn't contain any of the separators or if
    the chunks are too large after splitting, it will use the next separator in the list.

    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        separators: List of separators to use for splitting, in order of priority
                   If None, defaults to ["\n\n", "\n", ". ", " ", ""]

    Returns:
        List of text chunks
    """
    # Default separators if none provided
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    # If we're at the last separator or the text is smaller than the chunk size, return the text
    if len(text) <= chunk_size:
        return [text]

    # Get the current separator
    if not separators:
        # No more separators, use character chunking as fallback
        return _chunk_by_characters(text, chunk_size, chunk_overlap)

    separator = separators[0]
    next_separators = separators[1:] if len(separators) > 1 else []

    # Split the text by the current separator
    if separator == "":
        # Empty separator means we're doing character chunking
        return _chunk_by_characters(text, chunk_size, chunk_overlap)

    splits = text.split(separator)

    # If the split didn't work (only one chunk) and we have more separators, try the next one
    if len(splits) == 1:
        if next_separators:
            return _chunk_by_recursive_characters(
                text, chunk_size, chunk_overlap, next_separators
            )
        else:
            # No more separators and splitting didn't work, fall back to character chunking
            return _chunk_by_characters(text, chunk_size, chunk_overlap)

    # Process the splits
    chunks = []
    current_chunk = []
    current_length = 0

    for split in splits:
        split_length = len(split)

        # If adding this split would exceed the chunk size and we already have content,
        # finalize the current chunk and start a new one
        if (
            current_length + split_length + len(separator) > chunk_size
            and current_chunk
        ):
            # Join the current chunk with the separator
            chunk_text = separator.join(current_chunk)

            # If the chunk is still too large, recursively split it with the next separators
            if len(chunk_text) > chunk_size and next_separators:
                sub_chunks = _chunk_by_recursive_characters(
                    chunk_text, chunk_size, chunk_overlap, next_separators
                )
                chunks.extend(sub_chunks)
            else:
                chunks.append(chunk_text)

            # Calculate overlap - keep splits that fit within the overlap size
            overlap_length = 0
            overlap_splits = []

            for s in reversed(current_chunk):
                if overlap_length + len(s) + len(separator) <= chunk_overlap:
                    overlap_splits.insert(0, s)
                    overlap_length += len(s) + len(separator)
                else:
                    break

            # Start new chunk with overlap splits
            current_chunk = overlap_splits
            current_length = overlap_length

        # Add the split to the current chunk
        if split:
            current_chunk.append(split)
            current_length += split_length + len(separator)

    # Add the last chunk if it has content
    if current_chunk:
        chunk_text = separator.join(current_chunk)

        # If the chunk is still too large, recursively split it with the next separators
        if len(chunk_text) > chunk_size and next_separators:
            sub_chunks = _chunk_by_recursive_characters(
                chunk_text, chunk_size, chunk_overlap, next_separators
            )
            chunks.extend(sub_chunks)
        else:
            chunks.append(chunk_text)

    return chunks
