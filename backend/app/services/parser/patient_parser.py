"""
Patient information parser for medical reports.
Extracts patient details such as name, age, gender, report date, and extra fields.
Supports multiple lab report layouts:
  - NRL/Sterling Accuris: patient header at beginning of extracted text
  - Vertical column table (e.g. CBC reports): patient metadata block at end of report
Produces no hardcoded lab name fallbacks — returns None if unknown.
"""

import logging
import re
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PatientInfoParser:
    """Layout-agnostic patient information parser."""

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def parse_patient_info(self, text: str) -> Dict[str, Optional[str]]:
        logger.info("Starting patient information parsing")

        result = {
            "name": None,
            "age": None,
            "gender": None,
            "report_date": None,
            "lab_name": None,
            "doctor_name": None,
            "patient_id": None,
            "sample_type": None,
            "collection_date": None,
            "approval_date": None,
            "hospital": None,
            "doctor": None,
            "laboratory": None,
            "registration_number": None,
            "uhid": None,
            "lab_id": None
        }

        if not text:
            return result

        # ----------------------------------------------------------------
        # 1. Locate patient info block
        #    Supports both top-of-page (NRL/Accuris) and bottom-of-page
        #    (vertical CBC report) layouts.
        # ----------------------------------------------------------------
        patient_section = self._find_patient_section(text)

        # ----------------------------------------------------------------
        # 2. Name
        # ----------------------------------------------------------------
        result["name"] = self._extract_name(patient_section, text)

        # ----------------------------------------------------------------
        # 3. Age + Gender  (often co-located: "27 YRS / M" or "41 Years-Male")
        # ----------------------------------------------------------------
        age, gender = self._extract_age_gender(patient_section, text)
        result["age"] = age
        result["gender"] = gender

        # ----------------------------------------------------------------
        # 4. Patient ID / Registration number
        # ----------------------------------------------------------------
        pid, reg_num, uhid, lab_id = self._extract_ids(patient_section, text)
        result["patient_id"] = pid
        result["registration_number"] = reg_num or pid
        result["uhid"] = uhid or pid
        result["lab_id"] = lab_id

        # ----------------------------------------------------------------
        # 5. Dates
        # ----------------------------------------------------------------
        col_date = self._extract_date(patient_section,
            r'(?i)(?:collected\s*on|collection\s*date|collected)\s*[:\-]?\s*'
            r'(\d{1,2}[-\/\.](?:[A-Za-z]{3}|\d{1,2})[-\/\.]\d{2,4}|\d{1,2}\/\d{1,2}\/\d{4})'
        )
        result["collection_date"] = col_date

        app_date = self._extract_date(patient_section,
            r'(?i)(?:reported\s*on|report(?:ed)?\s*date|approval\s*date|approved\s*on|'
            r'date\s*of\s*report)\s*[:\-]?\s*'
            r'(\d{1,2}[-\/\.](?:[A-Za-z]{3}|\d{1,2})[-\/\.]\d{2,4}|\d{1,2}\/\d{1,2}\/\d{4})'
        )
        if not app_date:
            # Fallback: any date-like string after "registered on"
            app_date = self._extract_date(patient_section,
                r'(?i)registered\s*on\s*[:\-]?\s*'
                r'(\d{1,2}[-\/\.](?:[A-Za-z]{3}|\d{1,2})[-\/\.]\d{2,4}|\d{1,2}\/\d{1,2}\/\d{4})'
            )

        result["approval_date"] = app_date
        result["report_date"] = app_date or col_date

        # ----------------------------------------------------------------
        # 6. Sample type
        # ----------------------------------------------------------------
        result["sample_type"] = self._extract_sample_type(patient_section)

        # ----------------------------------------------------------------
        # 7. Hospital / Doctor / Laboratory
        # ----------------------------------------------------------------
        hospital, doctor, laboratory = self._extract_org_info(patient_section, text)
        result["hospital"] = hospital
        result["doctor"] = doctor
        result["doctor_name"] = doctor
        # NEVER fabricate a lab name — return None if not determinable
        result["laboratory"] = laboratory
        result["lab_name"] = laboratory

        self._normalize_fields(result)
        logger.info(f"Patient information parsed: {result}")
        return result

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    def _find_patient_section(self, text: str) -> str:
        """
        Locate the patient metadata block within the full extracted text.
        Checks the beginning (NRL/Accuris format) and the end (vertical CBC format).
        Returns the most informative 3000-char window.
        """
        lines = text.split("\n")

        # Filter out per-page repeated certification/watermark lines
        filtered = []
        for line in lines:
            ll = line.lower()
            if re.search(r'\d+-\w+-\d+\s*Years', line) or re.search(r'\d+-Mr\.?\s', line):
                continue
            if any(k in ll for k in [
                'md path', 'hematopathologist', 'electronically authenticated',
                'scan qr code', 'report authenticity'
            ]):
                if not any(d in ll for d in ['collected', 'registration', 'received', 'sex/age']):
                    continue
            filtered.append(line)

        cleaned = "\n".join(filtered)

        # ── Strategy A: vertical CBC reports have patient block near the END ──
        # Detect anchor lines like "Reg. no.", "Age / Sex", "Referred by"
        cbc_anchor_re = re.compile(
            r'(?i)(reg\.?\s*no\.?|age\s*/\s*sex|referred\s*by|registered\s*on|reported\s*on)',
            re.MULTILINE
        )
        matches = list(cbc_anchor_re.finditer(cleaned))
        if matches:
            # Take the earliest anchor — there may be duplicates across pages
            first_anchor = matches[0].start()
            candidate = cleaned[max(0, first_anchor - 200): first_anchor + 800]
            # Validate: does it contain a date or number?
            if re.search(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}', candidate) \
                    or re.search(r'\d{1,3}\s*(?:yrs?|years?)', candidate, re.IGNORECASE):
                return candidate

        # ── Strategy B: first 3000 chars (NRL/Accuris inline format) ──
        return cleaned[:3000]

    def _extract_name(self, section: str, full_text: str) -> Optional[str]:
        """Extract patient name from various label patterns."""

        # Pattern 1: "Mr. Saubhik Bhaumik" on its own (not followed by professional title)
        # Avoid matching lines like "Dr. Sanjeev Shah MD Pathologist"
        for m in re.finditer(
            r'\b(?:Mr|Mrs|Ms)\.?\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
            section
        ):
            name = m.group(1).strip()
            # Trim at first newline or keyword boundary
            name = re.split(r'[\n\r]|(?:\bAge\b|\bSex\b|\bReg\b|\bDate\b)', name)[0].strip()
            # Reject if looks like a doctor (title suffix or followed by degree)
            after = section[m.end():m.end()+30]
            if re.search(r'(?i)\b(md|mbbs|pathologist|dr\.|dmlt|phd|ms\.)', after):
                continue
            if re.search(r'(?i)\b(md|mbbs|pathologist|dmlt|phd)\b', name):
                continue
            # Must have at least one space (first + last name)
            if ' ' in name and all(p[0].isupper() for p in name.split() if p):
                return name

        # Pattern 2: "Patient Name: John Doe" or "Client Name: ..."
        # Only match explicit "patient name" or "client name" labels (not generic "name")
        m = re.search(
            r'(?i)(?:patient\s*name|client\s*name)\s*[:\-]?\s*'
            r'(?!dr\.?\s*|doctor\s*)([A-Za-z][A-Za-z ]{2,40})',
            section
        )
        if m:
            name = m.group(1).strip().split('\n')[0].strip()
            # Reject if contains lab/org keywords
            reject_words = {'sterling', 'accuris', 'diagnostics', 'laboratory', 'lab', 'clinic',
                           'hospital', 'centre', 'center', 'pathology', 'buddy', 'limited', 'pvt'}
            if name.lower() not in ('information', 'not available', 'unknown', '') \
               and not any(w in name.lower() for w in reject_words) \
               and 1 <= len(name.split()) <= 5:
                return name

        # Pattern 3: Coordinate layout "Lyubochka SvetkaName"
        m = re.search(
            r'(?i)(?:^|\s|\n|:)\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)Name',
            section
        )
        if m:
            return m.group(1).strip()

        # Pattern 4: Search full text for Mr/Mrs (first occurrence)
        for m in re.finditer(
            r'\b(?:Mr|Mrs|Ms)\.?\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)',
            full_text
        ):
            name = m.group(1).strip()
            name = re.split(r'[\n\r]|(?:\bAge\b|\bSex\b|\bReg\b)', name)[0].strip()
            after = full_text[m.end():m.end()+30]
            if re.search(r'(?i)\b(md|mbbs|pathologist|dr\.|dmlt|phd)', after):
                continue
            if ' ' in name:
                return name

        return None

    def _extract_age_gender(self, section: str, full_text: str):
        """Extract age and gender, supporting multiple format patterns."""
        age = None
        gender = None

        # Pattern 1: "Age / Sex : 27 YRS / M"  (vertical CBC format)
        m = re.search(
            r'(?i)age\s*/\s*sex\s*[:\-]?\s*(\d{1,3})\s*(?:yrs?|years?)?\s*/\s*(m|f|male|female)',
            section + "\n" + full_text[:200]
        )
        if m:
            age = m.group(1).strip()
            raw_gender = m.group(2).strip().upper()
            gender = 'Male' if raw_gender in ('M', 'MALE') else 'Female'
            return age, gender

        # Pattern 2: "41 Years-Male" (NRL inline header)
        m = re.search(r'\b(\d{1,3})\s*Years[-–](Male|Female)\b', section, re.IGNORECASE)
        if m:
            age = m.group(1).strip()
            gender = m.group(2).strip().capitalize()
            return age, gender

        # Pattern 3: standalone age "41 Years" / "41 Yrs" / "41 Y"
        m = re.search(r'\b(\d{1,3})\s*(?:Years?|Yrs?|Y)\b', section, re.IGNORECASE)
        if m:
            age = m.group(1).strip()

        # Pattern 4: labelled "Age: 45"
        if not age:
            m = re.search(r'(?i)(?:^|\s)age\s*[:\-]\s*(\d{1,3})\b', section)
            if m:
                age = m.group(1).strip()

        # Gender separately
        m = re.search(r'\b(Male|Female)\b', section, re.IGNORECASE)
        if m:
            gender = m.group(1).strip().capitalize()
        if not gender:
            m = re.search(r'(?i)(?:gender|sex)\s*[:\-]?\s*(male|female|other|m|f)\b', section)
            if m:
                g = m.group(1).strip().upper()
                gender = 'Male' if g in ('M', 'MALE') else 'Female' if g in ('F', 'FEMALE') else m.group(1).capitalize()

        return age, gender

    def _extract_ids(self, section: str, full_text: str):
        """
        Extract patient ID, registration number, UHID, and lab ID.
        Requires values of at least 3 characters to avoid single-letter false matches.
        """
        pid = None
        reg_num = None
        uhid = None
        lab_id = None

        # ── Registration / Reg. no. ──
        # New CBC format: "Reg. no. : 1001"
        m = re.search(
            r'(?i)reg\.?\s*no\.?\s*[:\-]?\s*([A-Za-z0-9\-]{2,30})',
            section
        )
        if m:
            val = m.group(1).strip()
            if len(val) >= 2 and val.lower() not in ('on', 'final', 'status', 'no'):
                reg_num = val

        # ── Old NRL format: registration number as long numeric ──
        if not reg_num:
            m = re.search(
                r'(?i)(?:registration\s*number|registration\s*no|ref\s*no|ref\s*number|ref\s*id)'
                r'\s*[:\-]?\s*([A-Za-z0-9\-]+)',
                section
            )
            if m:
                val = m.group(1).strip()
                if len(val) >= 3:
                    reg_num = val

        # ── Patient ID / UHID / MRN ──
        m = re.search(
            r'(?i)(?:patient\s*id|uhid|mrn)\s*[:\-]?\s*([A-Za-z0-9\-]{3,30})',
            section
        )
        if m:
            val = m.group(1).strip()
            if val.lower() not in ('printed', 'on', 'final', 'status'):
                pid = val

        # NRL-specific: long numeric ID embedded in page header
        if not pid:
            m = re.search(r'\b(022\d{9})\b', full_text)
            if m:
                pid = m.group(1)

        # ── Lab ID ──
        m = re.search(r'(?i)lab\s*id\s*[:\-]?\s*([A-Z0-9X\-]+)', section)
        if m:
            lab_id = m.group(1).strip()

        # ── UHID ──
        m = re.search(r'(?i)uhid\s*[:\-]?\s*([A-Za-z0-9\-]{3,30})', section)
        if m:
            uhid = m.group(1).strip()

        return pid or reg_num, reg_num or pid, uhid, lab_id

    def _extract_date(self, section: str, pattern: str) -> Optional[str]:
        m = re.search(pattern, section)
        if m:
            return m.group(1).strip()
        return None

    def _extract_sample_type(self, section: str) -> Optional[str]:
        m = re.search(
            r'(?i)sample\s*type\s*[:\-]?\s*([a-zA-Z ]{3,30})(?=\s*[\n\|]|$)',
            section
        )
        if m:
            s_type = m.group(1).strip()
            s_type = re.sub(r'(?i)\b(?:process|at|information)\b.*', '', s_type).strip()
            if s_type and s_type.lower() not in ('information',):
                return s_type
        return None

    def _extract_org_info(self, section: str, full_text: str):
        """Extract hospital, doctor, and laboratory name."""
        hospital = None
        doctor = None
        laboratory = None

        # ── Hospital ──
        m = re.search(
            r'(?i)hospital\s*[:\-]?\s*([a-zA-Z ]{3,50})(?=\s*[\n\|]|$)',
            section
        )
        if m:
            hospital = m.group(1).strip()

        # ── Doctor: "Referred by" or "Doctor:" ──
        # Use single-line match to avoid pulling in multiple lines
        m = re.search(
            r'(?i)(?:ref(?:erred)?\s*by|doctor|physician)\s*[:\-]?\s*'
            r'([A-Za-z][A-Za-z \.]{2,50}?)\s*(?:[\n\r]|$)',
            section
        )
        if m:
            ref_val = m.group(1).strip()
            ref_val = re.sub(r'[:\s]+$', '', ref_val).strip()
            if any(k in ref_val.lower() for k in [
                'nrl', 'sawpl', 'lab', 'accuris', 'hospital', 'clinic',
                'center', 'centre', 'diagnostics', 'pathology'
            ]):
                laboratory = ref_val
            elif ref_val.lower() not in ('self', 'none', '', 'na', 'n/a') and len(ref_val) > 2:
                doctor = ref_val

        # ── Laboratory: standalone line containing lab keywords ──
        if not laboratory:
            # Explicit "laboratory: Name" pattern (no cross-newline)
            m = re.search(
                r'(?i)laboratory[ \t]*[:\-]+[ \t]*([a-zA-Z ]{3,60})(?=[ \t]*[\r\n\|]|$)',
                section
            )
            if m:
                laboratory = m.group(1).strip()

        if not laboratory:
            # Scan all lines in the patient section for a standalone lab name
            for p_line in section.split("\n"):
                p_clean = p_line.strip()
                if not p_clean or len(p_clean) > 80:
                    continue
                if any(k in p_clean.lower() for k in [
                    'diagnostics limited', 'diagnostics pvt', 'laboratory', 'pathology',
                    'clinical lab', 'medical lab', 'health lab', 'accuris', 'nrl sawpl',
                ]):
                    if not any(w in p_clean.lower() for w in [
                        'test', 'report', 'end of', 'page', 'performed', 'laboratory test',
                        'clinical laboratory', 'clinical notes',
                    ]):
                        laboratory = p_clean
                        break

        # ── Doctor: try Dr. pattern if not found yet ──
        if not doctor:
            m = re.search(
                r'\bDr\.?\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z\.]+)*)',
                section
            )
            if m:
                candidate = m.group(1).strip()
                # Exclude known lab-staff titles
                if 'pathologist' not in section[section.find(m.group(0)):section.find(m.group(0))+60].lower():
                    doctor = candidate

        return hospital, doctor, laboratory

    def _normalize_fields(self, result: dict):
        for k, v in result.items():
            if isinstance(v, str):
                result[k] = v.strip() or None


def parse_patient_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract patient information from the given text.

    Args:
        text: Extracted text from the medical report.

    Returns:
        Dictionary containing patient fields.
    """
    parser = PatientInfoParser()
    return parser.parse_patient_info(text)