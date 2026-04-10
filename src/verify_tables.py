#!/usr/bin/env python3
"""
Verify Snowflake Tables
"""

import yaml

print("=" * 70)
print("✅ VERIFYING SNOWFLAKE TABLES")
print("=" * 70)

# Load config
with open('../config.yaml') as f:
    config = yaml.safe_load(f)

from control_pannel import SnowflakeConnector
conn = SnowflakeConnector(config['platform'])

if conn.connect():
    print('\n✅ SNOWFLAKE CONNECTION SUCCESSFUL')
    
    # Query for tables in PUBLIC schema
    cursor = conn.connection.cursor()
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'PUBLIC'")
    tables = cursor.fetchall()
    
    print(f'\n📊 Tables in PUBLIC schema: {len(tables)}')
    for table in tables:
        print(f'   ✓ {table[0]}')
    
    # Get row counts
    print('\n📈 Row counts:')
    for table in tables:
        table_name = table[0]
        cursor.execute(f'SELECT COUNT(*) FROM PUBLIC.{table_name}')
        count = cursor.fetchone()[0]
        print(f'   {table_name}: {count} rows')
    
    cursor.close()
    conn.disconnect()
else:
    print('❌ Connection failed')
