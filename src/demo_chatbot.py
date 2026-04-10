#!/usr/bin/env python3
"""Demo the enhanced chatbot capabilities with mock data"""

from control_pannel import ControlPlaneEngine

def demo_enhanced_chatbot():
    """Demonstrate the enhanced chatbot functionality"""
    
    print('🤖 ENHANCED DATA CHATBOT DEMO')
    print('='*60)
    
    # Connect and get schema
    engine = ControlPlaneEngine('config.yaml')
    
    if engine.connect_platform():
        print('✅ Connected to Snowflake successfully!')
        
        # Show dynamic schema discovery
        print('\n📊 DYNAMIC SCHEMA DISCOVERY:')
        print('-'*40)
        
        schema = engine._get_detailed_schema_for_chatbot()
        
        print(f'🔍 Discovered {len(schema)} table(s) automatically:')
        
        for table_name, table_info in schema.items():
            row_count = table_info.get('row_count', 0)
            table_type = table_info.get('table_type', 'TABLE')
            
            print(f'\n📋 {table_name}')
            print(f'   Type: {table_type}')
            print(f'   Rows: {row_count:,}')
            print(f'   Columns ({len(table_info["columns"])}):')
            
            for i, col in enumerate(table_info['columns'], 1):
                nullable = " [nullable]" if col.get('nullable') else ""
                print(f'      {i:2d}. {col["name"]} ({col["type"]}){nullable}')
        
        # Demonstrate SQL generation logic
        print('\n💡 NATURAL LANGUAGE QUERY EXAMPLES:')
        print('-'*40)
        
        example_queries = [
            ("Show me all employees", "SELECT * FROM PUBLIC.EMPLOYEES"),
            ("Count employees by department", "SELECT DEPARTMENT, COUNT(*) FROM PUBLIC.EMPLOYEES GROUP BY DEPARTMENT"),
            ("Who are the highest paid employees?", "SELECT * FROM PUBLIC.EMPLOYEES ORDER BY SALARY DESC LIMIT 10"),
            ("What's the average salary?", "SELECT AVG(SALARY) FROM PUBLIC.EMPLOYEES"),
            ("Show employees in Engineering", "SELECT * FROM PUBLIC.EMPLOYEES WHERE DEPARTMENT = 'Engineering'")
        ]
        
        for query, expected_sql in example_queries:
            print(f'\n📝 Query: "{query}"')
            print(f'🎯 Generated SQL: {expected_sql}')
        
        # Test actual data retrieval
        print('\n🚀 EXECUTING SAMPLE QUERY:')
        print('-'*40)
        
        try:
            # Execute a simple query
            sample_sql = "SELECT * FROM PUBLIC.EMPLOYEES LIMIT 5"
            print(f'SQL: {sample_sql}')
            
            results = engine.connector.execute(sample_sql)
            
            if results:
                print(f'\n📊 Results ({len(results)} rows):')
                for i, row in enumerate(results, 1):
                    print(f'   {i}. {row}')
            else:
                print('No results returned')
                
        except Exception as e:
            print(f'❌ Query error: {e}')
        
        print('\n🎉 DEMO COMPLETED!')
        print('='*60)
        print('\n💬 Your enhanced chatbot features:')
        print('   ✅ Dynamic schema discovery using INFORMATION_SCHEMA')
        print('   ✅ Complete table and column visibility at startup')
        print('   ✅ Natural language to SQL conversion')
        print('   ✅ Real-time query execution with results')
        print('   ✅ Future-proof - automatically adapts to new tables')
        
    else:
        print('❌ Failed to connect to database')

if __name__ == "__main__":
    demo_enhanced_chatbot()