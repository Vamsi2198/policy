"""
Test if schema correctly includes masking policy information
"""

import yaml
from ai_control_plane import AIControlPlane
from control_pannel import ControlPlaneEngine

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create engine and control plane
engine = ControlPlaneEngine(config)
control_plane = AIControlPlane(engine, config)

print("\n" + "="*80)
print("TESTING SCHEMA MASKING POLICY DETECTION")
print("="*80)

# Connect
print("\n1. Connecting to Snowflake...")
if engine.connect_platform():
    print("   ✅ Connected")
else:
    print("   ❌ Connection failed")
    exit(1)

# Build schema
print("\n2. Building schema context...")
schema = control_plane._build_schema_context()

# Check CUSTOMERS table
print("\n3. Checking CUSTOMERS table schema:")
customers_schema = schema.get('PUBLIC.CUSTOMERS')
if customers_schema:
    print(f"   Table found with {len(customers_schema.get('columns', []))} columns")
    print(f"   Row count: {customers_schema.get('row_count', 0)}")
    
    print("\n   Column Details:")
    for col in customers_schema.get('columns', []):
        name = col.get('name')
        col_type = col.get('type')
        policy = col.get('masking_policy_name')
        
        if policy:
            print(f"   ✅ {name:20s} ({col_type:15s}) → MASKED BY: {policy}")
        else:
            print(f"   ⚪ {name:20s} ({col_type:15s}) → No masking")
else:
    print("   ❌ CUSTOMERS table not found in schema")
    print(f"   Available tables: {list(schema.keys())}")

# Test masking policy query directly
print("\n4. Testing direct masking policy query...")
masking_info = control_plane._get_masking_policies_for_table('PUBLIC.CUSTOMERS')
if masking_info:
    print(f"   ✅ Found {len(masking_info)} masked columns:")
    for col, policy in masking_info.items():
        print(f"      - {col} → {policy}")
else:
    print("   ⚠️  No masking policies found (table might not be masked yet)")

# Test schema formatting for LLM
print("\n5. Testing schema formatting for OpenAI:")
if engine.nl_converter:
    formatted = engine.nl_converter._format_schema_context(schema)
    print("   Schema snippet for CUSTOMERS table:")
    lines = formatted.split('\n')
    in_customers = False
    for line in lines:
        if 'CUSTOMERS' in line:
            in_customers = True
        if in_customers:
            print(f"   {line}")
            if line.strip() == "" and in_customers:
                break
    
    # Check if MASKED BY appears
    if 'MASKED BY' in formatted:
        print("\n   ✅ Schema includes masking policy information")
    else:
        print("\n   ❌ Schema does NOT include masking policy information")
else:
    print("   ⚠️  No NL converter available")

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
print("\nNext step: If masking policies are shown, run unmask test")
print("Command: python test_unmask_intent.py")
print("="*80)
