#!/usr/bin/env python3
"""
Test Snowflake Connection
"""

import yaml
import json

print("=" * 70)
print("🔍 SNOWFLAKE CONNECTION TEST")
print("=" * 70)

# Load config
print("\n📋 Loading configuration...")
try:
    with open('config.yaml') as f:
        content = f.read().replace('```yaml', '').replace('```', '').strip()
        config = yaml.safe_load(content)
    
    print("✅ Config loaded")
    print(f"\n📊 Configuration Details:")
    print(f"   Platform Type: {config['platform']['type']}")
    print(f"   Account: {config['platform']['account']}")
    print(f"   User: {config['platform']['user']}")
    print(f"   Warehouse: {config['platform'].get('warehouse', 'NOT SET')}")
    print(f"   Database: {config['platform'].get('database', 'NOT SET')}")
    print(f"   Schema: {config['platform'].get('schema', 'NOT SET')}")
except Exception as e:
    print(f"❌ Error loading config: {e}")
    exit(1)

# Test Snowflake import
print("\n🔌 Testing Snowflake Connector Import...")
try:
    import snowflake.connector
    print(f"✅ Snowflake connector imported successfully")
    print(f"   Version: {snowflake.connector.__version__}")
except ImportError as e:
    print(f"❌ Snowflake connector not installed: {e}")
    print("\n   To fix, run:")
    print("   pip install snowflake-connector-python")
    exit(1)

# Test connection
print("\n🔐 Testing Snowflake Connection...")
try:
    from control_pannel import SnowflakeConnector
    
    conn = SnowflakeConnector(config['platform'])
    if conn.connect():
        print("✅ SNOWFLAKE CONNECTION SUCCESSFUL!")
        
        # Try to get tables
        print("\n📊 Fetching table list...")
        try:
            tables = conn.get_tables()
            print(f"✅ Found {len(tables)} tables in {config['platform']['database']}")
            print("\n📋 Sample tables:")
            for table in tables[:5]:
                print(f"   - {table['schema']}.{table['name']} ({table['rows']} rows)")
            
            if len(tables) > 5:
                print(f"   ... and {len(tables) - 5} more")
                
        except Exception as e:
            print(f"⚠️  Error fetching tables: {e}")
    else:
        print("❌ SNOWFLAKE CONNECTION FAILED")
        print("\n   Possible reasons:")
        print("   1. Invalid credentials (account, user, password)")
        print("   2. Warehouse not selected in Snowflake UI")
        print("   3. Database not selected in Snowflake UI")
        print("   4. Network connectivity issue")
        print("   5. Snowflake account doesn't exist")
        
except Exception as e:
    print(f"❌ Connection test failed: {e}")
    import traceback
    traceback.print_exc()
    
print("\n" + "=" * 70)
