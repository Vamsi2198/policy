#!/usr/bin/env python3
"""
Test GDPR Delete Fix
Quick test to verify the convert_for_general_sql method works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from control_pannel import NLToSQLConverter

def test_gdpr_delete():
    """Test GDPR delete functionality"""
    
    print("🧪 TESTING GDPR DELETE FIX")
    print("=" * 50)
    
    # Initialize converter
    converter = NLToSQLConverter(provider="openai")
    
    # Mock schema
    schema = {
        'PUBLIC.CUSTOMERS': {
            'columns': [
                {'name': 'ID', 'type': 'NUMBER'},
                {'name': 'FIRST_NAME', 'type': 'VARCHAR'},
                {'name': 'EMAIL', 'type': 'VARCHAR'}
            ]
        }
    }
    
    # Test query
    test_query = "Implement GDPR right to be forgotten across all systems"
    
    print(f"📝 Test Query: '{test_query}'")
    print("\n🔍 Testing method existence...")
    
    # Check if method exists
    if hasattr(converter, 'convert_for_general_sql'):
        print("✅ convert_for_general_sql method found!")
        
        try:
            result = converter.convert_for_general_sql(
                test_query, 
                schema, 
                platform="snowflake", 
                operation_type="DELETE"
            )
            
            print(f"✅ Method executed successfully!")
            print(f"📊 Result type: {type(result)}")
            print(f"🎯 Confidence: {result.confidence}")
            print(f"📝 SQL Commands: {len(result.sql_commands)}")
            
            if result.sql_commands:
                print(f"\n💻 Generated SQL:")
                for sql in result.sql_commands[:3]:  # Show first 3
                    print(f"  {sql}")
                
        except Exception as e:
            print(f"❌ Method execution failed: {e}")
            
    else:
        print("❌ convert_for_general_sql method NOT found!")
        print("🔍 Available methods:")
        for method in dir(converter):
            if method.startswith('convert_'):
                print(f"  - {method}")
    
    print("\n🎉 GDPR DELETE TEST COMPLETED!")
    print("=" * 50)

if __name__ == "__main__":
    test_gdpr_delete()