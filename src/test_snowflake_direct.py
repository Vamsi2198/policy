#!/usr/bin/env python3
"""
Direct Snowflake Connection Test
Test if we can connect and query CUSTOMERS table
"""

import snowflake.connector
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

platform_config = config['platform']

print("=" * 60)
print("🔍 SNOWFLAKE CONNECTION TEST")
print("=" * 60)

# Connection parameters
conn_params = {
    'account': platform_config['account'],
    'user': platform_config['user'],
    'password': platform_config['password'],
    'warehouse': platform_config.get('warehouse', 'COMPUTE_WH'),
    'database': platform_config.get('database'),
    'schema': platform_config.get('schema', 'PUBLIC'),
    'role': platform_config.get('role', 'ACCOUNTADMIN')
}

print(f"\n📊 Connection Parameters:")
print(f"   Account: {conn_params['account']}")
print(f"   User: {conn_params['user']}")
print(f"   Database: {conn_params['database']}")
print(f"   Schema: {conn_params['schema']}")
print(f"   Warehouse: {conn_params['warehouse']}")
print(f"   Role: {conn_params['role']}")

try:
    print(f"\n🔌 Connecting to Snowflake...")
    conn = snowflake.connector.connect(**conn_params)
    print(f"✅ Connected successfully!")
    
    cursor = conn.cursor()
    
    # Test 1: Check current database
    print(f"\n" + "=" * 60)
    print("TEST 1: Current Database")
    print("=" * 60)
    cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()")
    result = cursor.fetchone()
    print(f"   Database: {result[0]}")
    print(f"   Schema: {result[1]}")
    print(f"   Warehouse: {result[2]}")
    
    # Test 2: Check if CUSTOMERS table exists
    print(f"\n" + "=" * 60)
    print("TEST 2: Check CUSTOMERS Table Exists")
    print("=" * 60)
    cursor.execute("""
        SELECT TABLE_NAME, ROW_COUNT, BYTES 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_SCHEMA = 'PUBLIC' 
        AND TABLE_NAME = 'CUSTOMERS'
    """)
    table_info = cursor.fetchone()
    if table_info:
        print(f"✅ CUSTOMERS table found!")
        print(f"   Table: {table_info[0]}")
        print(f"   Row Count: {table_info[1]}")
        print(f"   Size (bytes): {table_info[2]}")
    else:
        print(f"❌ CUSTOMERS table NOT found!")
        # List all tables
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'PUBLIC'
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        print(f"\n📋 Available tables in PUBLIC schema:")
        for t in tables:
            print(f"   - {t[0]}.{t[1]}")
    
    # Test 3: Get column information
    print(f"\n" + "=" * 60)
    print("TEST 3: CUSTOMERS Table Columns")
    print("=" * 60)
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'PUBLIC' 
        AND TABLE_NAME = 'CUSTOMERS'
        ORDER BY ORDINAL_POSITION
    """)
    columns = cursor.fetchall()
    if columns:
        print(f"✅ Found {len(columns)} columns:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]} (Nullable: {col[2]})")
    else:
        print(f"❌ No columns found!")
    
    # Test 4: Query actual data
    print(f"\n" + "=" * 60)
    print("TEST 4: Query Data from CUSTOMERS")
    print("=" * 60)
    try:
        cursor.execute("SELECT * FROM SNOWFLAKE_LEARNING_DB.PUBLIC.CUSTOMERS LIMIT 5")
        rows = cursor.fetchall()
        
        if rows:
            print(f"✅ Successfully queried {len(rows)} rows!")
            
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            print(f"\n📋 Columns: {', '.join(column_names)}")
            
            print(f"\n📊 Sample Data:")
            for i, row in enumerate(rows, 1):
                print(f"\n   Row {i}:")
                for col_name, value in zip(column_names, row):
                    # Mask PII for display
                    if any(pii in col_name.upper() for pii in ['EMAIL', 'PHONE', 'SSN', 'NAME']):
                        value = '***MASKED***' if value else None
                    print(f"      {col_name}: {value}")
        else:
            print(f"⚠️ Table exists but has 0 rows!")
            
    except Exception as e:
        print(f"❌ Error querying data: {e}")
    
    # Test 5: Count total rows
    print(f"\n" + "=" * 60)
    print("TEST 5: Count Total Rows")
    print("=" * 60)
    try:
        cursor.execute("SELECT COUNT(*) FROM SNOWFLAKE_LEARNING_DB.PUBLIC.CUSTOMERS")
        count = cursor.fetchone()[0]
        print(f"✅ Total rows in CUSTOMERS table: {count}")
    except Exception as e:
        print(f"❌ Error counting rows: {e}")
    
    # Test 6: Check masking policies
    print(f"\n" + "=" * 60)
    print("TEST 6: Check Masking Policies")
    print("=" * 60)
    try:
        cursor.execute("SHOW MASKING POLICIES IN SCHEMA PUBLIC")
        policies = cursor.fetchall()
        if policies:
            print(f"✅ Found {len(policies)} masking policies:")
            for policy in policies:
                print(f"   - {policy[1]}")  # Policy name is usually in index 1
        else:
            print(f"⚠️ No masking policies found")
    except Exception as e:
        print(f"⚠️ Could not retrieve masking policies: {e}")
    
    cursor.close()
    conn.close()
    
    print(f"\n" + "=" * 60)
    print(f"✅ ALL TESTS COMPLETED!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ CONNECTION FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n")
