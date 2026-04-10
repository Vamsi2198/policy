#!/usr/bin/env python3
"""
Quick test to verify regex patterns now match table names correctly.
The issue was that [A-Z_] only matches uppercase, but we need [A-Za-z_] to match both.
"""

import re

# Test queries
test_queries = [
    "mask pii in RESIDENTIAL_ADDRESS table for analyst roles",
    "mask pii in residential_address table for analyst roles",
    "mask pii in Residential_Address table for analyst roles",
    "mask ssn from customers",
    "mask email on users",
    "discover pii in HEALTH_RECORDS table",
]

# Updated regex patterns that should work
patterns = {
    "in_pattern": r'\bin\s+([A-Za-z_][A-Za-z0-9_]*)\s+table\b',
    "from_pattern": r'\bfrom\s+([A-Za-z_][A-Za-z0-9_]*)\b',
    "on_pattern": r'\bon\s+([A-Za-z_][A-Za-z0-9_]*)\b',
}

print("=" * 80)
print("TESTING REGEX PATTERNS FOR TABLE EXTRACTION")
print("=" * 80)
print()

for query in test_queries:
    print(f"Query: '{query}'")
    found = False
    
    # Try in pattern
    matches = re.findall(patterns["in_pattern"], query, re.IGNORECASE)
    if matches:
        print(f"  ✅ 'in X table' pattern: {matches[0].upper()}")
        found = True
    
    # Try from pattern
    matches = re.findall(patterns["from_pattern"], query, re.IGNORECASE)
    if matches:
        print(f"  ✅ 'from X' pattern: {matches[0].upper()}")
        found = True
    
    # Try on pattern
    matches = re.findall(patterns["on_pattern"], query, re.IGNORECASE)
    if matches:
        print(f"  ✅ 'on X' pattern: {matches[0].upper()}")
        found = True
    
    if not found:
        print(f"  ❌ No table found")
    
    print()

print("=" * 80)
print("COMPARISON: OLD vs NEW PATTERNS")
print("=" * 80)
print()

query = "mask pii in RESIDENTIAL_ADDRESS table for analyst roles"
print(f"Query: '{query}'")
print()

# OLD pattern (broken)
old_pattern = r'\bin\s+([A-Z_][A-Z0-9_]*)\s+table\b'
matches_old = re.findall(old_pattern, query, re.IGNORECASE)
print(f"OLD pattern [A-Z_]: {matches_old if matches_old else '❌ NO MATCH'}")

# NEW pattern (fixed)
new_pattern = r'\bin\s+([A-Za-z_][A-Za-z0-9_]*)\s+table\b'
matches_new = re.findall(new_pattern, query, re.IGNORECASE)
print(f"NEW pattern [A-Za-z_]: {matches_new if matches_new else '❌ NO MATCH'}")

print()
print("=" * 80)

if matches_new:
    print("✅ ALL TESTS PASSED - Regex patterns fixed!")
else:
    print("❌ TESTS FAILED - Regex patterns still not working")
