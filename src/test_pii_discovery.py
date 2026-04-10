#!/usr/bin/env python3
"""
Quick test for PII discovery functionality
"""

import sys
import os
import json
from decimal import Decimal

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

from ai_control_plane import AIControlPlane

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal objects"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def test_pii_discovery():
    """Test PII discovery and masking functionality"""
    print("🔍 Testing PII Discovery and Masking...")
    print("=" * 60)
    
    try:
        # Initialize AI Control Plane
        control_plane = AIControlPlane()
        print("✅ AI Control Plane initialized")
        
        # Test the PII discovery command
        test_query = "Automatically discover PII and apply intelligent masking"
        print(f"\n🧪 Testing query: '{test_query}'")
        
        # Define a simple progress callback
        def progress_callback(phase_num, total_phases, phase_name, message):
            print(f"   📍 Phase {phase_num}/{total_phases}: {phase_name} - {message}")
        
        # Execute the query
        result = control_plane.process_natural_language(
            test_query, 
            progress_callback=progress_callback,
            session_id="test_session_001"
        )
        
        print("\n📊 RESULT:")
        print("=" * 30)
        print(f"Status: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'error':
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False
        else:
            print("✅ Query processed successfully!")
            
            # Show key results
            if 'phases' in result:
                print(f"\nPhases completed: {len(result['phases'])}")
            
            if 'query' in result:
                print(f"Original query: {result['query']}")
            
            # Pretty print the full result (truncated)
            result_str = json.dumps(result, indent=2, cls=DecimalEncoder)
            if len(result_str) > 2000:
                print(f"\nFirst 2000 chars of result:\n{result_str[:2000]}...")
            else:
                print(f"\nFull result:\n{result_str}")
            
            return True
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test runner"""
    print("🚀 Starting PII Discovery Test")
    print("=" * 60)
    
    success = test_pii_discovery()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: PII discovery functionality working!")
    else:
        print("❌ TEST FAILED: PII discovery has issues")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())