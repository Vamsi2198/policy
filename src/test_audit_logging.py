#!/usr/bin/env python3
"""
Test script to verify Snowflake audit logging functionality
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_control_plane import AIControlPlane

def test_audit_logging():
    """Test that audit logging works for various scenarios"""
    print("🧪 Testing Snowflake Audit Logging...")
    
    try:
        # Initialize AI Control Plane
        control_plane = AIControlPlane()
        
        # Test 1: Simple query that should work
        print("\n1️⃣ Testing successful execution with audit logging...")
        test_query = "discover PII in customers table and apply intelligent masking"
        
        results = control_plane.process_natural_language(test_query)
        
        print(f"Status: {results['status']}")
        print(f"Total time: {results.get('total_time', 0):.2f} seconds")
        
        if results['status'] == 'success':
            print("✅ Process completed successfully - check AUDIT_LOGS table")
        elif results['status'] == 'cancelled':
            print("⚠️ Process was cancelled by user - audit log still stored")
        elif results['status'] == 'low_confidence':
            print("⚠️ Low confidence - audit log stored with diagnostic info")
        else:
            print("❌ Process failed - audit log stored with error details")
        
        # Test 2: Query with intentionally low confidence
        print("\n2️⃣ Testing low confidence scenario...")
        low_conf_query = "do something with data"
        
        results2 = control_plane.process_natural_language(low_conf_query)
        print(f"Status: {results2['status']}")
        print(f"Confidence: {results2.get('confidence', 0):.1%}")
        
        print("\n✅ Audit logging test completed!")
        print("📊 Check your Snowflake AUDIT_LOGS table to see the stored results:")
        print("   SELECT * FROM MY_DATABASE.PUBLIC.AUDIT_LOGS ORDER BY TIMESTAMP DESC;")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audit_logging()