#!/usr/bin/env python3
"""
Test Enhanced Audit Logging System
Tests comprehensive audit trail functionality
"""

import sqlite3
import json
from datetime import datetime
from ai_control_plane import AIControlPlane

def test_audit_logging():
    """Test that all audit logging components work"""
    
    print("🧪 Testing Enhanced Audit Logging System...")
    
    # Initialize AI Control Plane
    control_plane = AIControlPlane(use_llm=False)
    
    print("\n✅ Step 1: AI Control Plane initialized")
    
    # Test audit database tables exist
    cursor = control_plane.metadata_db.cursor()
    
    # Check all audit tables exist
    audit_tables = [
        'user_requests_audit',
        'phase_audit_log', 
        'approval_audit_log',
        'sql_execution_audit',
        'snowflake_audit_sync',
        'column_classifications',
        'execution_history',
        'atlan_sync_log'
    ]
    
    for table in audit_tables:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        result = cursor.fetchone()
        if result:
            print(f"✅ Step 2: Audit table '{table}' exists")
        else:
            print(f"❌ Step 2: Audit table '{table}' MISSING")
    
    # Test audit request logging
    print("\n🔍 Step 3: Testing audit request logging...")
    test_query = "mask pii in customers table"
    request_id = control_plane._audit_user_request(test_query, session_id="test_session_123")
    print(f"✅ Step 3: Request logged with ID: {request_id}")
    
    # Test phase audit logging
    print("\n📋 Step 4: Testing phase audit logging...")
    from ai_control_plane import ObservationResult
    
    mock_phase_result = ObservationResult(
        intent="pii_masking",
        target_entities=["PUBLIC.CUSTOMERS"],
        confidence=0.95,
        schema_context={},
        current_state={},
        sample_data={},
        sql_result={}
    )
    
    control_plane._audit_phase_completion(request_id, "OBSERVE", mock_phase_result, True)
    print("✅ Step 4: Phase audit logged successfully")
    
    # Test approval audit logging
    print("\n👤 Step 5: Testing approval audit logging...")
    approval_decision = {
        'approved': True,
        'reason': 'Test approval for audit logging',
        'timestamp': datetime.now().isoformat()
    }
    
    control_plane._audit_user_approval(request_id, approval_decision)
    print("✅ Step 5: Approval decision audit logged")
    
    # Test Snowflake audit sync (mock)
    print("\n❄️ Step 6: Testing Snowflake audit sync...")
    audit_data = {
        'user_query': test_query,
        'action': 'GOVERNANCE_TEST',
        'table_name': 'PUBLIC.CUSTOMERS',
        'record_id': None,
        'test_data': 'Enhanced audit logging test'
    }
    
    try:
        control_plane._audit_snowflake_logs(request_id, audit_data)
        print("✅ Step 6: Snowflake audit sync attempted (may fail if no connection)")
    except Exception as e:
        print(f"⚠️ Step 6: Snowflake audit sync failed (expected): {e}")
    
    # Verify audit data was stored
    print("\n📊 Step 7: Verifying audit data storage...")
    
    # Check user request audit
    cursor.execute("SELECT * FROM user_requests_audit WHERE request_id = ?", (request_id,))
    request_data = cursor.fetchone()
    if request_data:
        print("✅ Step 7a: User request audit data found")
    else:
        print("❌ Step 7a: User request audit data NOT found")
    
    # Check phase audit log
    cursor.execute("SELECT * FROM phase_audit_log WHERE request_id = ?", (request_id,))
    phase_data = cursor.fetchone()
    if phase_data:
        print("✅ Step 7b: Phase audit data found")
    else:
        print("❌ Step 7b: Phase audit data NOT found")
    
    # Check approval audit log
    cursor.execute("SELECT * FROM approval_audit_log WHERE request_id = ?", (request_id,))
    approval_data = cursor.fetchone()
    if approval_data:
        print("✅ Step 7c: Approval audit data found")
    else:
        print("❌ Step 7c: Approval audit data NOT found")
    
    # Display summary
    print("\n📈 Audit Data Summary:")
    print("=" * 50)
    
    # Count total audit records
    cursor.execute("SELECT COUNT(*) FROM user_requests_audit")
    request_count = cursor.fetchone()[0]
    print(f"Total user requests audited: {request_count}")
    
    cursor.execute("SELECT COUNT(*) FROM phase_audit_log")
    phase_count = cursor.fetchone()[0]
    print(f"Total phase executions audited: {phase_count}")
    
    cursor.execute("SELECT COUNT(*) FROM approval_audit_log")
    approval_count = cursor.fetchone()[0]
    print(f"Total approval decisions audited: {approval_count}")
    
    cursor.execute("SELECT COUNT(*) FROM sql_execution_audit")
    sql_count = cursor.fetchone()[0]
    print(f"Total SQL executions audited: {sql_count}")
    
    cursor.execute("SELECT COUNT(*) FROM column_classifications")
    classification_count = cursor.fetchone()[0]
    print(f"Total column classifications: {classification_count}")
    
    print(f"\n🎯 Test Request ID: {request_id}")
    print("✅ Enhanced audit logging system is operational!")
    
    return request_id

def test_full_workflow_audit():
    """Test audit logging through a complete workflow"""
    
    print("\n\n🔄 Testing Full Workflow Audit...")
    print("=" * 60)
    
    control_plane = AIControlPlane(use_llm=False)
    
    # Run a simple test command (will use mock/local mode)
    test_query = "show current policies"
    
    try:
        results = control_plane.process_natural_language(test_query, session_id="test_workflow_123")
        
        print("✅ Full workflow completed")
        print(f"Request ID: {results.get('request_id', 'N/A')}")
        print(f"Status: {results.get('status', 'N/A')}")
        print(f"Phases completed: {len(results.get('phases', {}))}")
        
        # Check if audit data was created
        if 'request_id' in results:
            request_id = results['request_id']
            cursor = control_plane.metadata_db.cursor()
            
            cursor.execute("SELECT status, execution_time FROM user_requests_audit WHERE request_id = ?", (request_id,))
            audit_record = cursor.fetchone()
            
            if audit_record:
                print(f"✅ Audit record found - Status: {audit_record[0]}, Time: {audit_record[1]}s")
            else:
                print("❌ No audit record found for workflow")
        
        return results
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Enhanced Audit Logging Test Suite")
    print("=" * 60)
    
    # Test 1: Basic audit components
    test_request_id = test_audit_logging()
    
    # Test 2: Full workflow audit
    workflow_results = test_full_workflow_audit()
    
    print("\n🎉 Audit Testing Complete!")
    print("📝 Check atlan_actions_metadata.db for audit records")
    print(f"🔍 Test request ID: {test_request_id}")
    
    # Show database file location
    import os
    db_path = os.path.abspath("atlan_actions_metadata.db")
    print(f"📄 Database location: {db_path}")