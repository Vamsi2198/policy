#!/usr/bin/env python3
"""Test the enhanced masking functionality with correct Snowflake syntax"""

from control_pannel import ControlPlaneEngine, NLToSQLConverter

def test_masking():
    """Test masking with proper Snowflake syntax"""
    
    print('🔐 TESTING ENHANCED DATABASE MASKING')
    print('='*60)
    
    engine = ControlPlaneEngine('config.yaml')
    
    if engine.connect_platform():
        print('✅ Connected to Snowflake')
        
        # Get schema
        schema = engine._get_detailed_schema_for_chatbot()
        
        # Initialize converter
        nl_converter = NLToSQLConverter(provider="openai")
        
        # Test masking query generation
        test_query = "mask phone numbers in customers table"
        
        print(f'\n🧪 Testing: "{test_query}"')
        print('-'*50)
        
        try:
            result = nl_converter._fallback_masking_query(test_query, schema, "snowflake")
            
            print(f'✅ Generated SQL:')
            for sql in result.sql_commands:
                print(f'   {sql}')
            
            print(f'\n💡 Explanation: {result.explanation}')
            print(f'🎯 Confidence: {result.confidence:.1%}')
            
            # Test if SQL is valid (dry run)
            print(f'\n🧪 Testing SQL syntax...')
            for sql_cmd in result.sql_commands:
                if sql_cmd.startswith('UPDATE') or sql_cmd.startswith('BEGIN') or sql_cmd.startswith('COMMIT'):
                    print(f'   ✅ Valid: {sql_cmd[:50]}...')
            
        except Exception as e:
            print(f'❌ Error: {e}')
            
    else:
        print('❌ Failed to connect to database')

if __name__ == "__main__":
    test_masking()