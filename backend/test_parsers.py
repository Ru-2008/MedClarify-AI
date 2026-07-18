#!/usr/bin/env python3
"""
Simple test for the parsers - run from backend directory
"""

import sys
import os

# Add the current directory to path so we can find app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.parser.patient_parser import parse_patient_info
from app.services.parser.lab_parser import parse_lab_tests

# Sample text simulating a medical report
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

def test_patient_parser():
    print("=== Testing Patient Parser ===")
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
    print("✓ Patient parser test passed!")

def test_lab_parser():
    print("\n=== Testing Lab Parser ===")
    results = parse_lab_tests(sample_text)
    print(f"Found {len(results)} laboratory tests:")
    for i, test in enumerate(results, 1):
        unit_str = f" {test['unit']}" if test['unit'] else ""
        range_str = ""
        if test['reference_range']:
            range_str = f" [{test['reference_range']['min']}-{test['reference_range']['max']}]"
        status_str = f" {test['status']}" if test['status'] else ""
        print(f"{i}. {test['test_name']}: {test['value']}{unit_str}{range_str}{status_str}")

    # Validate we found some key tests
    test_names = [test['test_name'].lower() for test in results]
    expected_tests = ['hemoglobin', 'rbc count', 'wbc count', 'platelet count',
                     'glucose', 'urea', 'creatinine', 'cholesterol']

    found_count = 0
    for expected in expected_tests:
        found = any(expected in name for name in test_names)
        print(f"{'✓' if found else '✗'} Found '{expected}': {found}")
        if found:
            found_count += 1

    # Check that we didn't get false positives
    false_positives = ['page', 'printed on', 'approved on', 'client name', 'lab id']
    fp_found = [fp for fp in false_positives if any(fp in name.lower() for name in test_names)]
    print(f"False positives to avoid: {fp_found}")
    assert len(fp_found) == 0, f"Found false positives: {fp_found}"

    print(f"✓ Lab parser test completed! Found {found_count}/{len(expected_tests)} expected tests.")

if __name__ == "__main__":
    test_patient_parser()
    test_lab_parser()
    print("\n🎉 All tests passed!")