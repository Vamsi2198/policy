#!/usr/bin/env python3
"""
Test script to verify Snowflake query logging functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from control_pannel import ControlPlaneEngine
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_query_logging():
    """Test the query logging functionality"""
    print("\n" + "="*80)
    print("🧪 Testing Snowflake Query Logging")
    print("="*80 + "\n")
    
    try:
        # Initialize the engine
        print("1. Initializing Control Plane Engine...")
        engine = ControlPlaneEngine('config.yaml')
        
        print("2. Testing successful SELECT query...")
        try:
            result = engine.connector.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_ROLE()")
            print(f"   ✅ Query executed successfully, got {len(result)} rows")
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
        
        print("\n3. Testing successful SHOW query...")
        try:
            result = engine.connector.execute("SHOW TABLES IN SCHEMA PUBLIC")
            print(f"   ✅ Query executed successfully")
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
        
        print("\n4. Testing intentional failure (invalid query)...")
        try:
            result = engine.connector.execute("SELECT * FROM NON_EXISTENT_TABLE_12345")
            print(f"   ❌ Query should have failed but didn't!")
        except Exception as e:
            print(f"   ✅ Query failed as expected: {type(e).__name__}")
        
        print("\n5. Testing DDL query (if permissions allow)...")
        try:
            # Try to show masking policies
            result = engine.connector.execute("SHOW MASKING POLICIES")
            print(f"   ✅ Query executed successfully")
        except Exception as e:
            print(f"   ⚠️  Query failed (may be permissions): {type(e).__name__}")
        
        print("\n" + "="*80)
        print("✅ Logging Test Complete!")
        print("="*80)
        print("\n📝 Check the following files:")
        print("   - snowflake_queries.log (detailed query logs)")
        print("\n🔍 View logs with:")
        print("   python src/view_snowflake_logs.py")
        print("   python src/view_snowflake_logs.py --summary-only")
        print("   python src/view_snowflake_logs.py --status FAILED --errors")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_query_logging()
