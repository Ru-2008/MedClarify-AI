import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.services.unified_extraction import extract_text
from app.services.parser.patient_parser import parse_patient_info
from app.services.parser.lab_parser import parse_lab_tests

pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploaded_reports')
pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
if not pdf_files:
    print("No PDF files found")
    sys.exit(1)
pdf_path = os.path.join(pdf_dir, pdf_files[0])
print(f"Using PDF: {pdf_path}")
text = extract_text(pdf_path)
print(f"Extracted text length: {len(text)}")
print("First 500 chars:")
print(text[:500])
print("\n--- Patient Info ---")
patient = parse_patient_info(text)
for k, v in patient.items():
    print(f"{k}: {v}")
print("\n--- Lab Tests ---")
tests = parse_lab_tests(text)
print(f"Found {len(tests)} tests")
for i, t in enumerate(tests[:10]):
    print(f"{i+1}: {t}")
