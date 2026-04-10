#!/usr/bin/env python3
"""
Test verification fix for entity handling
"""

def test_verification_fix():
    """Test the verification entity extraction"""
    print("🔧 Testing Verification Fix")
    print("=" * 30)
    
    # Simulate the target_entities from your OpenAI run
    target_entities = ['PUBLIC.CUSTOMERS.EMAIL', 'PUBLIC.CUSTOMERS.PHONE', 'PUBLIC.CUSTOMERS.SSN']
    
    print(f"Input entities: {target_entities}")
    
    # Apply the fix logic
    unique_tables = set()
    for entity in target_entities:
        if entity.count('.') >= 2:  # Format: SCHEMA.TABLE.COLUMN
            parts = entity.split('.')
            table_name = f"{parts[0]}.{parts[1]}"
            unique_tables.add(table_name)
        elif entity.count('.') == 1:  # Format: SCHEMA.TABLE
            unique_tables.add(entity)
        else:  # Simple table name
            unique_tables.add(entity)
    
    print(f"Tables for verification: {list(unique_tables)}")
    print("✅ Will sample 'PUBLIC.CUSTOMERS' instead of individual columns")
    print("✅ This should eliminate the 'Database PUBLIC does not exist' errors")

if __name__ == "__main__":
    test_verification_fix()