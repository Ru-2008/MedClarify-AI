import logging
from pypdf import PdfReader
from pypdf.errors import PdfReadError

logger = logging.getLogger(__name__)

def extract_pdf_text(file_path: str, limit: int = None) -> str:
    """
    Extract text from a digital PDF using PyPDF.

    Args:
        file_path: Path to the PDF file
        limit: Maximum number of characters to extract (optional)

    Returns:
        Extracted text as string, or empty string if extraction fails
    """
    try:
        logger.info(f"Starting PDF text extraction for: {file_path}")
        reader = PdfReader(file_path)

        # Check if PDF is encrypted
        if reader.is_encrypted:
            logger.warning(f"PDF is encrypted: {file_path}")
            return ""

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                if limit is not None and len(text) >= limit:
                    break

        if limit is not None:
            result = text[:limit]
        else:
            result = text

        logger.info(f"PDF text extraction completed. Extracted {len(result)} characters.")
        return result

    except PdfReadError as e:
        logger.warning(f"PDF read error (possibly corrupted): {file_path} - {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error during PDF text extraction: {file_path} - {str(e)}")
        return ""