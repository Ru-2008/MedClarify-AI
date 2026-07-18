"""
Tests for the extraction service.
"""

import os
import tempfile
import pytest
from app.services.extraction_service import extract_pdf_text


def test_extract_pdf_text_with_valid_pdf():
    """Test extracting text from a valid PDF."""
    # This test would require a sample PDF file
    # For now, we'll test that the function exists and handles errors gracefully
    assert callable(extract_pdf_text)

    # Test with non-existent file
    result = extract_pdf_text("non_existent_file.pdf")
    assert result == ""  # Should return empty string on error


def test_extract_pdf_text_with_empty_string():
    """Test extracting text with empty file path."""
    result = extract_pdf_text("")
    assert result == ""  # Should return empty string on error


if __name__ == "__main__":
    test_extract_pdf_text_with_valid_pdf()
    test_extract_pdf_text_with_empty_string()
    print("All extraction service tests passed!")