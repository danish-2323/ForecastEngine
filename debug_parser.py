"""
Debug PDF Parser - Test with actual PDF content
"""

import re
from datetime import datetime

# Sample text from your PDF
text = """
Date: 2024-01-01 Model: iPhone 15 Sales: 234
Date: 2024-01-01 Model: iPhone 15 Pro Sales: 254
Date: 2024-01-01 Model: iPhone 15 Pro Max Sales: 163
Date: 2024-01-02 Model: iPhone 15 Sales: 300
"""

print("Testing different regex patterns:\n")

# Pattern 1: Original
pattern1 = r'Date:\s*(\d{4}-\d{2}-\d{2})\s+(?:Model|Product):\s*([A-Za-z0-9\s]+?)\s+Sales:\s*([\d,]+\.?\d*)'
matches1 = re.findall(pattern1, text, re.IGNORECASE)
print(f"Pattern 1 (greedy): {len(matches1)} matches")
for m in matches1[:2]:
    print(f"  Date: {m[0]}, Product: '{m[1]}', Sales: {m[2]}")

# Pattern 2: Non-greedy with lookahead
pattern2 = r'Date:\s*(\d{4}-\d{2}-\d{2})\s+(?:Model|Product):\s*(.+?)\s+Sales:\s*(\d+)'
matches2 = re.findall(pattern2, text, re.IGNORECASE)
print(f"\nPattern 2 (non-greedy): {len(matches2)} matches")
for m in matches2[:2]:
    print(f"  Date: {m[0]}, Product: '{m[1]}', Sales: {m[2]}")

# Pattern 3: Capture until Sales keyword
pattern3 = r'Date:\s*(\d{4}-\d{2}-\d{2})\s+(?:Model|Product|Item):\s*([^\n]+?)\s+Sales:\s*(\d+)'
matches3 = re.findall(pattern3, text, re.IGNORECASE)
print(f"\nPattern 3 (until newline): {len(matches3)} matches")
for m in matches3[:2]:
    print(f"  Date: {m[0]}, Product: '{m[1]}', Sales: {m[2]}")

# Pattern 4: Most specific
pattern4 = r'Date:\s*(\d{4}-\d{2}-\d{2})\s+Model:\s*([^S]+?)\s+Sales:\s*(\d+)'
matches4 = re.findall(pattern4, text)
print(f"\nPattern 4 (specific): {len(matches4)} matches")
for m in matches4[:2]:
    print(f"  Date: {m[0]}, Product: '{m[1].strip()}', Sales: {m[2]}")

print("\n" + "="*60)
print("RECOMMENDED PATTERN:")
print("="*60)
print("pattern = r'Date:\\s*(\\d{4}-\\d{2}-\\d{2})\\s+(?:Model|Product|Item|Device|SKU|Name):\\s*(.+?)\\s+Sales:\\s*(\\d+)'")
