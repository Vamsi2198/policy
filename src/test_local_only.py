#!/usr/bin/env python3
"""
Test AI Control Plane in PURE LOCAL mode (no external connections)
This test validates the core functionality without Snowflake or API calls.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_control_plane import AIControlPlane
import json

def mock_snowflake_connection():
    """Mock successful Snowflake connection"""
    return True

def test_pure_local_flow():
    """Test the AI Control Plane in pure local mode"""
    print("=" * 60)
    print("🚀 Testing AI Control Plane - PURE LOCAL MODE")
    print("=" * 60)
    
    # Create temporary config file for testing
    test_config_content = """
# Test configuration for local-only mode
snowflake:
  account: "test-account"
  user: "test-user" 
  password: "test-password"
  warehouse: "TEST_WH"
  database: "TEST_DB"
  schema: "TEST_SCHEMA"

governance:
  auto_approve: true
  enable_pii_detection: true
  enable_audit_logging: false  # Disable for local testing
"""
    
    config_file = "test_local_config.yaml"
    
    try:
        # Write test config
        with open(config_file, 'w') as f:
            f.write(test_config_content)
        
        # Initialize AI Control Plane with config file
        control_plane = AIControlPlane(config_file, use_llm=False)
        print("✅ AI Control Plane initialized in Pure Local mode")
        
        # Mock the engine connection and connector to avoid actual Snowflake calls
        original_connect = control_plane.engine.connect_platform
        control_plane.engine.connect_platform = mock_snowflake_connection
        
        # Create a mock connector with get_tables method
        class MockConnector:
            def get_tables(self):
                return [
                    {"name": "EMPLOYEES", "schema": "PUBLIC", "type": "TABLE"},
                    {"name": "CUSTOMERS", "schema": "PUBLIC", "type": "TABLE"},
                    {"name": "ORDERS", "schema": "PUBLIC", "type": "TABLE"}
                ]
            def get_columns(self, table):
                if table == "EMPLOYEES":
                    return [
                        {"name": "ID", "type": "NUMBER", "nullable": False},
                        {"name": "NAME", "type": "VARCHAR", "nullable": True},
                        {"name": "EMAIL", "type": "VARCHAR", "nullable": True},
                        {"name": "PHONE", "type": "VARCHAR", "nullable": True},
                        {"name": "SSN", "type": "VARCHAR", "nullable": True}
                    ]
                return [
                    {"name": "ID", "type": "NUMBER", "nullable": False},
                    {"name": "NAME", "type": "VARCHAR", "nullable": True},
                    {"name": "CREATED_DATE", "type": "TIMESTAMP", "nullable": True}
                ]
                
        control_plane.engine.connector = MockConnector()
        
        # Test query
        test_query = "mask NAME column in EMPLOYEES table"
        print(f"\n📝 Processing query: '{test_query}'")
        
        # Process the natural language query
        print("\n🔄 Starting 6-phase AI Control Plane execution...")
        
        # Override the audit storage to avoid Snowflake calls
        original_audit_method = control_plane._store_complete_audit_to_snowflake
        def mock_audit_storage(query, results):
            print("📊 Audit stored locally (Snowflake disabled)")
            return True
        control_plane._store_complete_audit_to_snowflake = mock_audit_storage
        
        # Execute the control plane
        results = control_plane.process_natural_language(test_query)
        
        print("\n" + "=" * 60)
        print("📋 EXECUTION RESULTS")
        print("=" * 60)
        
        if results:
            print(f"✅ Success: {results.get('success', False)}")
            print(f"📊 Phases completed: {len(results.get('phases', []))}")
            
            # Show each phase result
            for phase_name, phase_result in results.get('phases', {}).items():
                print(f"\n🔸 {phase_name}:")
                if isinstance(phase_result, dict):
                    for key, value in phase_result.items():
                        if key != 'raw_data':  # Skip large data dumps
                            print(f"   {key}: {value}")
                else:
                    print(f"   Result: {phase_result}")
            
            # Show final SQL if generated
            if 'final_sql' in results:
                print(f"\n💾 Generated SQL:")
                print(f"   {results['final_sql']}")
            
            # Show PII detection
            if 'pii_detected' in results:
                print(f"\n🔍 PII Detection:")
                print(f"   Columns: {results.get('pii_columns', [])}")
                print(f"   Types: {results.get('pii_types', [])}")
        
        else:
            print("❌ No results returned")
        
        print("\n" + "=" * 60)
        print("🎯 LOCAL MODE TEST COMPLETED")
        print("=" * 60)
        
        # Restore original methods
        control_plane.engine.connect_platform = original_connect
        control_plane._store_complete_audit_to_snowflake = original_audit_method
        
        # Clean up test config file
        if os.path.exists(config_file):
            os.remove(config_file)
        
        return results
        
    except Exception as e:
        print(f"❌ Error during local testing: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Clean up test config file
        if os.path.exists(config_file):
            os.remove(config_file)
        return None

def test_local_sql_generation():
    """Test local SQL generation capabilities"""
    print("\n" + "=" * 40)
    print("🧪 Testing Local SQL Generation")
    print("=" * 40)
    
    # Create temporary config for this test too
    test_config_content = """
snowflake:
  account: "test-account"
  user: "test-user" 
  password: "test-password"
  warehouse: "TEST_WH"
  database: "TEST_DB"
  schema: "TEST_SCHEMA"
"""
    
    config_file = "test_sql_config.yaml"
    
    try:
        with open(config_file, 'w') as f:
            f.write(test_config_content)
            
        control_plane = AIControlPlane(config_file, use_llm=False)
        
        test_queries = [
            "mask NAME column in EMPLOYEES table",
            "show all tables",
            "create masking policy for email addresses",
            "drop policy EMAIL_MASK"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            try:
                # Extract intent and entities for proper method call
                intent = control_plane._extract_intent(query)
                entities = control_plane._extract_entities(query)
                confidence = 0.8  # Default confidence for testing
                
                # Test local pattern matching
                sql_result = control_plane._create_fallback_sql_result(intent, entities, confidence)
                print(f"✅ Intent: {intent}")
                print(f"📝 Entities: {entities}")
                print(f"🎯 Confidence: {confidence}")
                print(f"� Policy Type: {sql_result.policy_type}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error in SQL generation test: {str(e)}")
    finally:
        # Clean up config file
        if os.path.exists(config_file):
            os.remove(config_file)

if __name__ == "__main__":
    print("Starting PURE LOCAL testing (no external dependencies)...")
    
    # Test 1: Full local flow
    results = test_pure_local_flow()
    
    # Test 2: SQL generation
    test_local_sql_generation()
    
    print("\n🏁 All local tests completed!")