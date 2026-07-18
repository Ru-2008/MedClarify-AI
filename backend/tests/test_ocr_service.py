"""
Tests for the OCR service.
"""

from unittest.mock import MagicMock, patch
import pytest
from app.services.ocr_service import extract_text_from_image, extract_text_from_scanned_pdf


@patch("app.services.ocr_service.pytesseract.image_to_string")
@patch("app.services.ocr_service.Image.open")
def test_extract_text_from_image(mock_open, mock_image_to_string):
    """Test that image OCR extracts text using pytesseract."""
    mock_image_to_string.return_value = "Mocked Image OCR Text"
    
    result = extract_text_from_image("dummy_image.png")
    
    assert result == "Mocked Image OCR Text"
    mock_open.assert_called_once_with("dummy_image.png")
    mock_image_to_string.assert_called_once()


@patch("app.services.ocr_service.pytesseract.image_to_string")
@patch("app.services.ocr_service.convert_from_path")
def test_extract_text_from_scanned_pdf(mock_convert, mock_image_to_string):
    """Test that scanned PDF OCR extracts text using pdf2image and pytesseract."""
    mock_img1 = MagicMock()
    mock_img2 = MagicMock()
    mock_convert.return_value = [mock_img1, mock_img2]
    mock_image_to_string.side_effect = ["Page 1 Text", "Page 2 Text"]
    
    result = extract_text_from_scanned_pdf("dummy_scanned.pdf")
    
    assert result == "Page 1 Text\nPage 2 Text"
    mock_convert.assert_called_once_with("dummy_scanned.pdf")
    assert mock_image_to_string.call_count == 2