"""
Text cleaning utilities for medical report parsing.
"""

import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean the input text by normalizing unicode, replacing tabs with spaces,
    collapsing multiple whitespace, and normalizing line endings.

    Args:
        text: Raw text string.

    Returns:
        Cleaned text string.
    """
    if not text:
        return ""

    # Normalize unicode to compatibility composition
    text = unicodedata.normalize('NFKC', text)

    # Normalize line endings to LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Replace horizontal whitespace (spaces and tabs) with a single space
    # But we want to keep newlines intact, so we only replace spaces and tabs.
    text = re.sub(r'[ \t]+', ' ', text)

    # Collapse multiple newlines to a single newline
    text = re.sub(r'\n+', '\n', text)

    # Strip leading and trailing whitespace
    text = text.strip()

    return text


def split_into_lines(text: str) -> list[str]:
    """
    Split the cleaned text into lines and remove empty lines.

    Args:
        text: Cleaned text string.

    Returns:
        List of non-empty lines.
    """
    if not text:
        return []

    lines = text.split('\n')
    # Remove empty lines and lines that are only whitespace
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return non_empty_lines


def remove_duplicate_lines(text: str) -> str:
    """
    Remove consecutive duplicate lines from the text.
    """
    if not text:
        return ""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not cleaned_lines or stripped != cleaned_lines[-1].strip():
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


def merge_wrapped_lines(text: str) -> str:
    """
    Merge lines that were wrapped during OCR back into single lines.
    Strictly avoids merging across different table rows, page headers, footers,
    and identifier numbers (e.g. registration numbers, patient IDs).
    """
    if not text:
        return ""
    lines = text.split('\n')
    if not lines:
        return ""
    
    # Import WHITELIST locally or check against known test prefixes to avoid merging new rows
    from app.services.parser.lab_parser import WHITELIST
    whitelist_prefixes = tuple(WHITELIST.keys())

    non_merge_pattern = r'(?i)\b(page\s*\d+|\d+-\w+-\d+\s*years|printed\s*on|approved\s*on|collected\s*on|received\s*on|analysis\s*performed|sample\s*id|registration\s*no|registration\s*number|patient\s*id|uhid|lab\s*id|report\s*no|report\s*number|qr\s*code|watermark|end\s*of\s*report)\b|\b\d{8,25}\b'

    merged_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if not merged_lines:
            merged_lines.append(line)
            continue
        
        prev = merged_lines[-1].strip()
        if not prev:
            merged_lines.append(line)
            continue

        # Rule 0: NEVER merge if either previous line or current line matches non-merging metadata/identifier anchor
        if re.search(non_merge_pattern, prev) or re.search(non_merge_pattern, stripped):
            merged_lines.append(line)
            continue

        # Rule 1: NEVER merge if current line starts with a known lab test name (it is a separate table row)
        stripped_lower = stripped.lower()
        # Check word-boundary match at start of stripped line for any whitelist key
        is_new_test_row = False
        for k in whitelist_prefixes:
            if stripped_lower.startswith(k):
                # Ensure word boundary after k
                if len(stripped_lower) == len(k) or not stripped_lower[len(k)].isalnum():
                    is_new_test_row = True
                    break
        if is_new_test_row:
            merged_lines.append(line)
            continue

        # Rule 1.5: NEVER merge if current line looks like a column-table row
        # (ALL_CAPS test name optionally followed by H/L flag then a number)
        # e.g. "HEMOGLOBIN  15  g/dl  13 - 17" or "LYMPHOCYTE  L  18  %"
        if re.match(r'^[A-Z][A-Z ,\.\(\)/]+\s+(HH|LL|H|L|N)?\s*[\d,]+', stripped):
            merged_lines.append(line)
            continue

        # Rule 2: Check if previous line is explicitly unfinished or awaiting a value/unit
        is_prev_unfinished = (
            prev[-1] in ',-([/\\:' or 
            (not any(c.isdigit() for c in prev) and stripped[0].isdigit())
        )
        is_curr_continuation = (
            stripped.startswith('(') or 
            any(stripped.upper().startswith(u) for u in ['G/DL', 'MG/DL', 'MMOL/L', '%', 'X10', 'IU/L', 'NG/ML', 'PG/ML', '/CMM', 'FL', 'PG', 'MM/HR', 'U/L'])
        )

        if is_prev_unfinished or (is_curr_continuation and not any(c.isdigit() for c in prev)):
            merged_lines[-1] = merged_lines[-1] + " " + line.strip()
        else:
            merged_lines.append(line)
            
    return '\n'.join(merged_lines)


def fix_common_ocr_mistakes(text: str) -> str:
    """
    Fix common OCR errors (e.g. 0 -> O in words, l -> 1 in numbers).
    """
    if not text:
        return ""
    
    # 1. Replace '0' with 'O' in uppercase/lowercase alphabetic words
    # Word starts with letters, has 0, ends with letters
    text = re.sub(r'\b([A-Z]*)0([A-Z]+)\b', r'\1O\2', text)
    text = re.sub(r'\b([A-Z]+)0([A-Z]*)\b', r'\1O\2', text)
    text = re.sub(r'\b([a-z]*)0([a-z]+)\b', r'\1o\2', text)
    text = re.sub(r'\b([a-z]+)0([a-z]*)\b', r'\1o\2', text)
    
    # 2. Replace 'l', 'I', or '|' with '1' in numbers
    # Preceded or followed by a digit and optional dot
    text = re.sub(r'\b(\d+[\.\,]?)[lI|]\b', r'\g<1>1', text)
    text = re.sub(r'\b[lI|]([\.\,]?\d+)\b', r'1\g<1>', text)
    text = re.sub(r'\b(\d+)[lI|](\d+)\b', r'\g<1>1\g<2>', text)
    
    return text