"""
Unified text extraction pipeline for medical reports.
Handles both digital PDFs (using PyPDF) and scanned documents/images (using OCR).
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List

from pypdf import PdfReader
import pytesseract
from pdf2image import convert_from_path

from app.services.ocr_service import extract_text_from_image, extract_text_from_scanned_pdf
from app.utils.file_utils import is_pdf_file, is_image_file

logger = logging.getLogger(__name__)


def extract_text(file_path: str, metadata: Optional[dict] = None) -> str:
    """
    Extract text from a file using the appropriate method based on file type.

    For PDF files:
    Use hybrid per-page extraction. For each page, if it has digital text,
    use it. Otherwise, render and OCR only that page.

    For image files:
    Use OCR to extract text.

    Args:
        file_path: Path to the file to extract text from
        metadata: Optional dictionary to record extraction metadata (in-place)

    Returns:
        Extracted text as string (empty string if extraction fails)
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        logger.error(f"File not found: {file_path}")
        if metadata is not None:
            metadata["extraction_method"] = "unknown"
            metadata["ocr_pages"] = []
        return ""

    try:
        if is_pdf_file(file_path):
            logger.info(f"Extracting text from PDF: {file_path}")
            return _extract_text_from_pdf(file_path, metadata)
        elif is_image_file(file_path):
            logger.info(f"Extracting text from image: {file_path}")
            if metadata is not None:
                metadata["extraction_method"] = "ocr"
                metadata["ocr_pages"] = [1]
            return extract_text_from_image(file_path)
        else:
            logger.warning(f"Unsupported file type for text extraction: {file_path}")
            if metadata is not None:
                metadata["extraction_method"] = "unknown"
                metadata["ocr_pages"] = []
            return ""

    except Exception as e:
        logger.error(f"Unexpected error during text extraction for {file_path}: {str(e)}")
        if metadata is not None:
            metadata["extraction_method"] = "unknown"
            metadata["ocr_pages"] = []
        return ""


def _extract_text_from_pdf(file_path: str, metadata: Optional[dict] = None) -> str:
    """
    Extract text from a PDF file page-by-page. For each page, tries digital extraction.
    If digital text is missing, renders and OCRs that specific page.

    Args:
        file_path: Path to the PDF file
        metadata: Optional dictionary to record extraction metadata (in-place)

    Returns:
        Extracted text as string
    """
    logger.info(f"Attempting per-page hybrid extraction for PDF: {file_path}")
    try:
        reader = PdfReader(file_path)
        ocr_pages = []
        total_pages = len(reader.pages)
        pages_text = []

        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            page_text = page.extract_text()
            
            # Check if page has sufficient digital text
            if page_text and len(page_text.strip()) > 10:
                logger.info(f"Page {page_num}/{total_pages}: Using digital text extraction")
                pages_text.append(page_text)
            else:
                logger.info(f"Page {page_num}/{total_pages}: Digital text empty/insufficient, using OCR")
                try:
                    # Convert only this page to image and OCR it
                    images = convert_from_path(file_path, first_page=page_num, last_page=page_num)
                    if images:
                        ocr_text = pytesseract.image_to_string(images[0])
                        pages_text.append(ocr_text)
                        ocr_pages.append(page_num)
                        images[0].close()
                    else:
                        logger.warning(f"Failed to render image for page {page_num}")
                        pages_text.append("")
                except Exception as ocr_err:
                    logger.error(f"OCR failed for page {page_num}: {str(ocr_err)}")
                    pages_text.append("")

        # Determine extraction method
        if len(ocr_pages) == 0:
            extraction_method = "pdf_text"
        elif len(ocr_pages) == total_pages:
            extraction_method = "ocr"
        else:
            extraction_method = "hybrid"

        if metadata is not None:
            metadata["extraction_method"] = extraction_method
            metadata["ocr_pages"] = ocr_pages

        return "\n".join(pages_text)

    except Exception as e:
        logger.error(f"Error during hybrid PDF text extraction: {str(e)}")
        # Fallback to scanned PDF OCR
        try:
            if metadata is not None:
                metadata["extraction_method"] = "ocr"
                metadata["ocr_pages"] = []
            return extract_text_from_scanned_pdf(file_path)
        except Exception as ocr_fallback_err:
            logger.error(f"Fallback OCR also failed: {str(ocr_fallback_err)}")
            return ""