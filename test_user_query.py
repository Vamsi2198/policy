#!/usr/bin/env python3
"""
Test the exact query from user's log to verify the fix
"""

import sys
sys.path.insert(0, r'c:\Users\HP\OneDrive\Documents\policy\s3_policy\policy2 (3)\policy2 (2)\policy2\src')

from ai_control_plane import AIControlPlane
import logging

# Setup logging to match user's log format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize control plane
cp = AIControlPlane(config_path=r'c:\Users\HP\OneDrive\Documents\policy\s3_policy\policy2 (3)\policy2 (2)\policy2\config.yaml')

# User's exact query from the log
query = 'mask pii in RESIDENTIAL_ADDRESS  table for analyst roles'

print("\n" + "="*80)
print("TESTING USER'S EXACT QUERY")
print("="*80)
print(f"\nQuery: {query}")
print("\nExtracting table name...\n")

# Extract entities (table names)
entities = cp._extract_entities(query)

print("\n" + "="*80)
print("RESULTS")
print("="*80)
print(f"Extracted entities: {entities}")
print(f"First entity (table): {entities[0] if entities else 'NONE'}")

if entities and entities[0].upper() == 'RESIDENTIAL_ADDRESS':
    print("\n[SUCCESS] Table name 'RESIDENTIAL_ADDRESS' correctly extracted!")
    print("The fix resolves the issue - the query will now proceed with the correct table.\n")
else:
    print("\n[FAILED] Table extraction did not work as expected.\n")

# Also test role extraction
print("\nExtracting role directive...\n")
role_directive = cp._extract_role_directive(query)
print(f"Role directive: {role_directive}")
print(f"Role: {role_directive['role']}")
print(f"Visible to (unmasked): {role_directive['visible_for_roles']}")
print(f"Masked for: {role_directive['masked_for_roles']}")
print("\n" + "="*80 + "\n")
