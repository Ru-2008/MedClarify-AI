from app.services.parser.lab_parser import _extract_test_from_line_improved

# Test case from the issue
test_line = "Hemoglobin g/dL 13.0 - 16.5 Colorimetric 14.5"

print("Testing line:", test_line)
result = _extract_test_from_line_improved(test_line)

if result:
    print("Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
else:
    print("No result returned")

# Expected: value should be 14.5, not 13.0
if result and result.get('value') == 14.5:
    print("\nSUCCESS: Correct value (14.5) extracted!")
elif result:
    print(f"FAILURE: Expected value 14.5, got {result.get('value')}")
else:
    print("FAILURE: No result returned")
