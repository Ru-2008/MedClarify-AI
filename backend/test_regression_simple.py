import sys
sys.path.insert(0, "/c/Users/HOME/MEDCLARIFY AI (Backend)/backend")
from app.services.parser.lab_parser import _extract_test_from_line_improved

# Test case where measured value comes first (should still work)
test_line1 = "Glucose 95 mg/dL (ref: 70-100)"
print("Test 1: " + test_line1)
result1 = _extract_test_from_line_improved(test_line1)
if result1:
    print("  Result: value=" + str(result1['value']) + ", expected ~95.0")
    if abs(result1['value'] - 95.0) < 0.1:
        print("  PASS")
    else:
        print("  FAIL")
else:
    print("  FAIL: No result")

# Test case with measured value in middle
test_line2 = "Cholesterol total: 200 mg/dL Desirable: <200"
print("Test 2: " + test_line2)
result2 = _extract_test_from_line_improved(test_line2)
if result2:
    print("  Result: value=" + str(result2['value']) + ", expected ~200.0")
    if abs(result2['value'] - 200.0) < 0.1:
        print("  PASS")
    else:
        print("  FAIL")
else:
    print("  FAIL: No result")

# Test case with no numbers
test_line3 = "This is just text with no numbers"
print("Test 3: " + test_line3)
result3 = _extract_test_from_line_improved(test_line3)
if result3 is None:
    print("  PASS: Correctly returned None")
else:
    print("  FAIL: Expected None, got " + str(result3))

print("\nRegression test complete.")
