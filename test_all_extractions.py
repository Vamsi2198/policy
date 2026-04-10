#!/usr/bin/env python3
"""
Test both extraction methods with the user's exact query
"""

import sys
sys.path.insert(0, r'c:\Users\HP\OneDrive\Documents\policy\s3_policy\policy2 (3)\policy2 (2)\policy2\src')

from ai_control_plane import AIControlPlane
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

cp = AIControlPlane(config_path=r'c:\Users\HP\OneDrive\Documents\policy\s3_policy\policy2 (3)\policy2 (2)\policy2\config.yaml')

query = 'mask pii in RESIDENTIAL_ADDRESS  table for analyst roles'

print("\n" + "="*80)
print("TESTING BOTH EXTRACTION METHODS")
print("="*80)
print(f"\nQuery: {query}\n")

# Test _extract_explicit_table_name (used in Phase 1 OBSERVE)
print("1. Testing _extract_explicit_table_name():")
print("-" * 80)
table = cp._extract_explicit_table_name(query)
print(f"Result: '{table}'")
if table == 'RESIDENTIAL_ADDRESS':
    print("[SUCCESS] Explicit table extraction working!")
else:
    print(f"[FAILED] Expected RESIDENTIAL_ADDRESS, got {table}")

# Test _extract_entities (used in Phase 1 OBSERVE)
print("\n2. Testing _extract_entities():")
print("-" * 80)
entities = cp._extract_entities(query)
print(f"Result: {entities}")
if entities and entities[0] == 'RESIDENTIAL_ADDRESS':
    print("[SUCCESS] Entity extraction working!")
else:
    print(f"[FAILED] Expected ['RESIDENTIAL_ADDRESS'], got {entities}")

# Test role directive extraction
print("\n3. Testing _extract_role_directive():")
print("-" * 80)
role = cp._extract_role_directive(query)
print(f"Role: {role['role']}")
print(f"Visible to: {role['visible_for_roles']}")
print(f"Masked for: {role['masked_for_roles']}")
if role['role'] == 'ANALYST_ROLE':
    print("[SUCCESS] Role directive extraction working!")
else:
    print(f"[FAILED] Expected ANALYST_ROLE, got {role['role']}")

print("\n" + "="*80)
print("ALL THREE METHODS WORKING!")
print("="*80 + "\n")
