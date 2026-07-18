import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.services.reference_ranges import normalize_test_name

logger = logging.getLogger(__name__)

# Cache knowledge base JSON
_kb_cache: Optional[Dict[str, Any]] = None


def _load_knowledge_base() -> Dict[str, Any]:
    global _kb_cache
    if _kb_cache is not None:
        return _kb_cache

    try:
        json_path = Path(__file__).resolve().parent / "data" / "knowledge_base.json"
        if not json_path.exists():
            # Try workspace absolute path
            json_path = Path("/home/nulltrace/Desktop/MEDCLARIFY AI (Backend)/backend/app/services/data/knowledge_base.json")
        
        with open(json_path, "r", encoding="utf-8") as f:
            _kb_cache = json.load(f)
            logger.info("Successfully loaded medical knowledge base.")
            return _kb_cache
    except Exception as e:
        logger.error(f"Failed to load knowledge base JSON: {str(e)}")
        return {}


def interpret(test_name: str, status: str, value: float, unit: Optional[str] = None,
              ref_range: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Interpret a test status using the medical knowledge base.

    Args:
        test_name: Name of the test
        status: Evaluated status (LOW/NORMAL/BORDERLINE/HIGH/CRITICAL)
        value: Float result value
        unit: Optional unit string
        ref_range: Optional reference range dict with 'low' and 'high' keys

    Returns:
        dict containing:
            - 'test_name': str
            - 'finding': str (lowercase finding representing the status, e.g. 'low')
            - 'explanation': str (hedge-worded medical details)
            - 'evidence': list of strings detailing the values
            - 'recommendations': list of medical recommendations
    """
    db = _load_knowledge_base()
    norm_name = normalize_test_name(test_name)
    
    # Try status mapping (status is uppercase from reference ranges evaluate())
    status_upper = (status or "NORMAL").upper()
    finding_lower = status_upper.lower()

    # Find the knowledge base entry for this test name
    kb_entry = None
    if norm_name in db:
        kb_entry = db[norm_name]
    else:
        # Try substring lookup
        for k in db:
            if k in norm_name or norm_name in k:
                kb_entry = db[k]
                break

    # Map deficient to low, and insufficient to borderline for default lookups
    mapped_status_upper = status_upper
    if status_upper == "DEFICIENT":
        mapped_status_upper = "LOW"
    elif status_upper == "INSUFFICIENT":
        mapped_status_upper = "BORDERLINE"

    # If test is not in kb, fall back to default
    status_entry = None
    if kb_entry and status_upper in kb_entry:
        status_entry = kb_entry[status_upper]
    elif kb_entry and mapped_status_upper in kb_entry:
        status_entry = kb_entry[mapped_status_upper]
    elif status_upper in db.get("default", {}):
        status_entry = db.get("default", {})[status_upper]
    else:
        status_entry = db.get("default", {}).get(mapped_status_upper)

    # Format the evidence string
    evidence_str = ""
    unit_str = f" {unit}" if unit else ""
    
    # Build range description
    range_desc = "unknown"
    if ref_range:
        low = ref_range.get("low")
        high = ref_range.get("high")
        if low is not None and high is not None:
            range_desc = f"{low}-{high}"
        elif low is not None:
            range_desc = f">{low}"
        elif high is not None:
            range_desc = f"<{high}"

    evidence_str = f"{test_name} {value}{unit_str} vs reference {range_desc}"

    if status_entry:
        explanation = f"level {finding_lower} {status_entry.get('explanation')}"
        recommendations = status_entry.get("recommendations", [])
    else:
        explanation = f"level {finding_lower} than standard reference range"
        recommendations = ["Consult a healthcare provider to review this result."]

    # Capitalize the starting letter of explanation for good styling
    # e.g., "Hemoglobin level low may indicate..."
    explanation = f"{test_name} {explanation}"

    return {
        "test_name": test_name,
        "finding": finding_lower,
        "explanation": explanation,
        "evidence": [evidence_str],
        "recommendations": recommendations
    }
