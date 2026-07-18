import py_compile
import sys

try:
    py_compile.compile('app/services/parser/lab_parser.py', doraise=True)
    print("Compilation successful!")
except SyntaxError as e:
    print(f"Syntax error: {e}")
    print(f"Line {e.lineno}: {e.text}")
except Exception as e:
    print(f"Other error: {e}")