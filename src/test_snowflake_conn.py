#!/usr/bin/env python3
"""Test Snowflake connection"""

import yaml
from control_pannel import SnowflakeConnector

# Load config
with open('config.yaml') as f:
    content = f.read().replace('```yaml', '').replace('```', '').strip()
    config = yaml.safe_load(content)

print('Testing Snowflake connection...')
print(f"Account: {config['platform']['account']}")
print(f"User: {config['platform']['user']}")
print(f"Warehouse: {config['platform']['warehouse']}")
print(f"Database: {config['platform']['database']}")
print(f"Schema: {config['platform']['schema']}")
print()

# Try to connect
conn = SnowflakeConnector(config['platform'])
if conn.connect():
    print('✅ CONNECTION SUCCESSFUL!')
    try:
        tables = conn.get_tables()
        print(f'Found {len(tables)} tables')
        for table in tables[:5]:
            print(f"  - {table['schema']}.{table['name']}")
    except Exception as e:
        print(f"Error getting tables: {e}")
else:
    print('❌ CONNECTION FAILED')
