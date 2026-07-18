"""
Tests for the unified extraction service.
"""

import pytest
from app.services.unified_extraction import extract_text


def test_unified_extraction_import():
    """Test that the unified extraction function can be imported."""
    assert callable(extract_text)


def test_unified_extraction_with_nonexistent_file():
    """Test extraction with a non-existent file."""
    result = extract_text("non_existent_file.pdf")
    assert result == ""  # Should return empty string on error


def test_unified_extraction_with_empty_path():
    """Test extraction with empty file path."""
    result = extract_text("")
    assert result == ""  # Should return empty string on error


if __name__ == "__main__":
    test_unified_extraction_import()
    test_unified_extraction_with_nonexistent_file()
    test_unified_extraction_with_empty_path()
    print("All unified extraction tests passed!")