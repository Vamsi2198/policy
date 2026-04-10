#!/usr/bin/env python3
"""Test script to verify dynamic schema discovery is working"""

from control_pannel import ControlPlaneEngine

# Create engine with config file path
print('📊 Testing Dynamic Schema Discovery...')
engine = ControlPlaneEngine('config.yaml')

# Connect to the platform
print('🔌 Connecting to database...')
if engine.connect_platform():
    print('✅ Connected successfully!')
    
    # Test dynamic schema discovery
    schema = engine._get_detailed_schema_for_chatbot()
    
    print(f'\n🔍 Found {len(schema)} tables:')
    for table, info in schema.items():
        print(f'  📋 {table}: {len(info["columns"])} columns, {info["row_count"]} rows')
        print(f'      Type: {info.get("table_type", "TABLE")}')
        for col in info['columns'][:3]:  # Show first 3 columns
            print(f'        - {col["name"]} ({col["type"]})')
        if len(info['columns']) > 3:
            print(f'        ... and {len(info["columns"]) - 3} more columns')
        print()
else:
    print('❌ Failed to connect to database')