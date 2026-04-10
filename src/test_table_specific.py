#!/usr/bin/env python3
"""Test table-specific masking functionality"""

from control_pannel import NLToSQLConverter

def test_table_specific_masking():
    """Test if masking now correctly targets specific tables/columns"""
    
    print('🧪 TESTING TABLE-SPECIFIC MASKING')
    print('='*60)
    
    # Mock schema
    mock_schema = {
        'PUBLIC.ORDERS': {
            'columns': [
                {'name': 'ID', 'type': 'NUMBER'},
                {'name': 'TOTAL_AMOUNT', 'type': 'NUMBER'},
                {'name': 'STATUS', 'type': 'TEXT'}
            ]
        },
        'PUBLIC.CUSTOMERS': {
            'columns': [
                {'name': 'ID', 'type': 'NUMBER'},
                {'name': 'PHONE', 'type': 'TEXT'},
                {'name': 'EMAIL', 'type': 'TEXT'}
            ]
        }
    }
    
    converter = NLToSQLConverter(provider="openai")
    
    test_queries = [
        "mask total_amount in ORDERS table",
        "hide phone numbers in CUSTOMERS table", 
        "mask salary in EMPLOYEES table",
        "anonymize credit card in TRANSACTIONS table"
    ]
    
    for query in test_queries:
        print(f'\n📝 Query: "{query}"')
        print('-'*50)
        
        try:
            # Test fallback logic (which should be table-specific now)
            result = converter._fallback_masking_query(query, mock_schema, "snowflake")
            
            print(f'✅ Generated SQL:')
            for sql in result.sql_commands:
                print(f'   {sql}')
            
            print(f'\n💡 Explanation: {result.explanation}')
            print(f'🎯 Confidence: {result.confidence:.1%}')
            
            # Check if it targets the right table
            sql_text = ' '.join(result.sql_commands).upper()
            if 'ORDERS' in query.upper() and 'PUBLIC.ORDERS' in sql_text:
                print(f'✅ CORRECT: Targets ORDERS table as requested')
            elif 'CUSTOMERS' in query.upper() and 'PUBLIC.CUSTOMERS' in sql_text:
                print(f'✅ CORRECT: Targets CUSTOMERS table as requested')
            elif 'EMPLOYEES' in query.upper() and 'PUBLIC.EMPLOYEES' in sql_text:
                print(f'✅ CORRECT: Targets EMPLOYEES table as requested')
            elif 'TRANSACTIONS' in query.upper() and 'PUBLIC.TRANSACTIONS' in sql_text:
                print(f'✅ CORRECT: Targets TRANSACTIONS table as requested')
            else:
                print(f'⚠️  Check: Review if correct table is targeted')
            
        except Exception as e:
            print(f'❌ Error: {e}')
    
    print(f'\n🎉 Table-specific masking test completed!')

if __name__ == "__main__":
    test_table_specific_masking()