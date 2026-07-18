"""
Laboratory test parser for medical reports.
Extracts analyte names, values, units, reference ranges, methods, and status.
Refactored to support word-boundary matching, whitelisting, row-based constraints, and strict validation.
"""

import logging
import re
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Complete analyte whitelist to ensure extraction accuracy (Step 8)
WHITELIST = {
    # Complete Blood Count (CBC) / Hematology
    "hemoglobin": "Hemoglobin",
    "haemoglobin": "Hemoglobin",
    "rbc count": "RBC Count",
    "total rbc count": "RBC Count",
    "rbc": "RBC Count",
    "wbc count": "WBC Count",
    "wbc": "WBC Count",
    "total leukocyte count": "WBC Count",
    "total leucocyte count": "WBC Count",
    "leukocyte count": "WBC Count",
    "leucocyte count": "WBC Count",
    "leukocytes": "WBC Count",
    "leucocytes": "WBC Count",
    "platelet count": "Platelet Count",
    "platelets": "Platelet Count",
    "platelet": "Platelet Count",
    "thrombocytes": "Platelet Count",
    "mcv": "MCV",
    "mean corpuscular volume, mcv": "MCV",
    "mean corpuscular volume": "MCV",
    "mch": "MCH",
    "mean cell haemoglobin, mch": "MCH",
    "mean cell hemoglobin, mch": "MCH",
    "mean corpuscular haemoglobin": "MCH",
    "mean corpuscular hemoglobin": "MCH",
    "mchc": "MCHC",
    "mean cell haemoglobin con, mchc": "MCHC",
    "mean cell hemoglobin con, mchc": "MCHC",
    "mean corpuscular haemoglobin concentration": "MCHC",
    "mean corpuscular hemoglobin concentration": "MCHC",
    "rdw": "RDW",
    "rdw cv": "RDW CV",
    "rdw-cv": "RDW CV",
    "rdw-sd": "RDW",
    "hematocrit": "Hematocrit",
    "haematocrit": "Hematocrit",
    "hematocrit value, hct": "Hematocrit",
    "haematocrit value, hct": "Hematocrit",
    "hct": "Hematocrit",
    "packed cell volume": "Hematocrit",
    "pcv": "Hematocrit",
    "mpv": "MPV",
    
    # Differential / Absolute Counts
    "neutrophils": "Neutrophils",
    "neutrophil": "Neutrophils",
    "polymorphs": "Neutrophils",
    "lymphocytes": "Lymphocytes",
    "lymphocyte": "Lymphocytes",
    "eosinophils": "Eosinophils",
    "eosinophil": "Eosinophils",
    "monocytes": "Monocytes",
    "monocyte": "Monocytes",
    "basophils": "Basophils",
    "basophil": "Basophils",
    "absolute neutrophil count": "Absolute Neutrophil Count",
    "absolute neutrophils": "Absolute Neutrophil Count",
    "absolute lymphocyte count": "Absolute Lymphocyte Count",
    "absolute lymphocytes": "Absolute Lymphocyte Count",
    "absolute eosinophil count": "Absolute Eosinophil Count",
    "absolute eosinophils": "Absolute Eosinophil Count",
    "absolute monocyte count": "Absolute Monocyte Count",
    "absolute monocytes": "Absolute Monocyte Count",
    "absolute basophil count": "Absolute Basophil Count",
    "absolute basophils": "Absolute Basophil Count",
    
    # Lipid Profile
    "cholesterol": "Total Cholesterol",
    "total cholesterol": "Total Cholesterol",
    "triglyceride": "Triglycerides",
    "triglycerides": "Triglycerides",
    "hdl cholesterol": "HDL Cholesterol",
    "hdl": "HDL Cholesterol",
    "ldl cholesterol": "LDL Cholesterol",
    "ldl": "LDL Cholesterol",
    "direct ldl": "Direct LDL",
    "vldl": "VLDL",
    "vldl cholesterol": "VLDL",
    "chol/hdl ratio": "CHOL/HDL Ratio",
    "ldl/hdl ratio": "LDL/HDL Ratio",
    
    # Renal / Electrolytes / Minerals
    "urea": "Urea",
    "blood urea nitrogen": "Blood Urea Nitrogen",
    "bun": "Blood Urea Nitrogen",
    "creatinine": "Creatinine",
    "creatinine, serum": "Creatinine",
    "uric acid": "Uric Acid",
    "calcium": "Calcium",
    "sodium": "Sodium",
    "potassium": "Potassium",
    "chloride": "Chloride",
    
    # Liver Function / Enzymes / Proteins
    "sgpt": "SGPT",
    "sgot": "SGOT",
    "alt": "ALT",
    "ast": "AST",
    "alt (sgpt)": "ALT (SGPT)",
    "ast (sgot)": "AST (SGOT)",
    "total bilirubin": "Total Bilirubin",
    "conjugated bilirubin": "Conjugated Bilirubin",
    "unconjugated bilirubin": "Unconjugated Bilirubin",
    "delta bilirubin": "Delta Bilirubin",
    "bilirubin": "Total Bilirubin",
    "total protein": "Total Protein",
    "albumin": "Albumin",
    "globulin": "Globulin",
    "a/g ratio": "A/G Ratio",
    
    # Thyroid Profile
    "tsh": "TSH",
    "t3": "T3",
    "t4": "T4",
    "free t3": "Free T3",
    "free t4": "Free T4",
    "triiodothyronine": "T3",
    "thyroxine": "T4",
    "thyroid stimulating hormone": "TSH",
    
    # Vitamins / Anemia / Others
    "vitamin d": "Vitamin D",
    "25(oh) vitamin d": "Vitamin D",
    "25-hydroxy vitamin d": "Vitamin D",
    "vitamin b12": "Vitamin B12",
    "folate": "Folate",
    "folic acid": "Folate",
    "iron": "Iron",
    "ferritin": "Ferritin",
    "tibc": "TIBC",
    "total iron binding capacity": "TIBC",
    "transferrin saturation": "Transferrin Saturation",
    "homocysteine": "Homocysteine",
    "homocysteine, serum": "Homocysteine",
    "psa": "PSA",
    "prostate specific antigen": "PSA",
    "psa-prostate specific antigen, total": "PSA",
    "ige": "IgE",
    "immunoglobulin e": "IgE",
    "hiv": "HIV I & II Ab/Ag",
    "hiv i & ii": "HIV I & II Ab/Ag",
    "hbsag": "HBsAg",
    "esr": "ESR",
    "erythrocyte sedimentation rate": "ESR",
    "glucose": "Glucose",
    "fasting blood sugar": "Glucose",
    "hba1c": "HbA1c",
    "mean blood glucose": "Mean Blood Glucose",
    "microalbumin": "Microalbumin",
    
    # Urine / Chemical strip
    "urine glucose": "Urine Glucose",
    "urine protein": "Urine Protein",
    "urine ketone": "Urine Ketone",
    "nitrite": "Nitrite",
    "urobilinogen": "Urobilinogen",
    "specific gravity": "Specific Gravity",
    "ph": "pH",
    "colour": "Colour",
    "clearity": "Clearity",
    "pus cells": "Pus Cells",
    "red cells": "Red Cells",
    "epithelial cells": "Epithelial Cells",
    "casts": "Casts",
    "crystals": "Crystals",
    "amorphous material": "Amorphous Material",
    
    # HPLC Electrophoresis Specific
    "hb a": "Hb A",
    "hb a2": "Hb A2",
    "foetal hb": "Foetal Hb",
}

VALID_UNITS = {
    'g/dL', 'mg/dL', 'mg/L', 'µg/L', 'ug/L', 'IU/L', 'mIU/L',
    'mmol/L', 'mol/L', '%', 'x10^3/µL', 'x10^6/µL', 'x10^9/L',
    '/µL', '/mm3', '/L', 'mEq/L', 'ng/mL', 'pg/mL', 'µIU/mL',
    'iU/mL', 'mu/mL', 'cU/mL', 'mmHg', 'cmH2O', 'mL/min',
    'mL/min/m2', 'sec', 'seconds', 'minutes', 'hours', 'U/L', 'u/L',
    # Extended units to restore missing values in report context
    'mg/mL', 'million/cmm', 'fL', 'pg', 'mm/1hr', 'mm/hr', '/cmm', 
    'microIU/mL', 'micromol/L', 'micro g/dL', 'IU/mL', 'microg/dL', 
    'ug/dL', 'µg/dL', 'g/l', 'mg/dl', 'g/dl',
    # Lakhs-scale and alternative CBC units
    'lakhs/cumm', 'lakh/cumm', 'lacs/cumm', 'lac/cumm',
    'cumm', 'cells/cumm', 'thou/cumm', 'K/cumm', 'K/uL', 'M/uL',
    'x10^3/uL', 'x10^6/uL', '10^3/uL', '10^6/uL',
}

DEFAULT_UNITS = {
    "Hemoglobin": "g/dL",
    "RBC Count": "million/cmm",
    "Hematocrit": "%",
    "MCV": "fL",
    "MCH": "pg",
    "MCHC": "g/dL",
    "RDW": "%",
    "RDW CV": "%",
    "WBC Count": "/cmm",
    "Platelet Count": "/cmm",
    "MPV": "fL",
    "ESR": "mm/hr",
    "Total Cholesterol": "mg/dL",
    "Triglycerides": "mg/dL",
    "HDL Cholesterol": "mg/dL",
    "LDL Cholesterol": "mg/dL",
    "Direct LDL": "mg/dL",
    "VLDL": "mg/dL",
    "Glucose": "mg/dL",
    "Mean Blood Glucose": "mg/dL",
    "HbA1c": "%",
    "TSH": "microIU/mL",
    "T3": "ng/mL",
    "T4": "mg/mL",
    "Creatinine": "mg/dL",
    "Urea": "mg/dL",
    "Blood Urea Nitrogen": "mg/dL",
    "Uric Acid": "mg/dL",
    "Calcium": "mg/dL",
    "SGPT": "U/L",
    "SGOT": "U/L",
    "Sodium": "mmol/L",
    "Potassium": "mmol/L",
    "Chloride": "mmol/L",
    "Total Protein": "g/dL",
    "Albumin": "g/dL",
    "Globulin": "g/dL",
    "Total Bilirubin": "mg/dL",
    "Conjugated Bilirubin": "mg/dL",
    "Unconjugated Bilirubin": "mg/dL",
    "Delta Bilirubin": "mg/dL",
    "Iron": "micro g/dL",
    "TIBC": "micro g/dL",
    "Homocysteine": "micromol/L",
    "Vitamin B12": "pg/mL",
    "IgE": "IU/mL",
    "Microalbumin": "mg/L",
}

SANITY_CHECKS = {
    "Hemoglobin": (2.0, 30.0),
    "RBC Count": (0.5, 15.0),
    "Hematocrit": (10.0, 80.0),
    "MCV": (30.0, 200.0),
    "MCH": (10.0, 60.0),
    "MCHC": (15.0, 50.0),
    "RDW": (5.0, 40.0),
    "RDW CV": (5.0, 40.0),
    "WBC Count": (0.1, 1000000.0),
    "Platelet Count": (0.1, 2000000.0),
    "MPV": (4.0, 25.0),
    "Neutrophils": (0.0, 100.0),
    "Lymphocytes": (0.0, 100.0),
    "Eosinophils": (0.0, 100.0),
    "Monocytes": (0.0, 100.0),
    "Basophils": (0.0, 100.0),
    "Absolute Neutrophil Count": (0.0, 100000.0),
    "Absolute Lymphocyte Count": (0.0, 100000.0),
    "Absolute Eosinophil Count": (0.0, 100000.0),
    "Absolute Monocyte Count": (0.0, 100000.0),
    "Absolute Basophil Count": (0.0, 100000.0),
    "ESR": (0.0, 150.0),
    "Total Cholesterol": (20.0, 1000.0),
    "Triglycerides": (10.0, 3000.0),
    "HDL Cholesterol": (5.0, 200.0),
    "LDL Cholesterol": (5.0, 1000.0),
    "Direct LDL": (5.0, 1000.0),
    "VLDL": (2.0, 500.0),
    "CHOL/HDL Ratio": (0.1, 50.0),
    "LDL/HDL Ratio": (0.1, 50.0),
    "Glucose": (10.0, 1000.0),
    "Mean Blood Glucose": (10.0, 1000.0),
    "HbA1c": (2.0, 20.0),
    "TSH": (0.001, 200.0),
    "T3": (0.1, 20.0),
    "T4": (0.5, 50.0),
    "T4 (Thyroxine)": (0.5, 50.0),
    "T3 (Triiodothyronine)": (0.1, 20.0),
    "Free T3": (0.5, 30.0),
    "Free T4": (0.1, 15.0),
    "Vitamin D": (2.0, 250.0),
    "Vitamin B12": (10.0, 3000.0),
    "Folate": (0.5, 100.0),
    "Iron": (5.0, 1000.0),
    "Ferritin": (1.0, 5000.0),
    "TIBC": (50.0, 1000.0),
    "Transferrin Saturation": (1.0, 100.0),
    "Creatinine": (0.05, 20.0),
    "Urea": (2.0, 300.0),
    "Blood Urea Nitrogen": (1.0, 150.0),
    "Uric Acid": (0.5, 30.0),
    "Calcium": (1.0, 30.0),
    "SGPT": (1.0, 5000.0),
    "SGOT": (1.0, 5000.0),
    "ALT": (1.0, 5000.0),
    "AST": (1.0, 5000.0),
    "ALT (SGPT)": (1.0, 5000.0),
    "AST (SGOT)": (1.0, 5000.0),
    "Total Bilirubin": (0.05, 50.0),
    "Conjugated Bilirubin": (0.0, 30.0),
    "Unconjugated Bilirubin": (0.0, 30.0),
    "Delta Bilirubin": (0.0, 10.0),
    "Total Protein": (1.0, 15.0),
    "Albumin": (1.0, 10.0),
    "Globulin": (0.5, 10.0),
    "A/G Ratio": (0.1, 10.0),
    "Sodium": (50.0, 200.0),
    "Potassium": (1.0, 15.0),
    "Chloride": (50.0, 200.0),
    "Homocysteine": (1.0, 200.0),
    "PSA": (0.0, 1000.0),
    "IgE": (0.0, 50000.0),
    "Microalbumin": (0.1, 5000.0),
    "Hb A": (0.0, 100.0),
    "Hb A2": (0.0, 20.0),
    "Foetal Hb": (0.0, 20.0),
}


class LabTestParser:
    """Production-grade medical report parser for laboratory tables."""

    def __init__(self):
        # Sort whitelist keys by length descending to prevent shorter substring match overrides
        self.sorted_whitelist_keys = sorted(WHITELIST.keys(), key=len, reverse=True)

    def parse_lab_tests(self, text: str) -> List[Dict]:
        if not text:
            return []

        layout = self._detect_layout(text)
        if layout == "column_table":
            tests = self._parse_column_table(text)
        else:
            tests = self._parse_inline_rows(text)

        # Remove duplicates based on name
        tests = self._remove_duplicates(tests)
        return tests

    def _detect_layout(self, text: str) -> str:
        """
        Detect whether the report uses a vertical column-table layout or inline row format.
        Handles two sub-variants of column table:
          A) Horizontal: each row on one line "HEMOGLOBIN  15  g/dl  13 - 17"
          B) Vertical/multi-line: each column field on its own line (PDF column extraction)

        Returns: 'column_table' or 'inline_row'
        """
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        # Explicit column header check — works for both sub-variants
        # The headers may be on a single line OR consecutive separate lines
        first_n = '\n'.join(lines[:20])
        if re.search(r'(?i)\bTEST\b.{0,30}\bVALUE\b', first_n):
            return "column_table"

        # Multi-line variant: header labels appear on consecutive lines alone
        header_words = {'TEST', 'VALUE', 'UNIT', 'REFERENCE'}
        consecutive_headers = sum(1 for l in lines[:10] if l.strip().upper() in header_words)
        if consecutive_headers >= 3:
            return "column_table"

        # Single-line variant: rows like "HEMOGLOBIN  15  g/dl  13 - 17"
        col_like = sum(
            1 for l in lines[:20]
            if re.match(r'^[A-Z][A-Z ,\.\(\)/]+\s+(H|L|HH|LL)?\s*[\d,\.]+\s+[a-zA-Z/%]', l)
        )
        if col_like >= 3:
            return "column_table"

        return "inline_row"

    # ------------------------------------------------------------------ #
    # LAYOUT A: column table parser (TEST | VALUE | UNIT | REFERENCE)    #
    # ------------------------------------------------------------------ #

    # Pattern for inline H/L abnormal flags
    _HL_FLAG_RE = re.compile(r'\b(HH|LL|H|L|N)\b')
    # Pattern for known lakhs-scale units
    _LAKHS_UNITS = {'lakhs/cumm', 'lakh/cumm', 'lacs/cumm', 'lac/cumm'}
    # Known unit tokens (lowercase) for recognition in multi-line mode
    _UNIT_TOKENS = {u.lower() for u in {
        'g/dl', 'mg/dl', 'mg/l', 'ug/l', 'iu/l', 'miu/l', 'mmol/l', 'mol/l',
        '%', 'x10^3/ul', 'x10^6/ul', 'x10^9/l', '/ul', '/mm3', '/l', 'meq/l',
        'ng/ml', 'pg/ml', 'uiu/ml', 'iu/ml', 'mu/ml', 'cu/ml', 'mmhg', 'u/l',
        'mg/ml', 'million/cmm', 'fl', 'pg', 'mm/1hr', 'mm/hr', '/cmm',
        'microiu/ml', 'micromol/l', 'micro g/dl', 'ug/dl',
        'lakhs/cumm', 'lakh/cumm', 'lacs/cumm', 'lac/cumm', 'cumm', 'k/ul',
        'x10^3/ul', 'x10^6/ul', '10^3/ul', '10^6/ul', 'thou/cumm',
    }}

    def _parse_column_table(self, text: str) -> List[Dict]:
        """
        Parse reports that use a vertical column-table layout.
        Supports BOTH:
          A) Single-line rows: "HEMOGLOBIN  15  g/dl  13 - 17"
          B) Multi-line per-entry (PDF column extraction artefact):
               HEMOGLOBIN
               15
               g/dl
               13 - 17
               LYMPHOCYTE
               L
               18
               %
               20 - 40
        Strategy: collect consecutive lines into groups, detect boundaries
        at known test names, then assemble each group into a record.
        """
        lines = [l.strip() for l in text.split('\n')]
        tests = []

        # ── Step 1: Locate start and end of data table ──
        table_start = 0
        table_end = len(lines)
        header_words = {'TEST', 'VALUE', 'UNIT', 'REFERENCE', 'REMARKS'}

        for i, line in enumerate(lines):
            if line.upper() in header_words:
                table_start = i + 1  # skip past last header word
            # Check single-line header "TEST  VALUE  UNIT"
            if re.search(r'(?i)\bTEST\b.{0,30}\bVALUE\b', line):
                table_start = i + 1
                break

        # Find end: first line that signals patient info / clinical notes
        for i in range(table_start, len(lines)):
            if self._is_column_section_end(lines[i]):
                table_end = i
                break

        data_lines = lines[table_start:table_end]

        # ── Step 2: Try single-line parsing first ──
        single_line_hits = 0
        for line in data_lines:
            if not line:
                continue
            # Single-line row has at least: test_name + number
            if re.match(r'^[A-Za-z].*[\d,]+', line):
                result = self._parse_column_row(line)
                if result and self._is_valid_test(result):
                    tests.append(result)
                    single_line_hits += 1

        if single_line_hits >= 2:
            return tests

        # ── Step 3: Multi-line per-entry parsing ──
        # Group lines into logical records. A new record starts when we see
        # a whitelist test name on its own line (or with only a flag after it).
        tests = []
        groups: List[List[str]] = []
        current_group: List[str] = []

        for line in data_lines:
            if not line:
                continue
            line_lower = line.lower()

            # Check if this line is a test name start
            is_test_name = False
            for k in self.sorted_whitelist_keys:
                pat = r'\b' if k[0].isalnum() else ''
                pat += re.escape(k)
                pat += r'\b' if k[-1].isalnum() else ''
                # Must be either the whole line or line starts with the key
                if re.match(pat + r'\s*(HH|LL|H|L|N)?\s*$', line_lower) or \
                   re.match(pat + r'(?:\s+(HH|LL|H|L|N))?\s*$', line_lower):
                    is_test_name = True
                    break

            if is_test_name and current_group:
                groups.append(current_group)
                current_group = [line]
            else:
                current_group.append(line)

        if current_group:
            groups.append(current_group)

        # Parse each group as one record
        for group in groups:
            result = self._parse_multiline_group(group)
            if result and self._is_valid_test(result):
                tests.append(result)

        # If nothing found, fall back to inline row parsing
        if not tests:
            return self._parse_inline_rows(text)

        return tests

    def _is_column_section_end(self, line: str) -> bool:
        """Returns True when we've hit a line that marks end of table data."""
        lower = line.lower()
        end_markers = [
            'clinical note', 'clinical notes', 'note:', 'possible causes',
            'referred by', 'reg. no', 'registered on', 'reported on',
            'collected on', 'received on', 'scan to download', 'end of report',
            '~~~ end', 'page ', 'mbbs', 'dmlt', 'md path', 'pathologist',
            'lab incharge', 'mr.', 'mrs.', 'ms.',
        ]
        return any(m in lower for m in end_markers)

    def _parse_multiline_group(self, group: List[str]) -> Optional[Dict]:
        """
        Parse a group of consecutive lines that together represent one analyte row.
        Typical group for multi-line format:
          ["HEMOGLOBIN", "15", "g/dl", "13 - 17"]
          ["LYMPHOCYTE", "L", "18", "%", "20 - 40"]
          ["PLATELET COUNT", "3.5", "lakhs/cumm", "1.5 - 4.1"]
        """
        if not group:
            return None

        # ── Line 0: Test name (possibly with H/L flag on same line) ──
        name_line = group[0].strip()
        name_lower = name_line.lower()

        test_key = None
        for k in self.sorted_whitelist_keys:
            pat = r'\b' if k[0].isalnum() else ''
            pat += re.escape(k)
            pat += r'\b' if k[-1].isalnum() else ''
            if re.match(pat, name_lower):
                test_key = k
                break

        if not test_key:
            return None

        test_name = WHITELIST[test_key]
        after_name = name_line[len(test_key):].strip()

        # ── Collect remaining tokens from subsequent lines ──
        tokens = []
        if after_name:
            tokens.append(after_name)
        for line in group[1:]:
            stripped = line.strip()
            if stripped:
                tokens.append(stripped)

        # ── Parse tokens: [flag?] [value] [unit] [range] ──
        flag = None
        value = None
        value_str_raw = None
        unit = None
        low_str = None
        high_str = None

        i = 0
        while i < len(tokens):
            tok = tokens[i].strip()

            # Flag token (single letter H/L/HH/LL on its own)
            if re.match(r'^(HH|LL|H|L|N)$', tok, re.IGNORECASE) and value is None:
                flag = tok.upper()
                i += 1
                continue

            # Numeric value (possibly comma-separated like 5,100)
            num_match = re.match(r'^([\d,]+(?:\.\d+)?)$', tok)
            if num_match and value is None:
                value_str_raw = tok
                value_str = tok.replace(',', '')
                if len(value_str.split('.')[0]) >= 8:
                    return None  # identifier, not a lab value
                value = float(value_str)
                i += 1
                continue

            # Range pattern "13 - 17" or "4,800 - 10,800" or "< 2"
            range_match = re.match(r'^([\d,]+\.?\d*)\s*[-\u2013]\s*([\d,]+\.?\d*)$', tok)
            if range_match:
                low_str = range_match.group(1).replace(',', '')
                high_str = range_match.group(2).replace(',', '')
                i += 1
                continue
            upper_match = re.match(r'^(?:<|less\s+than\s*=?)\s*([\d,]+\.?\d*)$', tok, re.IGNORECASE)
            if upper_match:
                high_str = upper_match.group(1).replace(',', '')
                i += 1
                continue

            # Unit token
            if unit is None:
                tok_lower = tok.lower().strip('().,;:')
                matched_unit = None
                for u in sorted(VALID_UNITS, key=len, reverse=True):
                    if tok_lower == u.lower():
                        matched_unit = u
                        break
                if matched_unit or tok_lower in self._UNIT_TOKENS:
                    unit = matched_unit or tok
                    i += 1
                    continue
                if value is not None:
                    # Treat as unit anyway (unlisted unit like "Pg")
                    unit = tok
                    i += 1
                    continue

            i += 1

        if value is None:
            return None

        # Lakhs normalization: 3.5 lakhs/cumm → 350000 /cmm
        if unit and unit.lower() in self._LAKHS_UNITS:
            value = value * 100000
            value_str_raw = str(int(value))
            unit = '/cmm'

        # Sanity check
        sanity_range = SANITY_CHECKS.get(test_name)
        if sanity_range:
            min_v, max_v = sanity_range
            if not (min_v <= value <= max_v):
                logger.warning(f"Multi-line group sanity check failed for {test_name}: {value}")
                return None
        else:
            if value >= 5000000 or (value >= 100000 and test_name not in ["WBC Count", "Platelet Count"]):
                return None

        reference_range = None
        if low_str is not None or high_str is not None:
            reference_range = {
                "min": float(low_str) if low_str else None,
                "max": float(high_str) if high_str else None
            }

        # Status: prefer flag over computed
        status = None
        if flag == 'H' or flag == 'HH':
            status = 'high'
        elif flag == 'L' or flag == 'LL':
            status = 'low'
        elif reference_range:
            lo = reference_range.get('min')
            hi = reference_range.get('max')
            if lo is not None and value < lo:
                status = 'low'
            elif hi is not None and value > hi:
                status = 'high'
            else:
                status = 'normal'

        # Default unit fallback
        if not unit and test_name in DEFAULT_UNITS:
            unit = DEFAULT_UNITS[test_name]

        # Normalize unit casing
        unit_canonical = {
            'mg/dl': 'mg/dL', 'g/dl': 'g/dL', 'ug/dl': '\u00b5g/dL',
            'iu/l': 'IU/L', 'miu/l': 'mIU/L', 'mmol/l': 'mmol/L',
            'u/l': 'U/L', 'ng/ml': 'ng/mL', 'pg/ml': 'pg/mL',
            'iu/ml': 'IU/mL', 'mg/l': 'mg/L', 'ug/l': '\u00b5g/L', 'mm/1hr': 'mm/hr',
            'fl': 'fL', 'pg': 'pg', 'cumm': '/cmm',
        }
        if unit and unit.lower() in unit_canonical:
            unit = unit_canonical[unit.lower()]

        return {
            "test_name": test_name,
            "value": value,
            "unit": unit,
            "reference_range": reference_range,
            "method": None,
            "flag": flag,
            "status": status,
            "raw_value": value_str_raw,
            "source_text": " | ".join(group),
            "extraction_strategy": "column_table_multiline",
            "confidence": 0.92
        }

    def _parse_column_row(self, line: str) -> Optional[Dict]:
        """
        Parse a single row from a vertical column table.
        Format: TEST_NAME [H|L|HH|LL] VALUE UNIT LOW - HIGH
        Example:
          LYMPHOCYTE  L  18  %  20 - 40
          PLATELET COUNT  3.5  lakhs/cumm  1.5 - 4.1
          MCHC  H  35.7  %  31.5 - 34.5
        """
        # 1. Match whitelist test name at start of line
        line_lower = line.lower()
        test_key = None
        for k in self.sorted_whitelist_keys:
            pattern = ''
            if k[0].isalnum():
                pattern += r'\b'
            pattern += re.escape(k)
            if k[-1].isalnum():
                pattern += r'\b'
            if re.match(pattern, line_lower):
                test_key = k
                break

        if not test_key:
            return None

        test_name = WHITELIST[test_key]
        # Remaining text after test name
        remaining = line[len(test_key):].strip()

        # 2. Strip leading punctuation/symbols
        remaining = re.sub(r'^[-–\*•\s\.\,]+', '', remaining).strip()

        # 3. Extract and record H/L flag (if any, before the number)
        flag = None
        flag_match = re.match(r'^(HH|LL|H|L|N)\b\s*', remaining, re.IGNORECASE)
        if flag_match:
            flag = flag_match.group(1).upper()
            remaining = remaining[flag_match.end():].strip()

        # 4. Extract numeric value (may have commas: 5,100)
        val_match = re.match(r'^([\d,]+(?:\.\d+)?)', remaining)
        if not val_match:
            return None

        value_str_raw = val_match.group(1)
        value_str = value_str_raw.replace(',', '')  # remove comma separators
        # Reject pure identifiers (8+ digit integers)
        if len(value_str.split('.')[0]) >= 8:
            return None
        value = float(value_str)
        remaining = remaining[val_match.end():].strip()

        # 5. Extract unit (next whitespace-delimited token)
        unit = None
        unit_token_match = re.match(r'^(\S+)', remaining)
        if unit_token_match:
            unit_candidate = unit_token_match.group(1).strip('().,;:')
            # Check if it matches any known unit (case-insensitive)
            for u in sorted(VALID_UNITS, key=len, reverse=True):
                if unit_candidate.lower() == u.lower():
                    unit = u
                    break
            if unit is None and unit_candidate:
                unit = unit_candidate  # accept as-is, will be normalized later
            remaining = remaining[unit_token_match.end():].strip()

        # 6. Lakhs normalization: 3.5 lakhs/cumm → 350000 /cmm
        if unit and unit.lower() in self._LAKHS_UNITS:
            value = value * 100000
            value_str = str(int(value))
            unit = '/cmm'

        # Normalize comma-stripped value str
        value_str_clean = str(value) if '.' in str(value) else str(int(value))

        # 7. Sanity check
        sanity_range = SANITY_CHECKS.get(test_name)
        if sanity_range:
            min_v, max_v = sanity_range
            if not (min_v <= value <= max_v):
                logger.warning(f"Column-table sanity check failed for {test_name}: {value}")
                return None
        else:
            if value >= 5000000 or (value >= 100000 and test_name not in ["WBC Count", "Platelet Count"]):
                return None

        # 8. Extract reference range (remaining: "LOW - HIGH" or "< N" or "> N")
        low_str = None
        high_str = None
        range_match = re.search(r'([\d,]+\.?\d*)\s*[-–]\s*([\d,]+\.?\d*)', remaining)
        if range_match:
            low_str = range_match.group(1).replace(',', '')
            high_str = range_match.group(2).replace(',', '')
        else:
            upper_match = re.search(r'(?i)(?:<|less\s+than\s*=?)\s*([\d,]+\.?\d*)', remaining)
            if upper_match:
                high_str = upper_match.group(1).replace(',', '')
            else:
                lower_match = re.search(r'(?i)(?:>|greater\s+than\s*=?)\s*([\d,]+\.?\d*)', remaining)
                if lower_match:
                    low_str = lower_match.group(1).replace(',', '')

        reference_range = None
        if low_str is not None or high_str is not None:
            reference_range = {
                "min": float(low_str) if low_str else None,
                "max": float(high_str) if high_str else None
            }

        # 9. Determine status — prefer flag over computed
        status = None
        if flag == 'H' or flag == 'HH':
            status = 'high'
        elif flag == 'L' or flag == 'LL':
            status = 'low'
        elif value is not None and reference_range is not None:
            lo = reference_range.get('min')
            hi = reference_range.get('max')
            if lo is not None and value < lo:
                status = 'low'
            elif hi is not None and value > hi:
                status = 'high'
            else:
                status = 'normal'

        # 10. Restore default unit if missing
        if not unit and test_name in DEFAULT_UNITS:
            unit = DEFAULT_UNITS[test_name]

        # Normalize unit casing
        unit_canonical = {
            'mg/dl': 'mg/dL', 'g/dl': 'g/dL', 'ug/dl': 'µg/dL',
            'iu/l': 'IU/L', 'miu/l': 'mIU/L', 'mmol/l': 'mmol/L',
            'u/l': 'U/L', 'ng/ml': 'ng/mL', 'pg/ml': 'pg/mL',
            'iu/ml': 'IU/mL', 'mg/l': 'mg/L', 'ug/l': 'µg/L', 'mm/1hr': 'mm/hr',
            'fl': 'fL', 'pg': 'pg',
        }
        if unit and unit.lower() in unit_canonical:
            unit = unit_canonical[unit.lower()]

        return {
            "test_name": test_name,
            "value": value,
            "unit": unit,
            "reference_range": reference_range,
            "method": None,
            "flag": flag,
            "status": status,
            "raw_value": value_str_raw,
            "source_text": line,
            "extraction_strategy": "column_table",
            "confidence": 0.93
        }

    # ------------------------------------------------------------------ #
    # LAYOUT B: inline row parser (original format)                      #
    # ------------------------------------------------------------------ #

    def _parse_inline_rows(self, text: str) -> List[Dict]:
        """Parse the original inline-row format."""
        lines = text.split('\n')
        tests = []
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            test = self._parse_line(line_str)
            if test and self._is_valid_test(test):
                tests.append(test)
        return tests

    def _is_metadata_line(self, line: str) -> bool:
        l_lower = line.lower()
        if re.search(r'\bpage\s*\d+\b', l_lower):
            return True
        if any(k in l_lower for k in [
            'printed on', 'approved on', 'collected on', 'received on', 'analysis performed',
            'sample information', 'patient information', 'client/location', 'registration on',
            'scan qr code', 'report authenticity', 'laboratory test report', 'referred test',
            'md path', 'pathology', 'hematopathologist', 'electronically authenticated',
            'doctor name', 'client name', 'end of report', 'interpretation:', 'note:',
            'comments:', 'disclaimer:', 'methodology:', 'reference text', 'years-male', 'years-female'
        ]):
            return True
        if re.search(r'\b\d{8,25}\b', line):
            return True
        if re.search(r'\b(uhid|mrn|reg\s*no|reg\s*number|registration\s*no|registration\s*number|patient\s*id|sample\s*id|lab\s*id|report\s*no|report\s*number|qr\s*code|watermark|timestamp)\b', l_lower):
            return True
        return False

    def _parse_line(self, line: str) -> Optional[Dict]:
        if self._is_metadata_line(line):
            return None

        # Step 6: Decimal / Integer Range Splitting preprocessing
        merged_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.\d+\.\d+|\d{5,10}\.\d+|\d{5,10})', line)
        if merged_match:
            low_val = merged_match.group(1)
            merged_val = merged_match.group(2)
            parts = self._split_merged_numbers(merged_val)
            if len(parts) == 2:
                line = line.replace(f"{low_val} - {merged_val}", f"{low_val} - {parts[0]} {parts[1]}")
                line = line.replace(f"{low_val}-{merged_val}", f"{low_val} - {parts[0]} {parts[1]}")

        line_lower = line.lower()
        
        # 1. Whitelist match using word boundaries (longest first)
        test_key = None
        for k in self.sorted_whitelist_keys:
            pattern = ""
            if k[0].isalnum() or k[0] == '_':
                pattern += r'\b'
            pattern += re.escape(k)
            if k[-1].isalnum() or k[-1] == '_':
                pattern += r'\b'
            if re.search(pattern, line_lower):
                test_key = k
                break
                
        if not test_key:
            return None
            
        test_name = WHITELIST[test_key]
        
        # 2. Extract remaining text ONLY after the matched key (Row-based parsing constraint)
        idx = line_lower.find(test_key)
        remaining = line[idx+len(test_key):].strip()
        
        # Strip list prefixes like "1. ", "• "
        remaining = re.sub(r'^[-–\*•▪▫◦✓✗o\s\.\,]+', '', remaining).strip()
        
        # Strip inline H/L/HH/LL abnormal flag token (appears right after test name)
        # e.g. "WBC Count H /cmm ..." or "MPV H fL ..."
        inline_flag = None
        flag_match = re.match(r'^(HH|LL|H|L)\b\s*', remaining, re.IGNORECASE)
        if flag_match:
            inline_flag = flag_match.group(1).upper()
            remaining = remaining[flag_match.end():].strip()
        
        low_str = None
        high_str = None
        range_text = ""
        
        # 3. Range detection
        range_match = re.search(r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)', remaining)
        if range_match:
            low_str = range_match.group(1)
            high_str = range_match.group(2)
            range_text = range_match.group(0)
            remaining = remaining.replace(range_text, "", 1).strip()
        else:
            upper_match = re.search(r'(?i)(?:up\s+to\s+|<|less\s+than\s*=?)\s*(\d+\.?\d*)', remaining)
            if upper_match:
                high_str = upper_match.group(1)
                range_text = upper_match.group(0)
                remaining = remaining.replace(range_text, "", 1).strip()
            else:
                lower_match = re.search(r'(?i)(?:>|greater\s+than\s*=?)\s*(\d+\.?\d*)', remaining)
                if lower_match:
                    low_str = lower_match.group(1)
                    range_text = lower_match.group(0)
                    remaining = remaining.replace(range_text, "", 1).strip()

        # 4. Standalone value extraction within same table row
        value_match = re.search(r'\b(\d+\.?\d*)\b', remaining)
        if not value_match:
            return None
            
        value_str = value_match.group(1)
        # Reject if integer part has >= 8 digits (identifier numbers like 022321600126)
        if len(value_str.split('.')[0]) >= 8:
            logger.warning(f"Rejecting identifier/long number extracted as value: {value_str}")
            return None

        value = float(value_str)
        remaining = remaining.replace(value_str, "", 1).strip()

        # Sanity check validation layer
        sanity_range = SANITY_CHECKS.get(test_name)
        if sanity_range:
            min_v, max_v = sanity_range
            if not (min_v <= value <= max_v):
                logger.warning(f"Sanity check failed for {test_name}: impossible value {value}")
                return None
        else:
            # Universal bounds for unlisted checks
            if value >= 5000000 or (value >= 100000 and test_name not in ["WBC Count", "Platelet Count"]):
                return None
        
        unit = None
        method = None
        
        # 5. Unit extraction (checking words and longer unit phrases in remaining and source_text)
        sorted_valid_units = sorted(VALID_UNITS, key=len, reverse=True)
        # First check remaining text with exact case
        for u in sorted_valid_units:
            pattern = re.escape(u)
            if re.search(r'(?:\b|\s|^)' + pattern + r'(?:\b|\s|$|\))', remaining):
                unit = u
                break
        if not unit:
            # Then check remaining text case-insensitively
            for u in sorted_valid_units:
                pattern = re.escape(u)
                if re.search(r'(?:\b|\s|^)' + pattern + r'(?:\b|\s|$|\))', remaining, re.IGNORECASE):
                    unit = u
                    break
        if not unit:
            words = remaining.split()
            for word in words:
                word_clean = re.sub(r'[\(\)\:\.\,]', '', word).strip()
                if word_clean in VALID_UNITS:
                    unit = word_clean
                    break
        if not unit:
            for u in sorted_valid_units:
                pattern = re.escape(u)
                if re.search(r'(?:\b|\s|^)' + pattern + r'(?:\b|\s|$|\))', line, re.IGNORECASE):
                    unit = u
                    break

        # Normalize casing and variations (e.g. mm/1hr -> mm/hr, mg/dl -> mg/dL)
        unit_canonical = {
            'mg/dl': 'mg/dL', 'g/dl': 'g/dL', 'ug/dl': 'µg/dL', 'microg/dl': 'microg/dL',
            'iu/l': 'IU/L', 'miu/l': 'mIU/L', 'mmol/l': 'mmol/L', 'u/l': 'U/L', 'ng/ml': 'ng/mL',
            'pg/ml': 'pg/mL', 'iu/ml': 'IU/mL', 'mg/l': 'mg/L', 'ug/l': 'µg/L', 'mm/1hr': 'mm/hr'
        }
        if unit and unit.lower() in unit_canonical:
            unit = unit_canonical[unit.lower()]

        # Restore missing unit if report clearly implies or known test default
        if not unit and test_name in DEFAULT_UNITS:
            unit = DEFAULT_UNITS[test_name]
                
        # 6. Method extraction (Step 5)
        known_methods = [
            'uv with p5p ifcc', 'uv with p5p', 'uv', 'ifcc', 'clia', 'eclia',
            'elisa', 'hplc', 'god-pod', 'god/pod', 'colorimetric', 'direct-ise',
            'direct ise', 'direct measured', 'direct', 'calculated', 'derived',
            'electrical impedance', 'capillary photometry', 'chemiluminescence',
            'microscopic'
        ]
        rem_lower = remaining.lower()
        for m in known_methods:
            if m in rem_lower:
                method = m.upper()
                break
                
        # Build final reference range dictionary
        reference_range = None
        if low_str is not None or high_str is not None:
            reference_range = {
                "min": float(low_str) if low_str else None,
                "max": float(high_str) if high_str else None
            }

        status = None
        # Prefer the inline flag (H/L) over computed status for precision
        if inline_flag == 'H' or inline_flag == 'HH':
            status = 'high'
        elif inline_flag == 'L' or inline_flag == 'LL':
            status = 'low'
        elif value is not None and reference_range is not None:
            low = reference_range.get("min")
            high = reference_range.get("max")
            if low is not None and value < low:
                status = "low"
            elif high is not None and value > high:
                status = "high"
            else:
                status = "normal"

        return {
            "test_name": test_name,
            "value": value,
            "unit": unit,
            "reference_range": reference_range,
            "method": method,
            "flag": inline_flag,
            "status": status,
            "raw_value": value_str,
            "source_text": line,
            "extraction_strategy": "custom_parser",
            "confidence": 0.95
        }

    def _split_merged_numbers(self, s: str) -> List[str]:
        # Case 1: Double decimal points like 11.727.84 -> 11.72, 7.84
        double_decimal = re.match(r'^(\d+\.\d{1,2})(\d+\.\d{1,4})$', s)
        if double_decimal:
            return [double_decimal.group(1), double_decimal.group(2)]

        # Case 2: Range high merged with value with decimals: e.g. 462352.00 -> 462, 352.00
        # Require the decimal part to be present
        merged_int = re.match(r'^(\d{3})(\d{3})(\.\d+)$', s)
        if merged_int:
            val2 = merged_int.group(2) + merged_int.group(3)
            return [merged_int.group(1), val2]

        return [s]

    def _is_valid_test(self, test: Dict) -> bool:
        # Step 7 & 8: Strict validation layer
        test_name = test.get("test_name")
        if not test_name or test_name not in WHITELIST.values():
            return False

        value = test.get("value")
        if value is None:
            return False

        # Enforce sanity range verification
        sanity_range = SANITY_CHECKS.get(test_name)
        if sanity_range:
            min_v, max_v = sanity_range
            if not (min_v <= value <= max_v):
                return False
        else:
            if value >= 5000000 or (value >= 100000 and test_name not in ["WBC Count", "Platelet Count"]):
                return False

        source_text = test.get("source_text", "")
        source_lower = source_text.lower()
        
        # 1. Reject if line contains paragraph indicators or certify notes
        if any(w in source_lower for w in [
            'md path', 'pathology', 'hematopathologist', 'electronically authenticated',
            'approved on', 'printed on', 'scan qr code', 'report authenticity',
            'laboratory test report', 'referred test', 'page ', 'biological reference',
            'disclaimer', 'clinical correlation', 'intoxication', 'malabsorption',
            'accompanying comments', 'linearity range', 'typical beta thalassemia',
            'counselling', 'responsibility', 'physician', 'recommended to rule out',
            'screening and management', 'screening test for', 'referring physician',
            'normal urinary albumin excretion', 'ratio of albumin:creatinine'
        ]):
            return False

        # 2. Reject if line has high paragraph word count
        paragraph_words = {
            'the', 'and', 'of', 'for', 'with', 'to', 'in', 'on', 'at', 'by', 'an', 'be',
            'is', 'are', 'was', 'were', 'that', 'this', 'these', 'those', 'which',
            'have', 'has', 'had', 'but', 'or', 'as', 'if', 'then', 'else', 'when',
            'where', 'why', 'how', 'should', 'would', 'could', 'will', 'please'
        }
        words = [w.strip(',.:;()') for w in source_lower.split()]
        paragraph_word_count = sum(1 for w in words if w in paragraph_words)
        if paragraph_word_count >= 2:
            return False

        # 3. Reject if the line has no unit and no range, and is long (indicates text narrative)
        if not test.get("unit") and not (test.get("reference_range") and (test["reference_range"]["min"] is not None or test["reference_range"]["max"] is not None)):
            if len(source_text) > 40:
                return False

        return True

    def _remove_duplicates(self, tests: List[Dict]) -> List[Dict]:
        if not tests:
            return tests
        seen = {}
        for test in tests:
            seen[test["test_name"]] = test
        return list(seen.values())


def parse_lab_tests(text: str) -> List[Dict]:
    parser = LabTestParser()
    return parser.parse_lab_tests(text)


def _extract_test_from_line_improved(line: str) -> Optional[Dict]:
    parser = LabTestParser()
    results = parser.parse_lab_tests(line)
    return results[0] if results else None