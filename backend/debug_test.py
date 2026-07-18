import sys
sys.path.insert(0, "/c/Users/HOME/MEDCLARIFY AI (Backend)/backend")
from app.services.parser.lab_parser import _extract_test_from_line_improved

# Exact test string from the issue
test_line = "Hemoglobin g/dL 13.0 - 16.5 Colorimetric 14.5"
print(f"Testing: {test_line}")
result = _extract_test_from_line_improved(test_line)
print("Result:")
if result:
    for k, v in result.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")
        else:
            print(f"  {k}: {v}")
else:
    print("  None")
