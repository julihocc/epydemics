import json
import sys

try:
    with open('examples/scenario_analysis_measles.ipynb', 'r', encoding='utf-8') as f:
        content = f.read()
        json.loads(content)
        print("JSON is valid.")
except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
    print(f"At line {e.lineno}, column {e.colno}")
    print(f"Char: {e.pos}")
    # Print the context
    lines = content.splitlines()
    if 0 <= e.lineno - 1 < len(lines):
        print(f"Line content: {lines[e.lineno-1]}")
