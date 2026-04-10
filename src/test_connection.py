#!/usr/bin/env python3
"""
Test Snowflake Connection Directly
"""
import snowflake.connector
import yaml

# Load config
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

platform_config = config['platform']

print("🔍 Testing Snowflake Connection...")
print(f"Account: {platform_config['account']}")
print(f"User: {platform_config['user']}")
print(f"Database: {platform_config.get('database')}")

try:
    connection = snowflake.connector.connect(
        account=platform_config['account'],
        user=platform_config['user'],
        password=platform_config['password'],
        warehouse=platform_config.get('warehouse', 'COMPUTE_WH'),
        database=platform_config.get('database'),
        schema=platform_config.get('schema', 'PUBLIC')
    )
    
    print("✅ Connection successful!")
    
    # Test a simple query
    cursor = connection.cursor()
    cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()")
    result = cursor.fetchone()
    print(f"Database: {result[0]}")
    print(f"Schema: {result[1]}")
    print(f"Warehouse: {result[2]}")
    
    # Test table listing
    cursor.execute("""
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'PUBLIC'
        LIMIT 5
    """)
    tables = cursor.fetchall()
    print(f"Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]} ({table[1]})")
    
    connection.close()
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()