#!/usr/bin/env python3
"""
Test Snowflake Connection
"""

import os
import yaml
import json

print("=" * 70)
print("🔍 SNOWFLAKE CONNECTION TEST")
print("=" * 70)


def find_config_path() -> str:
    env_path = os.getenv('CONFIG_PATH')
    candidates = []
    if env_path:
        candidates.append(env_path)

    candidates.extend([
        'config.yaml',
        os.path.join(os.path.dirname(__file__), 'config.yaml'),
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.yaml')),
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'config.yaml')),
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')),
    ])

    seen = set()
    for candidate in candidates:
        candidate = os.path.abspath(candidate)
        if candidate in seen:
            continue
        seen.add(candidate)
        if os.path.exists(candidate):
            return candidate
    return ''


config_path = find_config_path()
print("\n📋 Loading configuration...")
if not config_path:
    print("❌ No config.yaml found in expected locations.")
    print("   Please create config.yaml in one of these directories:")
    print(f"     - {os.getcwd()}")
    print(f"     - {os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}")
    print(f"     - {os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))}")
    exit(1)

try:
    with open(config_path, 'r') as f:
        content = f.read().replace('```yaml', '').replace('```', '').strip()
        config = yaml.safe_load(content) or {}

    print(f"✅ Config loaded from: {config_path}")
    platform_cfg = config.get('platform', {})
    print(f"\n📊 Configuration Details:")
    print(f"   Platform Type: {platform_cfg.get('type', 'NOT SET')}")
    print(f"   Account: {platform_cfg.get('account', 'NOT SET')}")
    print(f"   User: {platform_cfg.get('user', 'NOT SET')}")
    print(f"   Warehouse: {platform_cfg.get('warehouse', 'NOT SET')}")
    print(f"   Database: {platform_cfg.get('database', 'NOT SET')}")
    print(f"   Schema: {platform_cfg.get('schema', 'NOT SET')}")
except Exception as e:
    print(f"❌ Error loading config: {e}")
    exit(1)

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

print("\n🔐 Testing Snowflake Connection...")
try:
    from control_pannel import SnowflakeConnector

    conn = SnowflakeConnector(platform_cfg)
    if conn.connect():
        print("✅ SNOWFLAKE CONNECTION SUCCESSFUL!")

        print("\n📊 Fetching table list...")
        try:
            tables = conn.get_tables()
            print(f"✅ Found {len(tables)} tables in {platform_cfg.get('database', 'UNKNOWN')}")
            print("\n📋 Sample tables:")
            for table in tables[:5]:
                print(f"   - {table.get('schema')}.", end='')
                print(f"{table.get('name')} ({table.get('rows', 'N/A')} rows)")

            if len(tables) > 5:
                print(f"   ... and {len(tables) - 5} more")
        except Exception as e:
            print(f"⚠️  Error fetching tables: {e}")
    else:
        print("❌ SNOWFLAKE CONNECTION FAILED")
        print("\n   Possible reasons:")
        print("   1. Invalid credentials (account, user, password)")
        print("   2. Warehouse or role not configured correctly")
        print("   3. Database/schema not accessible")
        print("   4. Network connectivity issues")
except Exception as e:
    print(f"❌ Connection test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
