#!/usr/bin/env python3
"""
Test Enhanced GDPR Functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from control_pannel import NLToSQLConverter

def test_gdpr_scenarios():
    """Test various GDPR deletion scenarios"""
    
    print("🧪 TESTING ENHANCED GDPR DELETION")
    print("=" * 60)
    
    # Initialize converter
    converter = NLToSQLConverter(provider="openai")
    
    # Mock schema
    schema = {
        'PUBLIC.CUSTOMERS': {
            'columns': [
                {'name': 'ID', 'type': 'NUMBER'},
                {'name': 'FIRST_NAME', 'type': 'VARCHAR'},
                {'name': 'EMAIL', 'type': 'VARCHAR'},
                {'name': 'PHONE', 'type': 'VARCHAR'}
            ]
        },
        'PUBLIC.ORDERS': {
            'columns': [
                {'name': 'ID', 'type': 'NUMBER'}, 
                {'name': 'CUSTOMER_ID', 'type': 'NUMBER'},
                {'name': 'CUSTOMER_EMAIL', 'type': 'VARCHAR'}
            ]
        }
    }
    
    test_cases = [
        "Implement GDPR right to be forgotten across all systems",  # Generic - should ask for clarification
        "GDPR delete for john@example.com",  # Email identifier
        "Right to be forgotten for customer ID 12345",  # ID identifier  
        "Remove user with phone +1234567890",  # Phone identifier
        "Delete customer data for user@test.com"  # Another email test
    ]
    
    for i, test_query in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{test_query}'")
        print("-" * 50)
        
        try:
            result = converter.convert_for_general_sql(
                test_query, 
                schema, 
                platform="snowflake", 
                operation_type="DELETE"
            )
            
            print(f"🎯 Confidence: {result.confidence * 100:.1f}%")
            print(f"📊 SQL Commands: {len(result.sql_commands)}")
            
            if result.sql_commands:
                print("💻 Generated SQL:")
                for sql in result.sql_commands:
                    print(f"  {sql}")
            
            print(f"📝 Explanation: {result.explanation}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 GDPR TESTING COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    test_gdpr_scenarios()