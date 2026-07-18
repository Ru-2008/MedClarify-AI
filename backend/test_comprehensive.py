from app.services.parser.lab_parser import _extract_test_from_line_improved

test_cases = [
    # Original issue case - measured value last
    ("Hemoglobin g/dL 13.0 - 16.5 Colorimetric 14.5", 14.5),
    
    # Measured value first
    ("Glucose 95 mg/dL (ref: 70-100)", 95),
    
    # Single number
    ("HbA1c 5.8%", 5.8),
    
    # Measured value in middle
    ("Cholesterol total: 200 mg/dL Desirable: <200", 200),
]

print("Running comprehensive tests...")
print("="*50)

all_passed = True

for i, (test_line, expected_value) in enumerate(test_cases, 1):
    print(f"Test {i}: {test_line}")
    result = _extract_test_from_line_improved(test_line)
    
    if result:
        actual_value = result.get('value')
        print(f"  Result: value={actual_value}")
        if actual_value == expected_value:
            print("  PASS")
        else:
            print(f"  FAIL: expected {expected_value}, got {actual_value}")
            all_passed = False
    else:
        print("  FAIL: No result returned")
        all_passed = False
    print()

# Test case with no numbers
print("Test: No numbers")
result = _extract_test_from_line_improved("This is just text with no numbers")
if result is None:
    print("  PASS: Correctly returned None for no numbers")
else:
    print(f"  FAIL: Expected None, got {result}")
    all_passed = False

print("="*50)
if all_passed:
    print("ALL TESTS PASSED!")
else:
    print("SOME TESTS FAILED")
print("="*50)
