"""
Test for the recursive character text splitter.
This test directly imports and tests the _chunk_by_recursive_characters function.
"""

import os
import sys
import unittest

# Add the parent directory to the path so we can import the agents_hub package
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Direct import of the recursive chunker function
from agents_hub.utils.document.chunking import _chunk_by_recursive_characters


class TestRecursiveCharacterTextSplitter(unittest.TestCase):
    """Test cases for the recursive character text splitter."""

    def test_basic_functionality(self):
        """Test basic functionality with default separators."""
        text = "This is a test document. It has multiple sentences. Let's see how it splits."
        chunks = _chunk_by_recursive_characters(text, chunk_size=30, chunk_overlap=5)
        
        # Should split into multiple chunks
        self.assertTrue(len(chunks) > 1)
        # Each chunk should be <= chunk_size
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 30)
    
    def test_custom_separators(self):
        """Test with custom separators."""
        text = "Section 1\n\nParagraph 1\nParagraph 2\n\nSection 2\n\nParagraph 3"
        custom_separators = ["\n\n", "\n"]
        chunks = _chunk_by_recursive_characters(
            text, chunk_size=20, chunk_overlap=5, separators=custom_separators
        )
        
        # Should split on section boundaries first
        self.assertEqual(chunks[0], "Section 1")
        # Should contain all content
        full_text = "\n\n".join(chunks)
        self.assertTrue(all(p in full_text for p in ["Paragraph 1", "Paragraph 2", "Paragraph 3"]))
    
    def test_empty_text(self):
        """Test with empty text."""
        chunks = _chunk_by_recursive_characters("", chunk_size=100, chunk_overlap=10)
        self.assertEqual(chunks, [""])
    
    def test_small_text(self):
        """Test with text smaller than chunk size."""
        text = "Small text"
        chunks = _chunk_by_recursive_characters(text, chunk_size=100, chunk_overlap=10)
        self.assertEqual(chunks, [text])
    
    def test_no_good_separator(self):
        """Test with text that doesn't contain any of the separators."""
        text = "ThisIsALongStringWithNoSpacesOrSeparators"
        chunks = _chunk_by_recursive_characters(
            text, chunk_size=10, chunk_overlap=2, separators=["\n", " "]
        )
        # Should fall back to character chunking
        self.assertTrue(len(chunks) > 1)
        self.assertLessEqual(len(chunks[0]), 10)


if __name__ == "__main__":
    unittest.main()
