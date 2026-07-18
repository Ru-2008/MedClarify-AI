"""
Utility functions for file type detection and validation.
"""

from pathlib import Path
from pypdf import PdfReader
from pypdf.errors import PdfReadError


def is_pdf_file(file_path: str) -> bool:
    """
    Check if a file is a PDF based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        True if file is a PDF, False otherwise
    """
    return Path(file_path).suffix.lower() == '.pdf'


def is_image_file(file_path: str) -> bool:
    """
    Check if a file is an image based on its extension.

    Args:
        file_path: Path to the file

    Returns:
        True if file is an image (PNG, JPG, JPEG), False otherwise
    """
    extension = Path(file_path).suffix.lower()
    return extension in ['.png', '.jpg', '.jpeg']


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension in lowercase.

    Args:
        file_path: Path to the file

    Returns:
        File extension (including the dot) in lowercase
    """
    return Path(file_path).suffix.lower()


def get_page_count(file_path: str) -> int:
    """
    Get the number of pages in a PDF file.
    For image files, returns 1 (treating image as a single page).
    For unsupported or unreadable files, returns 0.

    Args:
        file_path: Path to the file

    Returns:
        Number of pages (int)
    """
    try:
        if is_pdf_file(file_path):
            reader = PdfReader(file_path)
            if reader.is_encrypted:
                # Encrypted PDFs cannot be read for page count
                return 0
            return len(reader.pages)
        elif is_image_file(file_path):
            return 1
        else:
            return 0
    except PdfReadError:
        # PDF is corrupted or unreadable
        return 0
    except Exception:
        # Any other error
        return 0