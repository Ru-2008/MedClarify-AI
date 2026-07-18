import json
import logging
import re
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Cache reference ranges JSON
_ranges_cache: Optional[Dict[str, Any]] = None

ALIASES = {
    "hgb": "hemoglobin",
    "hb": "hemoglobin",
    "hct": "hematocrit",
    "plt": "platelet",
    "platelets": "platelet",
    "white blood cell": "wbc",
    "red blood cell": "rbc",
    "total cholesterol": "cholesterol",
    "triglyceride": "triglycerides",
    "potassium level": "potassium",
    "sodium level": "sodium",
    "chloride level": "chloride",
}


def _load_reference_ranges() -> Dict[str, Any]:
    global _ranges_cache
    if _ranges_cache is not None:
        return _ranges_cache

    try:
        json_path = Path(__file__).resolve().parent / "data" / "reference_ranges.json"
        if not json_path.exists():
            # Try workspace absolute path
            json_path = Path("/home/nulltrace/Desktop/MEDCLARIFY AI (Backend)/backend/app/services/data/reference_ranges.json")
        
        with open(json_path, "r", encoding="utf-8") as f:
            _ranges_cache = json.load(f)
            logger.info("Successfully loaded reference ranges database.")
            return _ranges_cache
    except Exception as e:
        logger.error(f"Failed to load reference ranges JSON: {str(e)}")
        return {}


def normalize_test_name(name: str) -> str:
    """Normalize and resolve aliases for a test name."""
    if not name:
        return ""
    name_clean = name.lower().strip()
    name_clean = " ".join(name_clean.split())
    
    # Remove common suffixes
    for suffix in [" count", " level", "s", " (hb)"]:
        if name_clean.endswith(suffix):
            name_clean = name_clean[:-len(suffix)].strip()
            
    # Resolve aliases
    if name_clean in ALIASES:
        return ALIASES[name_clean]
        
    return name_clean


def evaluate(test_name: str, value: float, unit: Optional[str] = None,
             age: Optional[int] = None, gender: Optional[str] = None,
             report_ref_range: Optional[Dict[str, Any]] = None,
             source_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Evaluate a lab test value against standard reference ranges.

    Args:
        test_name: The name of the test
        value: Float result value
        unit: Optional unit string
        age: Optional patient age (int)
        gender: Optional patient gender (str)
        report_ref_range: Optional reference range dict with 'min' and/or 'max' keys
        source_text: Optional raw text line from report for interpretation clues

    Returns:
        dict containing:
            - 'status': LOW/NORMAL/BORDERLINE/HIGH/CRITICAL/UNKNOWN/DEFICIENT/INSUFFICIENT
            - 'severity': none/mild/moderate/severe
            - 'reference_range': {'low': float or None, 'high': float or None}
    """
    # Priority 1 & 2: Report reference range / report interpretation
    report_min = report_ref_range.get("min") if report_ref_range else None
    report_max = report_ref_range.get("max") if report_ref_range else None

    if (report_min is not None) or (report_max is not None):
        status = "NORMAL"
        severity = "none"
        source_lower = (source_text or "").lower()

        # Deficiency check: e.g. Deficiency <10
        deficiency_match = re.search(r'(?:deficiency|deficient)\s*(?:<|<=|:|\b)?\s*(\d+\.?\d*)', source_lower)
        if deficiency_match:
            def_boundary = float(deficiency_match.group(1))
            if value < def_boundary:
                return {
                    "status": "DEFICIENT",
                    "severity": "moderate",
                    "reference_range": {"low": report_min, "high": report_max}
                }

        # Insufficiency check: e.g. Insufficiency 10-30 or Insufficiency <30
        insufficiency_range_match = re.search(r'(?:insufficiency|insufficient)\s*(?:\b)?\s*(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', source_lower)
        if insufficiency_range_match:
            ins_low = float(insufficiency_range_match.group(1))
            ins_high = float(insufficiency_range_match.group(2))
            if ins_low <= value <= ins_high:
                return {
                    "status": "INSUFFICIENT",
                    "severity": "moderate",
                    "reference_range": {"low": report_min, "high": report_max}
                }
        else:
            insufficiency_val_match = re.search(r'(?:insufficiency|insufficient)\s*(?:<|<=|:|\b)?\s*(\d+\.?\d*)', source_lower)
            if insufficiency_val_match:
                ins_boundary = float(insufficiency_val_match.group(1))
                if value < ins_boundary:
                    return {
                        "status": "INSUFFICIENT",
                        "severity": "moderate",
                        "reference_range": {"low": report_min, "high": report_max}
                    }

        # Standard comparisons (result against reference range)
        if report_min is not None and report_max is not None:
            if value < report_min:
                status = "LOW"
                severity = "moderate"
            elif value > report_max:
                status = "HIGH"
                severity = "moderate"
        elif report_min is not None:
            if value < report_min:
                status = "LOW"
                severity = "moderate"
        elif report_max is not None:
            if value > report_max:
                status = "HIGH"
                severity = "moderate"

        return {
            "status": status,
            "severity": severity,
            "reference_range": {
                "low": report_min,
                "high": report_max
            }
        }

    # Priority 3: Fall back to internal knowledge base
    db = _load_reference_ranges()
    norm_name = normalize_test_name(test_name)
    
    # Try exact match or substring match
    config = None
    if norm_name in db:
        config = db[norm_name]
    else:
        # Check if any database key is a substring of our normalized test name
        for k in db:
            if k in norm_name or norm_name in k:
                config = db[k]
                break

    if not config:
        logger.debug(f"Test name '{test_name}' (normalized: '{norm_name}') not found in reference range database.")
        return {
            "status": "UNKNOWN",
            "severity": "none",
            "reference_range": None
        }

    # Resolve gender specific ranges
    ranges = config.get("ranges", {})
    range_config = None
    
    if config.get("gender_specific", False):
        g = (gender or "").lower().strip()
        if "female" in g or g == "f":
            range_config = ranges.get("female")
        elif "male" in g or g == "m":
            range_config = ranges.get("male")
        else:
            # Default fallback if gender is missing or unspecified
            range_config = ranges.get("female") or ranges.get("male")
    else:
        range_config = ranges

    if not range_config:
        return {
            "status": "UNKNOWN",
            "severity": "none",
            "reference_range": None
        }

    status = "NORMAL"
    severity = "none"
    
    # Extract normal range bounds for reference range output
    normal_range = range_config.get("normal", {})
    low_val = normal_range.get("low")
    high_val = normal_range.get("high")

    # 1. Check critical range first
    critical_range = range_config.get("critical", {})
    if "low" in critical_range and value <= critical_range["low"]:
        status = "CRITICAL"
        severity = "severe"
    elif "high" in critical_range and value >= critical_range["high"]:
        status = "CRITICAL"
        severity = "severe"
    # 2. Check other tiers
    else:
        # Borderline and high specific ranges (like cholesterol, HbA1c)
        if "borderline" in range_config or "high" in range_config:
            borderline_range = range_config.get("borderline", {})
            high_limit_range = range_config.get("high", {})
            
            if "low" in high_limit_range and value >= high_limit_range["low"]:
                status = "HIGH"
                severity = "moderate"
            elif "low" in borderline_range and "high" in borderline_range:
                if borderline_range["low"] <= value <= borderline_range["high"]:
                    status = "BORDERLINE"
                    severity = "mild"
            elif "high" in normal_range and value > normal_range["high"]:
                status = "HIGH"
                severity = "moderate"
            else:
                status = "NORMAL"
                severity = "none"
        # Standard low/high normal ranges
        else:
            if "low" in normal_range and value < normal_range["low"]:
                status = "LOW"
                severity = "moderate"
            elif "high" in normal_range and value > normal_range["high"]:
                status = "HIGH"
                severity = "moderate"
            else:
                status = "NORMAL"
                severity = "none"

    return {
        "status": status,
        "severity": severity,
        "reference_range": {
            "low": low_val,
            "high": high_val
        }
    }
