#!/usr/bin/env python3
"""
Simple test with auto-approval to test the complete fixed flow
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_control_plane import AIControlPlane

def test_with_auto_approval():
    """Test with a modified approval that auto-approves for testing"""
    print("🧪 Testing Complete Fixed Flow with Auto-Approval...")
    
    try:
        # Initialize AI Control Plane
        control_plane = AIControlPlane()
        
        # Monkey patch the approval method to auto-approve
        def auto_approve(simulate_result, plan_result):
            print("\n🤖 AUTO-APPROVING for test...")
            return {
                'approved': True,
                'reason': 'Auto-approved for testing',
                'timestamp': '2025-10-17T15:40:00'
            }
        
        # Replace the approval method
        control_plane._get_human_approval = auto_approve
        
        print("\n1️⃣ Testing with simple masking request...")
        test_query = "mask NAME column in EMPLOYEES table"
        
        results = control_plane.process_natural_language(test_query)
        
        print(f"\n📊 RESULTS:")
        print(f"Status: {results['status']}")
        print(f"Total time: {results.get('total_time', 0):.2f} seconds")
        
        if results['status'] == 'success':
            execute_phase = results['phases'].get('execute', {})
            print(f"Commands executed: {len(execute_phase.get('commands_executed', []))}")
            print(f"Rows affected: {execute_phase.get('rows_affected', 0)}")
            print("✅ Execution completed successfully!")
        elif results['status'] == 'error':
            print(f"❌ Error: {results.get('error', 'Unknown error')}")
        else:
            print(f"ℹ️ Status: {results['status']}")
        
        print("\n✅ Fixed flow test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_auto_approval()