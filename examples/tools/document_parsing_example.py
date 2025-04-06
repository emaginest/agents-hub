"""
Example of using document parsing utilities in the Agents Hub framework.
"""

import os
import asyncio
import base64
from dotenv import load_dotenv

from agents_hub.utils.document import extract_text_from_pdf, extract_text_from_docx, chunk_text


def read_sample_file(file_path: str) -> bytes:
    """Read a sample file."""
    with open(file_path, "rb") as f:
        return f.read()


async def main():
    """Run the example."""
    # Check for sample files
    sample_pdf = "examples/tools/sample.pdf"
    sample_docx = "examples/tools/sample.docx"
    
    if not os.path.exists(sample_pdf):
        print(f"Sample PDF file not found: {sample_pdf}")
        print("Please create a sample PDF file for testing.")
        return
    
    if not os.path.exists(sample_docx):
        print(f"Sample DOCX file not found: {sample_docx}")
        print("Please create a sample DOCX file for testing.")
        return
    
    # Example 1: Extract text from PDF
    print("\n=== Example 1: Extract Text from PDF ===")
    pdf_result = extract_text_from_pdf(file_path=sample_pdf)
    print(f"PDF Text (first 500 chars): {pdf_result['text'][:500]}...")
    print(f"PDF Metadata: {pdf_result['metadata']}")
    print(f"PDF Pages: {len(pdf_result['pages'])}")
    
    # Example 2: Extract text from DOCX
    print("\n=== Example 2: Extract Text from DOCX ===")
    docx_result = extract_text_from_docx(file_path=sample_docx)
    print(f"DOCX Text (first 500 chars): {docx_result['text'][:500]}...")
    print(f"DOCX Metadata: {docx_result['metadata']}")
    print(f"DOCX Paragraphs: {len(docx_result['paragraphs'])}")
    
    # Example 3: Chunk text
    print("\n=== Example 3: Chunk Text ===")
    sample_text = pdf_result['text']
    
    # Chunk by tokens
    token_chunks = chunk_text(sample_text, chunk_size=100, chunk_overlap=20, chunk_method="token")
    print(f"Token Chunks: {len(token_chunks)}")
    print(f"First Token Chunk: {token_chunks[0][:100]}...")
    
    # Chunk by characters
    char_chunks = chunk_text(sample_text, chunk_size=500, chunk_overlap=50, chunk_method="character")
    print(f"Character Chunks: {len(char_chunks)}")
    print(f"First Character Chunk: {char_chunks[0][:100]}...")
    
    # Chunk by sentences
    sentence_chunks = chunk_text(sample_text, chunk_size=500, chunk_overlap=50, chunk_method="sentence")
    print(f"Sentence Chunks: {len(sentence_chunks)}")
    print(f"First Sentence Chunk: {sentence_chunks[0][:100]}...")


if __name__ == "__main__":
    asyncio.run(main())
