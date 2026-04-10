#!/usr/bin/env python3
"""
Test the fixed policy cleanup and creation logic
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_control_plane import AIControlPlane

def test_policy_fixes():
    """Test the policy creation fixes"""
    print("🧪 Testing Fixed Policy Creation Logic...")
    
    try:
        # Initialize AI Control Plane
        control_plane = AIControlPlane()
        
        print("\n1️⃣ Testing comprehensive policy cleanup...")
        
        # Test the comprehensive cleanup method
        cleanup_commands = control_plane._generate_comprehensive_policy_cleanup()
        print(f"Generated {len(cleanup_commands)} cleanup commands")
        
        if cleanup_commands:
            print("Sample cleanup commands:")
            for cmd in cleanup_commands[:5]:  # Show first 5
                print(f"  • {cmd[:80]}...")
        
        print("\n2️⃣ Testing masking SQL generation with unique names...")
        
        # Test masking SQL generation
        mask_sql = control_plane._generate_masking_sql(
            "PUBLIC.EMPLOYEES", 
            "NAME", 
            "test_policy", 
            ["PERSON"]
        )
        
        print(f"Generated {len(mask_sql)} masking commands")
        for cmd in mask_sql:
            print(f"  • {cmd}")
        
        print("\n✅ Policy fix testing completed!")
        print("🎯 The fixes should handle:")
        print("   • Comprehensive cleanup of existing policies")
        print("   • Unique policy names with timestamps")
        print("   • Graceful handling of cleanup failures")
        print("   • Proper UNSET before CREATE workflow")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_policy_fixes()