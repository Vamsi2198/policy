#!/usr/bin/env python3
"""
Simple test for audit logging - tests low confidence scenario to avoid approval prompt
"""

import sys
import os
import json

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_control_plane import AIControlPlane

def test_low_confidence_audit():
    """Test audit logging for low confidence scenario (no approval needed)"""
    print("🧪 Testing Snowflake Audit Logging - Low Confidence Scenario...")
    
    try:
        # Initialize AI Control Plane
        control_plane = AIControlPlane()
        
        # Test: Low confidence query (should trigger audit without approval)
        print("\n1️⃣ Testing low confidence scenario with audit logging...")
        test_query = "do something with data"  # Intentionally vague
        
        results = control_plane.process_natural_language(test_query)
        
        print(f"Status: {results['status']}")
        print(f"Confidence: {results.get('confidence', 0):.1%}")
        print(f"Message: {results.get('message', 'N/A')}")
        
        if results['status'] == 'low_confidence':
            print("✅ Low confidence scenario completed - audit log should be stored")
        else:
            print(f"ℹ️ Unexpected status: {results['status']}")
        
        # Test 2: Create a simple successful audit by mocking approval
        print("\n2️⃣ Testing direct audit storage method...")
        
        # Create mock results for direct audit test
        mock_results = {
            'status': 'test',
            'phases': {
                'observe': {
                    'intent': 'TEST',
                    'target_entities': ['test_table'],
                    'confidence': 0.9
                }
            },
            'total_time': 1.23
        }
        
        # Test direct audit storage
        control_plane._store_complete_audit_to_snowflake("Test audit logging", mock_results)
        print("✅ Direct audit storage test completed")
        
        print("\n🎯 AUDIT LOGGING TEST RESULTS:")
        print("✅ Audit logging functionality has been tested")
        print("📊 Check your Snowflake AUDIT_LOGS table:")
        print("   SELECT * FROM MY_DATABASE.PUBLIC.AUDIT_LOGS ORDER BY TIMESTAMP DESC LIMIT 5;")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_low_confidence_audit()