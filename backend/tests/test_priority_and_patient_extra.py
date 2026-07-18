"""
Tests for priority range matching, extra patient details, and dynamic status evaluations.
"""

from app.services.parser.patient_parser import parse_patient_info
from app.services.parser.lab_parser import parse_lab_tests
from app.services.reference_ranges import evaluate

def test_patient_extra_fields():
    sample_text = """
    Patient Name: John Doe
    Age: 35 Years
    Gender: Male
    Patient ID: PT-998877
    Sample Type: Serum
    Collection Date: 12-Jan-2023
    Approval Date: 13-Jan-2023
    Hospital: City General Hospital
    Doctor: Dr. Sarah Connor MD
    Laboratory: Central Diagnostic Lab
    Registration Number: REG-112233
    """
    res = parse_patient_info(sample_text)
    assert res["name"] == "John Doe"
    assert res["age"] == "35"
    assert res["gender"] == "Male"
    assert res["patient_id"] == "PT-998877"
    assert res["sample_type"] == "Serum"
    assert res["collection_date"] == "12-Jan-2023"
    assert res["approval_date"] == "13-Jan-2023"
    assert res["hospital"] == "City General Hospital"
    assert res["doctor"] == "Dr. Sarah Connor MD"
    assert res["doctor_name"] == "Dr. Sarah Connor MD"
    assert res["laboratory"] == "Central Diagnostic Lab"
    assert res["lab_name"] == "Central Diagnostic Lab"
    assert res["registration_number"] == "REG-112233"

def test_priority_range_matching_and_status():
    # Priority 1: Report reference range (min/max)
    # 150000 | Reference: 150000-410000 -> NORMAL
    res1 = evaluate(
        test_name="Platelet Count",
        value=150000.0,
        unit="x10^3/µL",
        report_ref_range={"min": 150000.0, "max": 410000.0},
        source_text="Platelet Count 150000 x10^3/µL (150000-410000)"
    )
    assert res1["status"] == "NORMAL"
    assert res1["severity"] == "none"

    # CHOL/HDL Ratio | 3.1 | Reference: Up to 5 -> NORMAL, NOT LOW
    res2 = evaluate(
        test_name="CHOL/HDL Ratio",
        value=3.1,
        unit=None,
        report_ref_range={"min": None, "max": 5.0},
        source_text="CHOL/HDL Ratio 3.1 Up to 5"
    )
    assert res2["status"] == "NORMAL"
    assert res2["severity"] == "none"

    # Vitamin D | 8.98 | Reference: Deficiency <10 -> DEFICIENT
    res3 = evaluate(
        test_name="Vitamin D",
        value=8.98,
        unit="ng/mL",
        report_ref_range={"min": None, "max": 10.0},
        source_text="Vitamin D 8.98 Deficiency <10"
    )
    assert res3["status"] == "DEFICIENT"
    assert res3["severity"] == "moderate"

    # Priority 3: Fall back to internal knowledge when report range is missing
    res4 = evaluate(
        test_name="Hemoglobin",
        value=11.0,
        gender="Male"
    )
    # Male normal low is 13.5, so 11.0 is LOW
    assert res4["status"] == "LOW"

def test_unit_method_separation():
    # Test that UV is parsed as method and not unit
    results = parse_lab_tests("ALT (SGPT) 35 U/L UV with P5P IFCC")
    assert len(results) == 1
    test = results[0]
    assert test["test_name"] == "ALT (SGPT)"
    assert test["value"] == 35.0
    assert test["unit"] == "U/L"
    assert "UV" in test["method"]
    assert "P5P" in test["method"]
