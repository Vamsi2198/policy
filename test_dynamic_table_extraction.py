#!/usr/bin/env python3
"""
Test dynamic table name extraction from natural language queries
"""

import sys
sys.path.insert(0, r'c:\Users\HP\OneDrive\Documents\policy\s3_policy\policy2 (3)\policy2 (2)\policy2\src')

from ai_control_plane import AIControlPlane
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Initialize control plane
cp = AIControlPlane(config_path=r'c:\Users\HP\OneDrive\Documents\policy\s3_policy\policy2 (3)\policy2 (2)\policy2\config.yaml')

# Test queries with various table name patterns
test_queries = [
    {
        'query': 'mask pii in RESIDENTIAL_ADDRESS table for analyst roles',
        'expected_table': 'RESIDENTIAL_ADDRESS',
        'description': 'in [TABLE] table pattern'
    },
    {
        'query': 'mask ssn from HEALTH_RECORDS',
        'expected_table': 'HEALTH_RECORDS',
        'description': 'from [TABLE] pattern'
    },
    {
        'query': 'mask pii on CUSTOMERS table',
        'expected_table': 'CUSTOMERS',
        'description': 'on [TABLE] table pattern'
    },
    {
        'query': 'mask email in USERS for analyst',
        'expected_table': 'USERS',
        'description': 'in [TABLE] pattern with role'
    },
    {
        'query': 'mask phone in EMPLOYEES table not for hr',
        'expected_table': 'EMPLOYEES',
        'description': 'in [TABLE] table pattern with negation'
    },
    {
        'query': 'mask ssn',
        'expected_table': 'CUSTOMERS',  # Default fallback
        'description': 'No table specified (should use default)'
    },
    {
        'query': 'mask in BANK_ACCOUNTS table',
        'expected_table': 'BANK_ACCOUNTS',
        'description': 'in [TABLE] table pattern'
    }
]

print("\n" + "="*80)
print("DYNAMIC TABLE EXTRACTION TEST")
print("="*80 + "\n")

passed = 0
failed = 0

for i, test in enumerate(test_queries, 1):
    print(f"\nTEST {i}: {test['description']}")
    print("-" * 80)
    print(f"Query: {test['query']}")
    print(f"Expected table: {test['expected_table']}\n")
    
    # Extract entities
    entities = cp._extract_entities(test['query'])
    extracted = entities[0].upper() if entities else 'NONE'
    
    print(f"Extracted entities: {entities}")
    print(f"Extracted table: {extracted}")
    
    # Check if it matches
    if extracted == test['expected_table']:
        print(f"[PASS] Correctly extracted table name")
        passed += 1
    else:
        print(f"[FAIL] Expected {test['expected_table']}, got {extracted}")
        failed += 1

print(f"\n{'='*80}")
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_queries)} tests")
print("="*80 + "\n")

if failed == 0:
    print("[SUCCESS] All tests passed! Dynamic table extraction is working correctly.\n")
else:
    print(f"[WARNING] {failed} test(s) failed. Review patterns above.\n")
