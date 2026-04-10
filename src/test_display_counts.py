"""
Test to verify rows_affected and columns_affected display correctly
"""

import sys
import json

# Simulate the data structure
simulate_result = {
    'affected_rows': 3,  # Should show 3 (from CUSTOMERS table)
    'affected_columns': [
        'CUSTOMERS.SSN',
        'CUSTOMERS.EMAIL',
        'CUSTOMERS.PHONE',
        'CUSTOMERS.FULL_NAME',
        'CUSTOMERS.ADDRESS'
    ],
    'risk_assessment': 'LOW'
}

analyze_result = {
    'pii_findings': [
        {'table': 'CUSTOMERS', 'column': 'SSN', 'pii_types': ['SSN']},
        {'table': 'CUSTOMERS', 'column': 'EMAIL', 'pii_types': ['EMAIL_ADDRESS']},
        {'table': 'CUSTOMERS', 'column': 'PHONE', 'pii_types': ['PHONE_NUMBER']},
        {'table': 'CUSTOMERS', 'column': 'FULL_NAME', 'pii_types': ['PERSON']},
        {'table': 'CUSTOMERS', 'column': 'ADDRESS', 'pii_types': ['ADDRESS']},
    ]
}

print("\n=== SIMULATION RESULT TEST ===")
print(f"Rows Affected: {simulate_result['affected_rows']}")
print(f"Columns Affected: {len(simulate_result['affected_columns'])}")
print(f"Risk Level: {simulate_result['risk_assessment']}")

print("\n=== COLUMNS BEING MASKED ===")
for col in simulate_result['affected_columns']:
    print(f"  - {col}")

print("\n=== PII FINDINGS ===")
print(f"Total PII columns found: {len(analyze_result['pii_findings'])}")
for finding in analyze_result['pii_findings']:
    print(f"  - {finding['table']}.{finding['column']} → {finding['pii_types']}")

print("\n✅ Expected Display:")
print(f"   Rows Affected: {simulate_result['affected_rows']} (total rows in affected tables)")
print(f"   Columns Affected: {len(simulate_result['affected_columns'])} (PII columns being masked)")

print("\n" + "="*60)
print("If the web UI shows 0 for both, the issue is in data passing")
print("If it shows correct values, the fix worked!")
print("="*60)
