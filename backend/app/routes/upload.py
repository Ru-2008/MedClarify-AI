import logging
import shutil
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

from app.services.unified_extraction import extract_text
from app.utils.file_utils import get_page_count
from app.services.parser.patient_parser import parse_patient_info
from app.services.parser.lab_parser import parse_lab_tests
from app.services.parser import text_cleaner
from app.services.reference_ranges import evaluate as evaluate_range
from app.services.knowledge_engine import interpret as interpret_test
from app.services.summary_engine import generate_summary

router = APIRouter()

# Allowed file extensions and their MIME types
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}

def get_upload_dir() -> Path:
    """
    Returns the upload directory path, creating it if it doesn't exist.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    upload_dir = base_dir / "uploaded_reports"
    upload_dir.mkdir(exist_ok=True)
    return upload_dir

def is_allowed_file(filename: str, content_type: str) -> bool:
    """
    Check if the file extension and MIME type are allowed.
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    if content_type not in ALLOWED_MIME_TYPES:
        return False
    return True

@router.post("/upload", tags=["upload"])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a medical report (PDF, PNG, JPG, JPEG).
    """
    logger = logging.getLogger(__name__)

    # Check if file is empty
    if file.size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file is not allowed",
        )

    # Validate file type
    if not is_allowed_file(file.filename, file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, PNG, JPG, JPEG are allowed.",
        )

    # Generate unique filename while preserving extension
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid4()}{file_ext}"
    upload_dir = get_upload_dir()
    file_path = upload_dir / unique_filename

    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Upload started: {file.filename} -> {unique_filename}")
    except Exception as e:
        logger.error(f"Could not save file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}",
        )
    finally:
        file.file.close()

    # Get page count (for PDF) or set to 1 for images
    page_count = get_page_count(str(file_path))

    # Initialize extraction metadata dictionary
    ocr_metadata = {
        "extraction_method": "pdf_text",
        "ocr_pages": [],
        "processing_time_ms": 0
    }
    start_time = time.time()

    # Extract text using unified extraction pipeline
    logger.info(f"Starting text extraction for: {unique_filename}")
    try:
        extracted_text = extract_text(str(file_path), metadata=ocr_metadata)
        logger.info(f"Text extraction completed. Extracted {len(extracted_text)} characters.")
    except Exception as e:
        logger.error(f"Text extraction failed for {unique_filename}: {str(e)}")
        extracted_text = ""

    # Clean text using Phase A new functions
    if extracted_text:
        try:
            cleaned = text_cleaner.remove_duplicate_lines(extracted_text)
            cleaned = text_cleaner.merge_wrapped_lines(cleaned)
            cleaned = text_cleaner.fix_common_ocr_mistakes(cleaned)
            extracted_text = text_cleaner.clean_text(cleaned)
        except Exception as e:
            logger.error(f"Error cleaning extracted text: {str(e)}")

    # Parse medical report
    logger.info(f"Starting medical report parsing for: {unique_filename}")
    try:
        patient_info = parse_patient_info(extracted_text)
        lab_tests = parse_lab_tests(extracted_text)
        
        parsed_data = {
            "patient": patient_info,
            "laboratory_tests": lab_tests
        }
        logger.info(f"Medical report parsing completed for: {unique_filename}")

        # Enhancement Pipeline (wrapped in try/except for backward compatibility)
        try:
            ocr_metadata["processing_time_ms"] = int((time.time() - start_time) * 1000)

            # Extract patient features
            age_val = None
            if patient_info.get("age"):
                try:
                    age_clean = "".join(c for c in str(patient_info["age"]) if c.isdigit())
                    if age_clean:
                        age_val = int(age_clean)
                except Exception:
                    pass
            gender_val = patient_info.get("gender")

            enriched_tests = []
            abnormal_tests = []
            interpretations = []
            warnings = []

            total_confidence = 0.0
            test_count = len(lab_tests)

            for test in lab_tests:
                val = test.get("value")
                test_name = test.get("test_name")
                unit = test.get("unit")
                
                # Get parser confidence (defaulting to 1.0)
                test_confidence = test.get("confidence", 1.0)
                total_confidence += test_confidence

                if test_confidence < 0.70:
                    warnings.append(f"Low extraction confidence for test: {test_name} ({int(test_confidence * 100)}%)")

                # Reference range check
                if val is not None:
                    eval_res = evaluate_range(
                        test_name,
                        val,
                        unit,
                        age=age_val,
                        gender=gender_val,
                        report_ref_range=test.get("reference_range"),
                        source_text=test.get("source_text")
                    )
                    status_upper = eval_res.get("status", "UNKNOWN")
                    severity = eval_res.get("severity", "none")
                    ref_range = eval_res.get("reference_range")
                else:
                    status_upper = "UNKNOWN"
                    severity = "none"
                    ref_range = None

                # Keep old min/max range keys, add new low/high keys
                original_ref_range = test.get("reference_range") or {}
                new_ref_range = {
                    "min": original_ref_range.get("min"),
                    "max": original_ref_range.get("max"),
                    "low": ref_range.get("low") if ref_range else None,
                    "high": ref_range.get("high") if ref_range else None
                }

                # Construct enhanced test object
                enriched_test = {
                    "test_name": test_name,
                    "value": val,
                    "unit": unit,
                    "reference_range": new_ref_range,
                    "status": status_upper,
                    "severity": severity,
                    "confidence": test_confidence,
                    "source_text": test.get("source_text", ""),
                    "extraction_strategy": test.get("extraction_strategy", "unknown")
                }
                enriched_tests.append(enriched_test)

                # Collect abnormal tests
                if status_upper not in ["NORMAL", "UNKNOWN"]:
                    abnormal_tests.append(enriched_test)
                    # Interpret finding via Knowledge Engine
                    interp = interpret_test(test_name, status_upper, val, unit, ref_range)
                    interpretations.append(interp)

            # Generate patient metadata warnings
            for key, display in [("name", "Name"), ("age", "Age"), ("gender", "Gender"), ("report_date", "Report Date")]:
                if not patient_info.get(key):
                    warnings.append(f"Patient {display} could not be extracted.")

            # Compute overall confidence
            global_confidence = 100
            if test_count > 0:
                global_confidence = int((total_confidence / test_count) * 100)
            elif not extracted_text:
                global_confidence = 0

            # Generate summary
            summary = generate_summary(enriched_tests, abnormal_tests, interpretations, global_confidence)

            # Inject into final parsed_data structure
            parsed_data["laboratory_tests"] = enriched_tests
            parsed_data["abnormal_tests"] = abnormal_tests
            parsed_data["interpretation"] = interpretations
            parsed_data["summary"] = summary
            parsed_data["confidence"] = global_confidence
            parsed_data["warnings"] = warnings
            parsed_data["processing_metadata"] = ocr_metadata

        except Exception as enhance_err:
            logger.error(f"Degrading gracefully due to enhancement pipeline failure: {str(enhance_err)}")
            # Degrade gracefully to current response shape
            parsed_data = {
                "patient": patient_info,
                "laboratory_tests": lab_tests
            }

    except Exception as e:
        logger.error(f"Medical report parsing failed for {unique_filename}: {str(e)}")
        parsed_data = {
            "patient": {"name": None, "age": None, "gender": None, "report_date": None},
            "laboratory_tests": []
        }

    # Prepare response data
    preview_text = extracted_text[:1000] if extracted_text else None
    character_count = len(extracted_text) if extracted_text else 0

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "filename": unique_filename,
            "original_name": file.filename,
            "preview_text": preview_text,
            "character_count": character_count,
            "pages": page_count,
            "parsed_data": parsed_data
        },
    )
