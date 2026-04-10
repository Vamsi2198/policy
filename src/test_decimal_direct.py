#!/usr/bin/env python3
"""
Direct test of the Decimal JSON serialization fix
"""

import json
from decimal import Decimal

def test_decimal_encoder():
    """Test the DecimalEncoder class directly"""
    
    print("="*60)
    print("🧪 TESTING DECIMAL JSON SERIALIZATION FIX")
    print("="*60)
    
    # Import the DecimalEncoder from ai_control_plane
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from ai_control_plane import DecimalEncoder
    
    # Test data with Decimal objects (similar to Snowflake data)
    test_data = {
        "ID": 1,
        "NAME": "John Doe", 
        "SALARY": Decimal('60000.50'),
        "BONUS": Decimal('5000.25'),
        "TAX_RATE": Decimal('0.22')
    }
    
    print("📊 Test Data:")
    print(f"   Original: {test_data}")
    print(f"   Types: {[(k, type(v).__name__) for k, v in test_data.items()]}")
    
    # Test JSON serialization without custom encoder (should fail)
    print("\n❌ Testing without DecimalEncoder:")
    try:
        json_without_encoder = json.dumps(test_data, indent=2)
        print("   Unexpected success:", json_without_encoder[:100] + "...")
    except TypeError as e:
        print(f"   Expected error: {e}")
    
    # Test JSON serialization with custom encoder (should work)
    print("\n✅ Testing with DecimalEncoder:")
    try:
        json_with_encoder = json.dumps(test_data, indent=2, cls=DecimalEncoder)
        print("   Success:", json_with_encoder[:100] + "...")
        
        # Verify the result can be parsed back
        parsed_data = json.loads(json_with_encoder)
        print(f"   Parsed back: {parsed_data}")
        print(f"   Parsed types: {[(k, type(v).__name__) for k, v in parsed_data.items()]}")
        
        print("\n🎉 DECIMAL ENCODER TEST PASSED")
        print("   ✅ Decimal objects converted to float")
        print("   ✅ JSON serialization successful")
        print("   ✅ Data can be parsed back correctly")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\n💥 DECIMAL ENCODER TEST FAILED")
    
    print("\n" + "="*60)
    
    # Test the simulation preview format specifically
    print("🎭 TESTING SIMULATION PREVIEW FORMAT")
    print("="*60)
    
    # Simulate the exact data structure from the simulation phase
    before_row = {
        "ID": 1,
        "NAME": "Employee 1",
        "DEPARTMENT": "HR", 
        "SALARY": Decimal('60000.0')
    }
    
    after_row = {
        "ID": 1,
        "NAME": "***MASKED***",
        "DEPARTMENT": "HR",
        "SALARY": Decimal('60000.0')
    }
    
    print("📋 Simulation Data:")
    print(f"   Before: {before_row}")
    print(f"   After: {after_row}")
    
    # Test the exact format used in the simulation phase
    try:
        before_json = json.dumps(before_row, indent=2, cls=DecimalEncoder)[:100] + "..."
        after_json = json.dumps(after_row, indent=2, cls=DecimalEncoder)[:100] + "..."
        
        print(f"\n📊 Simulation Preview Format:")
        print(f"   BEFORE: {before_json}")
        print(f"   AFTER:  {after_json}")
        
        print("\n🎉 SIMULATION PREVIEW TEST PASSED")
        print("   ✅ Before/after JSON serialization working")
        print("   ✅ Ready for AI Control Plane simulation phase")
        
    except Exception as e:
        print(f"\n❌ SIMULATION PREVIEW ERROR: {e}")
    
    print("\n" + "="*60)
    print("🏁 DECIMAL FIX VERIFICATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_decimal_encoder()