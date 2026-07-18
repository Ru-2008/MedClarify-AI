"""
Tests for the plain-English summary engine.
"""

from app.services.summary_engine import generate_summary, DISCLAIMER


def test_generate_summary_empty():
    """Test summary when no tests are extracted."""
    res = generate_summary(laboratory_tests=[], abnormal_tests=[], interpretations=[], global_confidence=100)
    assert "No laboratory tests were found" in res
    assert DISCLAIMER in res


def test_generate_summary_low_confidence():
    """Test summary when confidence is low."""
    res = generate_summary(
        laboratory_tests=[{"test_name": "Hemoglobin", "value": 14.0}],
        abnormal_tests=[],
        interpretations=[],
        global_confidence=45
    )
    assert "extraction confidence is low" in res
    assert DISCLAIMER in res


def test_generate_summary_all_normal():
    """Test summary when all tests are normal."""
    res = generate_summary(
        laboratory_tests=[{"test_name": "Hemoglobin", "value": 14.0}],
        abnormal_tests=[],
        interpretations=[],
        global_confidence=95
    )
    assert "within the normal reference ranges" in res
    assert DISCLAIMER in res


def test_generate_summary_abnormal():
    """Test summary with abnormal findings."""
    lab_tests = [{"test_name": "Hemoglobin", "value": 10.2}]
    abnormal_tests = [{"test_name": "Hemoglobin", "value": 10.2}]
    interpretations = [{
        "test_name": "Hemoglobin",
        "finding": "low",
        "explanation": "Hemoglobin level low may indicate iron deficiency, vitamin deficiency, or mild anemia",
        "evidence": ["Hemoglobin 10.2 g/dL vs reference 13.5-17.5"],
        "recommendations": ["Consult doctor"]
    }]
    
    res = generate_summary(
        laboratory_tests=lab_tests,
        abnormal_tests=abnormal_tests,
        interpretations=interpretations,
        global_confidence=95
    )
    
    assert "shows 1 abnormal test result" in res
    assert "Hemoglobin level low may indicate iron deficiency" in res
    assert DISCLAIMER in res
