#!/usr/bin/env python3
"""Test the enhanced chatbot functionality with sample queries"""

from control_pannel import ControlPlaneEngine, NLToSQLConverter

def test_chatbot_queries():
    """Test the chatbot with various sample queries"""
    
    # Initialize engine and connect
    print('🤖 INITIALIZING DATA CHATBOT TEST...')
    print('='*60)
    
    engine = ControlPlaneEngine('config.yaml')
    
    if not engine.connect_platform():
        print("❌ Failed to connect to platform")
        return
    
    print("✅ Connected to database successfully!")
    
    # Get schema information
    print('\n📊 DISCOVERING DATABASE SCHEMA...')
    schema = engine._get_detailed_schema_for_chatbot()
    
    print(f'✅ Found {len(schema)} table(s):')
    for table_name, table_info in schema.items():
        print(f'  📋 {table_name}: {len(table_info["columns"])} columns, {table_info["row_count"]} rows')
        for col in table_info['columns']:
            nullable = " [nullable]" if col.get('nullable') else ""
            print(f'      • {col["name"]} ({col["type"]}){nullable}')
        print()
    
    # Initialize NL converter
    nl_converter = NLToSQLConverter(provider="openai")
    
    # Test queries
    test_queries = [
        "Show me all employees",
        "What departments do we have?", 
        "Who are the highest paid employees?",
        "Count employees by department",
        "Show me employees with salary greater than 70000",
        "What is the average salary?"
    ]
    
    print('🧪 TESTING NATURAL LANGUAGE QUERIES...')
    print('='*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f'\n📝 TEST {i}: "{query}"')
        print('-'*50)
        
        try:
            # Convert to SQL
            result = nl_converter.convert_for_data_query(
                query, 
                schema, 
                platform="snowflake"
            )
            
            print(f'✅ Confidence: {result.confidence:.1%}')
            print(f'📄 Generated SQL:')
            for sql_cmd in result.sql_commands:
                print(f'   {sql_cmd}')
            
            if result.explanation:
                print(f'💡 Explanation: {result.explanation}')
            
            # Execute if confidence is good
            if result.sql_commands and result.confidence > 0.5:
                try:
                    sql_to_execute = result.sql_commands[0]
                    
                    # Safety check - only SELECT queries
                    if sql_to_execute.strip().upper().startswith('SELECT'):
                        print(f'\n🚀 Executing query...')
                        query_result = engine.connector.execute(sql_to_execute)
                        
                        if query_result:
                            print(f'📊 Results ({len(query_result)} rows):')
                            
                            # Show first 5 results
                            display_rows = query_result[:5]
                            for j, row in enumerate(display_rows, 1):
                                print(f'   {j}. {row}')
                            
                            if len(query_result) > 5:
                                print(f'   ... and {len(query_result) - 5} more rows')
                        else:
                            print('✅ Query executed (no results)')
                    else:
                        print('⚠️ Non-SELECT query - skipped for safety')
                        
                except Exception as e:
                    print(f'❌ Execution error: {e}')
            else:
                print('⚠️ Confidence too low for execution')
                
        except Exception as e:
            print(f'❌ Query processing error: {e}')
    
    print('\n🎉 CHATBOT TEST COMPLETED!')
    print('='*60)

if __name__ == "__main__":
    test_chatbot_queries()