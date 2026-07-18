from app.services.parser.lab_parser import _extract_test_from_line_improved

test_line = "Glucose 95 mg/dL (ref: 70-100)"
print(f"Testing: {test_line}")

result = _extract_test_from_line_improved(test_line)
if result:
    print("Full result:")
    for k, v in result.items():
        print(f"  {k}: {v}")
else:
    print("No result")
