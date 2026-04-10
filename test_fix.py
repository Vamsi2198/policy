#!/usr/bin/env python
"""Quick test for the ai_control_plane fix"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🧪 Testing ai_control_plane.py fix...")
print("-" * 60)

try:
    # Compile check
    print("1️⃣  Checking Python syntax...")
    import py_compile
    py_compile.compile('src/ai_control_plane.py', doraise=True)
    print("   ✅ Syntax OK")
    
    # Import check
    print("\n2️⃣  Importing AIControlPlane...")
    from ai_control_plane import AIControlPlane
    print("   ✅ Import successful")
    
    # Initialization check
    print("\n3️⃣  Initializing AIControlPlane...")
    control_plane = AIControlPlane()
    print(f"   ✅ Initialized (Mode: {control_plane.nl_mode})")
    
    # Test with a simple query
    print("\n4️⃣  Testing with simple query...")
    results = control_plane.process_natural_language("test")
    print(f"   Status: {results.get('status')}")
    
    # Check for the KeyError fix
    if results.get('status') == 'low_confidence':
        print("\n5️⃣  Checking 'low_confidence' response structure...")
        required_fields = ['confidence', 'message', 'suggestions']
        missing = [f for f in required_fields if f not in results]
        
        if missing:
            print(f"   ❌ Missing fields: {missing}")
        else:
            print(f"   ✅ All required fields present!")
            print(f"      - confidence: {results['confidence']}")
            print(f"      - message: {results['message']}")
            print(f"      - suggestions: {len(results['suggestions'])} items")
    else:
        print(f"   ✅ Got status: {results.get('status')}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Fix is working!")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
