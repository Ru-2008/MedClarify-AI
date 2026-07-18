from app.services.parser.lab_parser import parse_lab_tests

# Test line from the issue
test_line = "Hemoglobin g/dL 13.0 - 16.5 Colorimetric 14.5"
results = parse_lab_tests(test_line)
print(f"Found {len(results)} tests:")
for test in results:
    print(f"  Test: {test['test_name']}")
    print(f"  Value: {test['value']}")
    print(f"  Unit: {test['unit']}")
    print(f"  Ref: {test['reference_range']}")
    print(f"  Status: {test['status']}")