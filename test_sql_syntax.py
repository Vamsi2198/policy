#!/usr/bin/env python3
"""Test SQL syntax generation after fixes"""

import sys
sys.path.insert(0, 'src')

from ai_control_plane import AtlanActionsEngine

# Create engine
engine = AtlanActionsEngine(execution_mode="direct", nl_mode="local")

# Test the masking SQL generation
print("=" * 80)
print("Testing SQL Generation with Fixes")
print("=" * 80)

# Test 1: Basic masking SQL
print("\n[Test 1] _generate_masking_sql() - SSN masking")
sql_commands = engine._generate_masking_sql(
    table="HEALTH_RECORDS",
    column="SSN",
    policy_name="HEALTH_RECORDS_SSN_mask_policy",
    pii_types=["SSN"]
)

print("Generated SQL commands:")
for i, cmd in enumerate(sql_commands, 1):
    print(f"  {i}. {cmd}")

# Check for invalid syntax
print("\n[Validation] Checking for 'IF EXISTS' in SET MASKING POLICY clause...")
invalid_syntax = [cmd for cmd in sql_commands if "SET MASKING POLICY IF EXISTS" in cmd]
if invalid_syntax:
    print(f"  ❌ FOUND INVALID SYNTAX: {invalid_syntax}")
else:
    print(f"  ✅ NO INVALID SYNTAX FOUND")

# Check for correct ALTER syntax
print("\n[Validation] Checking for correct 'ALTER COLUMN ... SET MASKING POLICY' syntax...")
valid_set_policy = [cmd for cmd in sql_commands if "ALTER COLUMN" in cmd and "SET MASKING POLICY" in cmd]
if valid_set_policy:
    for cmd in valid_set_policy:
        if "IF EXISTS" not in cmd:
            print(f"  ✅ VALID: {cmd}")
        else:
            print(f"  ❌ INVALID: {cmd}")
else:
    print(f"  ⚠️  No SET MASKING POLICY commands found")

print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)
