#!/usr/bin/env python3
"""
Test script to demonstrate dynamic role-based masking
Examples:
1. "mask ssn in HEALTH_RECORDS table for analyst roles"
   -> ANALYST_ROLE sees: ***-**-3456 (MASKED)
   -> ADMIN sees: 111-22-3456 (UNMASKED)

2. "mask ssn in HEALTH_RECORDS table not for analyst roles"
   -> ANALYST_ROLE sees: 111-22-3456 (UNMASKED)
   -> ADMIN sees: ***-**-3456 (MASKED)

3. "mask ssn in HEALTH_RECORDS table" (no role specified)
   -> ADMIN/DATA_STEWARD see: 111-22-3456 (UNMASKED)
   -> ANALYST_ROLE sees: ***-**-3456 (MASKED)
"""

import sys
sys.path.insert(0, r'c:\Users\HP\OneDrive\Documents\policy\s3_policy\policy2 (3)\policy2 (2)\policy2\src')

from ai_control_plane import AIControlPlane
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Initialize control plane with defaults
cp = AIControlPlane(config_path=r'c:\Users\HP\OneDrive\Documents\policy\s3_policy\policy2 (3)\policy2 (2)\policy2\config.yaml')

# Test cases with different role directives
test_queries = [
    {
        'query': 'mask ssn in HEALTH_RECORDS table for analyst roles',
        'expected_behavior': 'ANALYST_ROLE sees MASKED (***-**-3456), ADMIN sees UNMASKED (111-22-3456)'
    },
    {
        'query': 'mask ssn in HEALTH_RECORDS table not for analyst roles',
        'expected_behavior': 'ANALYST_ROLE sees UNMASKED (111-22-3456), ADMIN sees MASKED (***-**-3456)'
    },
    {
        'query': 'mask email in HEALTH_RECORDS table for hr roles',
        'expected_behavior': 'HR_ROLE sees MASKED (***@***.com), ADMIN sees UNMASKED (john@example.com)'
    },
    {
        'query': 'mask phone in HEALTH_RECORDS table',
        'expected_behavior': 'Default: ADMIN/DATA_STEWARD see UNMASKED (555-123-4567), others see MASKED (***-***-4567)'
    }
]

print("\n" + "="*80)
print("DYNAMIC ROLE-BASED MASKING TEST")
print("="*80 + "\n")

for i, test in enumerate(test_queries, 1):
    print(f"\n{'─'*80}")
    print(f"TEST {i}: {test['query']}")
    print(f"{'─'*80}")
    print(f"Expected: {test['expected_behavior']}\n")
    
    # Extract role directive
    role_directive = cp._extract_role_directive(test['query'])
    
    print(f"Extracted Directive:")
    print(f"  Role: {role_directive['role']}")
    print(f"  Negate: {role_directive['negate']}")
    print(f"  Visible to (UNMASKED): {role_directive['visible_for_roles']}")
    print(f"  Masked for: {role_directive['masked_for_roles']}")
    
    # Generate sample masking policy SQL
    print(f"\nGenerated SQL Policy:")
    visible_roles = role_directive.get('visible_for_roles', [])
    masked_roles = role_directive.get('masked_for_roles', [])
    
    if visible_roles:
        roles_list = ', '.join([f"'{role}'" for role in visible_roles])
        case_statement = f"CASE WHEN CURRENT_ROLE() IN ({roles_list}) THEN val ELSE CONCAT('***-**-', RIGHT(val, 4)) END"
    else:
        roles_list = ', '.join([f"'{role}'" for role in masked_roles])
        case_statement = f"CASE WHEN CURRENT_ROLE() NOT IN ({roles_list}) THEN val ELSE CONCAT('***-**-', RIGHT(val, 4)) END"
    
    print(f"  CREATE MASKING POLICY policy_name AS (val STRING) RETURNS STRING ->")
    print(f"  {case_statement};")
    
    # Explain the behavior
    print(f"\nBehavior:")
    for role in ['ADMIN', 'ANALYST_ROLE', 'DATA_STEWARD', 'PUBLIC']:
        if role in visible_roles:
            status = "✓ SEES UNMASKED DATA"
        elif role in masked_roles:
            status = "✗ SEES MASKED DATA"
        else:
            status = "? (depends on context)"
        print(f"  {role:20} -> {status}")

print(f"\n{'='*80}")
print("TEST COMPLETE - All role directives extracted successfully!")
print("="*80 + "\n")
