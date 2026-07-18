"""
Tests for the reference ranges evaluation engine.
"""

from app.services.reference_ranges import evaluate


def test_evaluate_hemoglobin():
    """Test hemoglobin range evaluation across genders."""
    # Male: normal range (13.5 - 17.5)
    res_male_normal = evaluate("Hemoglobin", 15.0, gender="Male")
    assert res_male_normal["status"] == "NORMAL"
    assert res_male_normal["severity"] == "none"
    assert res_male_normal["reference_range"] == {"low": 13.5, "high": 17.5}

    res_male_low = evaluate("Hemoglobin", 10.0, gender="Male")
    assert res_male_low["status"] == "LOW"
    assert res_male_low["severity"] == "moderate"

    # Female: normal range (12.0 - 15.5)
    res_female_normal = evaluate("Hemoglobin", 14.0, gender="Female")
    assert res_female_normal["status"] == "NORMAL"
    assert res_female_normal["reference_range"] == {"low": 12.0, "high": 15.5}

    res_female_low = evaluate("Hemoglobin", 10.0, gender="Female")
    assert res_female_low["status"] == "LOW"


def test_evaluate_glucose():
    """Test glucose range evaluation (critical checks)."""
    # Normal fasting glucose (70 - 100)
    res_normal = evaluate("Glucose", 85.0)
    assert res_normal["status"] == "NORMAL"

    # High glucose
    res_high = evaluate("Glucose", 150.0)
    assert res_high["status"] == "HIGH"
    assert res_high["severity"] == "moderate"

    # Critical high glucose
    res_critical = evaluate("Glucose", 450.0)
    assert res_critical["status"] == "CRITICAL"
    assert res_critical["severity"] == "severe"


def test_evaluate_cholesterol_multitier():
    """Test multi-tier cholesterol evaluation (borderline cases)."""
    # Normal: < 200
    res_normal = evaluate("Cholesterol", 180.0)
    assert res_normal["status"] == "NORMAL"

    # Borderline: 200 - 239
    res_borderline = evaluate("Cholesterol", 220.0)
    assert res_borderline["status"] == "BORDERLINE"
    assert res_borderline["severity"] == "mild"

    # High: >= 240
    res_high = evaluate("Cholesterol", 250.0)
    assert res_high["status"] == "HIGH"
    assert res_high["severity"] == "moderate"


def test_unknown_test():
    """Test evaluation of unknown test names."""
    res = evaluate("Some Random Nonexistent Test Name", 99.9)
    assert res["status"] == "UNKNOWN"
    assert res["severity"] == "none"
    assert res["reference_range"] is None
