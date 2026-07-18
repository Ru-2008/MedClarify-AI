#!/usr/bin/env python3
"""
Test script to verify the parser fixes.
"""

import sys
import os

# Add the current directory to path so we can find app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.parser.patient_parser import parse_patient_info
from app.services.parser.lab_parser import parse_lab_tests

def test_patient_parser_improvements():
    """Test that the patient parser fixes work correctly."""
    print("=== Testing Patient Parser Improvements ===")

    # Test case from the original test file
    sample_text = """
    Client Name: Lyubochka Svetka
    Age: 41
    Gender: Female
    Patient ID: SA123456789
    Date of Report: 20-Feb-2023

    Sterling Accuris Diagnostics Limited
    Lab Report

    HEMATOLOGY
    Hemoglobin: 12.5 g/dL (11.5-15.5)
    RBC Count: 4.2 million/cmm (4.0-5.2)
    WBC Count: 6.8 x10^3/µL (4.0-10.0)
    Platelet Count: 220 x10^3/µL (150-400)

    BIOCHEMISTRY
    Glucose: 92 mg/dL (70-110)
    Urea: 18 mg/dL (15-45)
    Creatinine: 0.9 mg/dL (0.6-1.2)

    LIPID PROFILE
    Cholesterol: 180 mg/dL (<200)
    Triglycerides: 120 mg/dL (<150)
    """

    result = parse_patient_info(sample_text)

    print(f"Patient Name: {result['name']}")
    print(f"Age: {result['age']}")
    print(f"Gender: {result['gender']}")
    print(f"Report Date: {result['report_date']}")
    print(f"Lab Name: {result['lab_name']}")
    print(f"Doctor Name: {result['doctor_name']}")
    print(f"Patient ID: {result['patient_id']}")

    # Assertions for key fields
    assert result['name'] == 'Lyubochka Svetka', f"Expected 'Lyubochka Svetka', got '{result['name']}'"
    assert result['age'] == '41', f"Expected '41', got '{result['age']}'"
    assert result['gender'] == 'Female', f"Expected 'Female', got '{result['gender']}'"
    assert result['report_date'] == '20-Feb-2023', f"Expected '20-Feb-2023', got '{result['report_date']}'"
    assert result['patient_id'] == 'SA123456789', f"Expected patient ID, got '{result['patient_id']}'"
    assert result['lab_name'] == 'Sterling Accuris Diagnostics Limited', f"Expected lab name, got '{result['lab_name']}'"

    print("✓ Patient parser test passed!")
    return True

def test_lab_parser_improvements():
    """Test that the lab parser fixes work correctly."""
    print("\n=== Testing Lab Parser Improvements ===")

    # Test the specific issue mentioned: Hemoglobin g/dL 13.0 - 16.5 Colorimetric 14.5
    test_line = "Hemoglobin g/dL 13.0 - 16.5 Colorimetric 14.5"
    results = parse_lab_tests(test_line)

    print(f"Input: {test_line}")
    print(f"Results: {results}")

    assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    test = results[0]

    assert test['test_name'] == 'Hemoglobin', f"Expected 'Hemoglobin', got '{test['test_name']}'"
    assert test['value'] == 14.5, f"Expected value 14.5, got {test['value']}"
    assert test['unit'] == 'g/dL', f"Expected unit 'g/dL', got '{test['unit']}'"
    assert test['reference_range'] is not None, "Expected reference range"
    assert test['reference_range']['min'] == 13.0, f"Expected min 13.0, got {test['reference_range']['min']}"
    assert test['reference_range']['max'] == 16.5, f"Expected max 16.5, got {test['reference_range']['max']}"
    assert test['status'] == 'normal', f"Expected status 'normal', got '{test['status']}'"

    print("✓ Lab parser test for Hemoglobin passed!")

    # Test that false positives are rejected
    false_positives = [
        "13.0 16.5Colorimetric",
        "101Derived",
        "145Direct- ISE",
        "Bennett PH, Haffner",
        "Zelmanovitz T, Gross",
        "asthma in approximately",
        "screening test for diabetic nephropathy...",
        "reference text",
        "explanatory paragraphs",
        "methods",
        "literature citations",
        "Reference:",
        "Kidney Foundation",
        "Analysis Performed",
        "Generated",
        "Comments",
        "Inst."
    ]

    for fp in false_positives:
        results = parse_lab_tests(fp)
        assert len(results) == 0, f"False positive detected: '{fp}' produced {results}"
        print(f"✓ Correctly rejected false positive: '{fp}'")

    # Test normal lab results still work
    normal_tests = [
        ("Hemoglobin: 12.5 g/dL (11.5-15.5)", "Hemoglobin", 12.5, "g/dL", (11.5, 15.5)),
        ("Glucose 95 mg/dL (ref: 70-100)", "Glucose", 95, "mg/dL", (70, 100)),
        ("HbA1c 5.8%", "HbA1c", 5.8, "%", None),
        ("Cholesterol total: 200 mg/dL Desirable: <200", "Total Cholesterol", 200, "mg/dL", None),
    ]

    for test_line, expected_name, expected_value, expected_unit, expected_range in normal_tests:
        results = parse_lab_tests(test_line)
        assert len(results) >= 1, f"No results for '{test_line}'"
        test = results[0]
        assert test['test_name'] == expected_name, f"Expected '{expected_name}', got '{test['test_name']}' for '{test_line}'"
        assert test['value'] == expected_value, f"Expected value {expected_value}, got {test['value']} for '{test_line}'"
        if expected_unit:
            assert test['unit'] == expected_unit, f"Expected unit '{expected_unit}', got '{test['unit']}' for '{test_line}'"
        if expected_range:
            assert test['reference_range'] is not None, f"Expected range for '{test_line}'"
            assert test['reference_range']['min'] == expected_range[0], f"Expected min {expected_range[0]}, got {test['reference_range']['min']} for '{test_line}'"
            assert test['reference_range']['max'] == expected_range[1], f"Expected max {expected_range[1]}, got {test['reference_range']['max']} for '{test_line}'"
        print(f"✓ Normal test passed: '{test_line}'")

    print("✓ Lab parser test passed!")
    return True

def test_integration():
    """Test integration with sample text."""
    print("\n=== Testing Integration ===")

    sample_text = """
    Patient Name: John Doe
    Age: 45
    Gender: Male
    Patient ID: PT123456
    Date of Report: 15-Mar-2023

    City Medical Laboratory

    HEMATOLOGY
    Hemoglobin: 14.2 g/dL (13.0-16.5)
    WBC Count: 7.2 x10^3/µL (4.0-10.0)

    CHEMISTRY
    Glucose: 98 mg/dL (70-110)
    Creatinine: 1.1 mg/dL (0.6-1.2)

    Lipid Panel
    Cholesterol: 185 mg/dL (<200)
    HDL Cholesterol: 52 mg/dL (>40)
    Triglycerides: 165 mg/dL (<150)

    Some reference text that should not be mistaken for a test.
    Bennett PH, Haffner SM: Association between endogenous insulin resistance
    and vascular disease. J Lab Clin Med 123:456-467, 1994.
    """

    # Test patient parser
    patient_result = parse_patient_info(sample_text)
    assert patient_result['name'] == 'John Doe'
    assert patient_result['age'] == '45'
    assert patient_result['gender'] == 'Male'
    assert patient_result['patient_id'] == 'PT123456'
    assert 'City Medical Laboratory' in (patient_result['lab_name'] or '')

    # Test lab parser
    lab_results = parse_lab_tests(sample_text)

    # Should find the real tests but not the reference text
    test_names = [r['test_name'].lower() for r in lab_results]
    assert 'hemoglobin' in test_names
    assert 'wbc count' in test_names
    assert 'glucose' in test_names
    assert 'creatinine' in test_names
    assert 'total cholesterol' in test_names

    # Should NOT find false positives from the reference text
    false_positives = ['bennett', 'haffner', 'association', 'endogenous', 'insulin', 'resistance']
    for fp in false_positives:
        assert not any(fp in name.lower() for name in test_names), f"False positive found: {fp}"

    print(f"Found {len(lab_results)} lab tests: {test_names}")
    print("✓ Integration test passed!")
    return True

if __name__ == "__main__":
    try:
        test_patient_parser_improvements()
        test_lab_parser_improvements()
        test_integration()
        print("\n🎉 All tests passed! The parser fixes are working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)