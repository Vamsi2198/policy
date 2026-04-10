"""
Simple test to check current masking state and execute unmask
"""

import snowflake.connector
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

platform = config['platform']

print("="*80)
print("UNMASK TEST - Checking Current State")
print("="*80)

# Connect to Snowflake
conn = snowflake.connector.connect(
    account=platform['account'],
    user=platform['user'],
    password=platform['password'],
    warehouse=platform['warehouse'],
    database=platform['database'],
    schema=platform['schema'],
    role=platform['role']
)

cursor = conn.cursor()

# Step 1: Show all masking policies
print("\n1. EXISTING MASKING POLICIES:")
cursor.execute("SHOW MASKING POLICIES")
policies = cursor.fetchall()
print(f"   Found {len(policies)} policies:")
for policy in policies:
    print(f"   - {policy[1]}")

# Step 2: Show masked columns
print("\n2. COLUMNS WITH MASKING APPLIED:")
cursor.execute("""
    SELECT TABLE_NAME, COLUMN_NAME, MASKING_POLICY_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'PUBLIC'
    AND TABLE_NAME = 'CUSTOMERS'
    AND MASKING_POLICY_NAME IS NOT NULL
""")
masked_columns = cursor.fetchall()
print(f"   Found {len(masked_columns)} masked columns:")
for row in masked_columns:
    print(f"   - {row[0]}.{row[1]} → {row[2]}")

# Step 3: Unmask all columns
if masked_columns:
    print("\n3. UNMASKING COLUMNS:")
    policies_to_drop = set()
    
    for table_name, column_name, policy_name in masked_columns:
        try:
            sql = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} UNSET MASKING POLICY"
            print(f"\n   Executing: {sql}")
            cursor.execute(sql)
            print(f"   ✅ SUCCESS - Unmasked {table_name}.{column_name}")
            policies_to_drop.add(policy_name)
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
    
    # Step 4: Drop policies
    print("\n4. DROPPING MASKING POLICIES:")
    for policy_name in policies_to_drop:
        try:
            sql = f"DROP MASKING POLICY IF EXISTS {policy_name}"
            print(f"\n   Executing: {sql}")
            cursor.execute(sql)
            print(f"   ✅ SUCCESS - Dropped {policy_name}")
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
    
    # Step 5: Verify
    print("\n5. VERIFICATION:")
    cursor.execute("SHOW MASKING POLICIES")
    remaining_policies = cursor.fetchall()
    print(f"   Remaining policies: {len(remaining_policies)}")
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'PUBLIC'
        AND TABLE_NAME = 'CUSTOMERS'
        AND MASKING_POLICY_NAME IS NOT NULL
    """)
    remaining_masked = cursor.fetchone()[0]
    print(f"   Remaining masked columns: {remaining_masked}")
    
    if remaining_policies == 0 and remaining_masked == 0:
        print("\n✅ UNMASK COMPLETE - All policies removed!")
    else:
        print("\n⚠️  UNMASK INCOMPLETE - Some policies remain")
else:
    print("\n⚠️  No masked columns found - nothing to unmask")

cursor.close()
conn.close()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
