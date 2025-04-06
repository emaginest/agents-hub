"""
PDF processing utilities for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union, BinaryIO
import io
import PyPDF2
import pdfplumber
import logging

# Initialize logger
logger = logging.getLogger(__name__)


def extract_text_from_pdf(
    file_path: Optional[str] = None,
    file_content: Optional[bytes] = None,
    use_pdfplumber: bool = True,
    extract_metadata: bool = True,
) -> Dict[str, Any]:
    """
    Extract text and metadata from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        file_content: Binary content of the PDF file
        use_pdfplumber: Whether to use pdfplumber (better quality but slower)
        extract_metadata: Whether to extract metadata
        
    Returns:
        Dictionary containing text and metadata
    """
    if not file_path and not file_content:
        raise ValueError("Either file_path or file_content must be provided")
    
    result = {
        "text": "",
        "metadata": {},
        "pages": [],
    }
    
    try:
        # Open the PDF file
        if file_path:
            pdf_file = open(file_path, "rb")
        else:
            pdf_file = io.BytesIO(file_content)
        
        # Extract text using PyPDF2 or pdfplumber
        if use_pdfplumber:
            result = _extract_with_pdfplumber(pdf_file, extract_metadata)
        else:
            result = _extract_with_pypdf2(pdf_file, extract_metadata)
        
        # Close the file if it was opened from a path
        if file_path:
            pdf_file.close()
        
        return result
    
    except Exception as e:
        logger.exception(f"Error extracting text from PDF: {e}")
        return {
            "text": "",
            "metadata": {},
            "pages": [],
            "error": str(e),
        }


def _extract_with_pypdf2(file: BinaryIO, extract_metadata: bool) -> Dict[str, Any]:
    """
    Extract text and metadata from a PDF file using PyPDF2.
    
    Args:
        file: PDF file object
        extract_metadata: Whether to extract metadata
        
    Returns:
        Dictionary containing text and metadata
    """
    result = {
        "text": "",
        "metadata": {},
        "pages": [],
    }
    
    # Create a PDF reader object
    pdf_reader = PyPDF2.PdfReader(file)
    
    # Extract metadata if requested
    if extract_metadata:
        if pdf_reader.metadata:
            result["metadata"] = {
                "title": pdf_reader.metadata.title or "",
                "author": pdf_reader.metadata.author or "",
                "subject": pdf_reader.metadata.subject or "",
                "creator": pdf_reader.metadata.creator or "",
                "producer": pdf_reader.metadata.producer or "",
                "page_count": len(pdf_reader.pages),
            }
    
    # Extract text from each page
    all_text = []
    for i, page in enumerate(pdf_reader.pages):
        page_text = page.extract_text() or ""
        all_text.append(page_text)
        result["pages"].append({
            "page_number": i + 1,
            "text": page_text,
        })
    
    # Combine all text
    result["text"] = "\n\n".join(all_text)
    
    return result


def _extract_with_pdfplumber(file: BinaryIO, extract_metadata: bool) -> Dict[str, Any]:
    """
    Extract text and metadata from a PDF file using pdfplumber.
    
    Args:
        file: PDF file object
        extract_metadata: Whether to extract metadata
        
    Returns:
        Dictionary containing text and metadata
    """
    result = {
        "text": "",
        "metadata": {},
        "pages": [],
    }
    
    # Create a PDF plumber object
    with pdfplumber.open(file) as pdf:
        # Extract metadata if requested
        if extract_metadata:
            if pdf.metadata:
                result["metadata"] = {
                    "title": pdf.metadata.get("Title", ""),
                    "author": pdf.metadata.get("Author", ""),
                    "subject": pdf.metadata.get("Subject", ""),
                    "creator": pdf.metadata.get("Creator", ""),
                    "producer": pdf.metadata.get("Producer", ""),
                    "page_count": len(pdf.pages),
                }
        
        # Extract text from each page
        all_text = []
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ""
            all_text.append(page_text)
            result["pages"].append({
                "page_number": i + 1,
                "text": page_text,
            })
        
        # Combine all text
        result["text"] = "\n\n".join(all_text)
    
    return result
