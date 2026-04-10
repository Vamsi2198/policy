#!/usr/bin/env python3
"""
Test fix for entity extraction and table sampling
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_entity_extraction():
    """Test the entity extraction logic"""
    print("🧪 Testing Entity Extraction Fix")
    print("=" * 40)
    
    # Simulate the entities that OpenAI is returning
    target_entities = ['PUBLIC.CUSTOMERS.SSN', 'PUBLIC.CUSTOMERS.EMAIL', 'PUBLIC.CUSTOMERS.PHONE']
    
    print(f"Input entities: {target_entities}")
    
    # Apply the fix logic
    unique_tables = set()
    for entity in target_entities[:5]:  # Limit to 5 entities
        if entity.count('.') >= 2:  # Format: SCHEMA.TABLE.COLUMN
            # Extract just SCHEMA.TABLE part
            parts = entity.split('.')
            table_name = f"{parts[0]}.{parts[1]}"
            unique_tables.add(table_name)
        elif entity.count('.') == 1:  # Format: SCHEMA.TABLE
            unique_tables.add(entity)
        else:  # Simple table name
            unique_tables.add(entity)
    
    print(f"Extracted tables: {list(unique_tables)}")
    
    # Test with different formats
    test_cases = [
        ['PUBLIC.CUSTOMERS.SSN', 'PUBLIC.CUSTOMERS.EMAIL'],  # Column references
        ['PUBLIC.CUSTOMERS', 'PUBLIC.ORDERS'],               # Table references  
        ['customers', 'orders'],                             # Simple names
        ['PUBLIC.CUSTOMERS.SSN', 'PUBLIC.ORDERS', 'employees'] # Mixed
    ]
    
    for i, entities in enumerate(test_cases, 1):
        print(f"\nTest {i}: {entities}")
        unique_tables = set()
        for entity in entities:
            if entity.count('.') >= 2:
                parts = entity.split('.')
                table_name = f"{parts[0]}.{parts[1]}"
                unique_tables.add(table_name)
            elif entity.count('.') == 1:
                unique_tables.add(entity)
            else:
                unique_tables.add(entity)
        print(f"  → {list(unique_tables)}")
    
    print(f"\n✅ Fix should resolve the 'Database PUBLIC does not exist' error")
    print(f"✅ Now sampling tables instead of trying to sample columns as tables")

if __name__ == "__main__":
    test_entity_extraction()