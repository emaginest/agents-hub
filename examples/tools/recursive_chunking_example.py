"""
Example demonstrating the recursive character text splitter.
"""

import asyncio
import os
import sys
import nltk

# Download NLTK data
nltk.download("punkt")

# Add the parent directory to the path so we can import the agents_hub package
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from agents_hub.utils.document import chunk_text


async def main():
    # Sample text with various separators
    sample_text = """
# Introduction

This is a sample document that demonstrates the recursive character text splitter.
The document has multiple paragraphs separated by double newlines.

## Section 1

This section contains several sentences. Each sentence can be used as a separator.
The recursive splitter will try to split by paragraphs first. If the paragraphs are
too large, it will split by newlines. If that's still too large, it will split by
sentences, then by spaces, and finally by characters if needed.

## Section 2

This is another section with multiple paragraphs.

This paragraph is separate from the one above.

### Subsection 2.1

The recursive splitter respects the document structure when possible.
It tries to keep related content together while ensuring chunks don't exceed
the specified size limit.

## Section 3

Let's see how the different chunking methods compare:
"""

    print("Original text length:", len(sample_text))

    # Print the source of the chunk_text function to verify we're using the right implementation
    import inspect

    print(f"\nUsing chunk_text from: {inspect.getmodule(chunk_text).__name__}")
    print(f"Function signature: {inspect.signature(chunk_text)}")

    # Default recursive chunking (with default separators)
    recursive_chunks = chunk_text(
        sample_text, chunk_size=200, chunk_overlap=50, chunk_method="recursive"
    )
    print(f"\nRecursive Chunks (default separators): {len(recursive_chunks)}")
    for i, chunk in enumerate(recursive_chunks):
        print(f"Chunk {i+1} ({len(chunk)} chars): {chunk[:50]}...")

    # Recursive chunking with custom separators
    custom_separators = ["## ", "\n\n", "\n", ". ", " "]
    recursive_custom_chunks = chunk_text(
        sample_text,
        chunk_size=200,
        chunk_overlap=50,
        chunk_method="recursive",
        separators=custom_separators,
    )
    print(f"\nRecursive Chunks (custom separators): {len(recursive_custom_chunks)}")
    for i, chunk in enumerate(recursive_custom_chunks):
        print(f"Chunk {i+1} ({len(chunk)} chars): {chunk[:50]}...")

    # Compare with other chunking methods
    token_chunks = chunk_text(
        sample_text, chunk_size=200, chunk_overlap=50, chunk_method="token"
    )
    print(f"\nToken Chunks: {len(token_chunks)}")

    char_chunks = chunk_text(
        sample_text, chunk_size=200, chunk_overlap=50, chunk_method="character"
    )
    print(f"\nCharacter Chunks: {len(char_chunks)}")

    sentence_chunks = chunk_text(
        sample_text, chunk_size=200, chunk_overlap=50, chunk_method="sentence"
    )
    print(f"\nSentence Chunks: {len(sentence_chunks)}")


if __name__ == "__main__":
    asyncio.run(main())
