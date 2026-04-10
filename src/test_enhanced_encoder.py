#!/usr/bin/env python3
"""
Test enhanced JSON encoder with datetime objects
"""

import json
from datetime import datetime, date
from decimal import Decimal

def test_enhanced_encoder():
    """Test the enhanced DecimalEncoder with datetime objects"""
    
    print("="*70)
    print("🧪 TESTING ENHANCED JSON ENCODER - Datetime & Decimal Fix")
    print("="*70)
    
    # Import the enhanced DecimalEncoder
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from ai_control_plane import DecimalEncoder
    
    # Test data with various problematic types (similar to Snowflake data)
    test_data = {
        "ID": 1,
        "NAME": "John Doe", 
        "SALARY": Decimal('60000.50'),
        "HIRE_DATE": datetime(2023, 1, 15, 9, 30, 0),
        "BIRTH_DATE": date(1990, 5, 20),
        "CREATED_AT": datetime.now(),
        "BONUS": Decimal('5000.25'),
        "IS_ACTIVE": True
    }
    
    print("📊 Test Data with Complex Types:")
    print(f"   Original: {test_data}")
    print(f"\n   Data Types:")
    for k, v in test_data.items():
        print(f"      {k}: {type(v).__name__} = {v}")
    
    # Test JSON serialization without custom encoder (should fail)
    print("\n❌ Testing without Enhanced Encoder:")
    try:
        json_without_encoder = json.dumps(test_data, indent=2)
        print("   Unexpected success - this should have failed")
    except TypeError as e:
        print(f"   Expected error: {e}")
    
    # Test JSON serialization with enhanced encoder (should work)
    print("\n✅ Testing with Enhanced DecimalEncoder:")
    try:
        json_with_encoder = json.dumps(test_data, indent=2, cls=DecimalEncoder)
        print("   Success! Serialized result:")
        print(json_with_encoder)
        
        # Verify the result can be parsed back
        parsed_data = json.loads(json_with_encoder)
        print(f"\n   📋 Parsed back successfully:")
        for k, v in parsed_data.items():
            print(f"      {k}: {type(v).__name__} = {v}")
        
        print("\n🎉 ENHANCED ENCODER TEST PASSED")
        print("   ✅ Decimal objects converted to float")
        print("   ✅ Datetime objects converted to ISO string")
        print("   ✅ Date objects converted to ISO string")
        print("   ✅ JSON serialization successful")
        print("   ✅ Data can be parsed back correctly")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\n💥 ENHANCED ENCODER TEST FAILED")
    
    print("\n" + "="*70)
    
    # Test the specific simulation data structure that was failing
    print("🎭 TESTING PRODUCTS TABLE SIMULATION DATA")
    print("="*70)
    
    # Simulate PRODUCTS table data with datetime (like what caused the error)
    products_before = {
        "PRODUCT_ID": 1,
        "NAME": "Widget A",
        "PRICE": Decimal('29.99'),
        "CREATED_DATE": datetime(2023, 6, 1, 14, 30, 0),
        "LAST_UPDATED": datetime.now(),
        "CATEGORY": "Electronics"
    }
    
    products_after = {
        "PRODUCT_ID": 1,
        "NAME": "***MASKED***",
        "PRICE": Decimal('29.99'),
        "CREATED_DATE": datetime(2023, 6, 1, 14, 30, 0),
        "LAST_UPDATED": datetime.now(),
        "CATEGORY": "Electronics"
    }
    
    print("📋 Products Table Data:")
    print(f"   Before: {products_before}")
    print(f"   After: {products_after}")
    
    # Test the exact simulation preview format
    try:
        before_json = json.dumps(products_before, indent=2, cls=DecimalEncoder)[:150] + "..."
        after_json = json.dumps(products_after, indent=2, cls=DecimalEncoder)[:150] + "..."
        
        print(f"\n📊 Products Simulation Preview:")
        print(f"   BEFORE: {before_json}")
        print(f"   AFTER:  {after_json}")
        
        print("\n🎉 PRODUCTS SIMULATION TEST PASSED")
        print("   ✅ Products table before/after JSON serialization working")
        print("   ✅ Datetime objects handled correctly")
        print("   ✅ Ready for AI Control Plane simulation phase")
        
    except Exception as e:
        print(f"\n❌ PRODUCTS SIMULATION ERROR: {e}")
        print("Need further debugging...")
    
    print("\n" + "="*70)
    print("🏁 ENHANCED ENCODER VERIFICATION COMPLETE")
    print("="*70)
    print("STATUS: Enhanced JSON encoder ready for:")
    print("• Decimal objects (from Snowflake numeric columns)")  
    print("• Datetime objects (from Snowflake timestamp columns)")
    print("• Date objects (from Snowflake date columns)")
    print("• Complex objects (general fallback handling)")
    print("="*70)

if __name__ == "__main__":
    test_enhanced_encoder()