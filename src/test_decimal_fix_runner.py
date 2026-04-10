#!/usr/bin/env python3
"""
Test the fixed AI Control Plane with automatic input
Tests the Decimal JSON serialization fix
"""

import subprocess
import sys
import time

def test_ai_control_plane_fix():
    """Test the AI Control Plane with the Decimal serialization fix"""
    
    print("="*80)
    print("🧪 TESTING DECIMAL SERIALIZATION FIX")
    print("="*80)
    print("Testing: JSON serialization of Decimal objects in simulation phase")
    print("Target: Remove 'Object of type Decimal is not JSON serializable' error")
    print("="*80)
    
    # Create a test script that will provide input to the AI Control Plane
    test_script_content = '''
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_control_plane import AIControlPlane
import time

def test_decimal_fix():
    """Test the Decimal JSON serialization fix"""
    
    print("\\n🎯 TESTING: Automatically discover PII and apply intelligent masking")
    print("-"*60)
    
    # Initialize AI Control Plane
    control_plane = AIControlPlane()
    
    # Test the problematic query
    test_query = "Automatically discover PII and apply intelligent masking"
    
    try:
        start_time = time.time()
        
        # Process through 6-phase control plane
        results = control_plane.process_natural_language(test_query)
        
        end_time = time.time()
        
        print(f"\\n📊 DECIMAL FIX TEST RESULTS:")
        print(f"Status: {results['status']}")
        print(f"Total Time: {end_time - start_time:.2f} seconds")
        
        if results['status'] == 'success':
            print("✅ SUCCESS - Decimal serialization working correctly!")
            phases = results.get('phases', {})
            
            if 'simulate' in phases:
                print("✅ SIMULATE phase completed without JSON errors")
            else:
                print("⚠️ SIMULATE phase not found in results")
                
        elif results['status'] == 'error':
            error_msg = results.get('error', 'Unknown error')
            if 'Decimal is not JSON serializable' in error_msg:
                print("❌ FAILED - Decimal serialization error still present")
                print(f"Error: {error_msg}")
            else:
                print(f"⚠️ Different error occurred: {error_msg}")
        else:
            print(f"⚠️ Unexpected status: {results['status']}")
            
    except Exception as e:
        if 'Decimal is not JSON serializable' in str(e):
            print("❌ FAILED - Decimal serialization error still present")
            print(f"Exception: {e}")
        else:
            print(f"⚠️ Different exception occurred: {e}")

if __name__ == "__main__":
    test_decimal_fix()
'''
    
    # Write the test script
    with open('test_decimal_fix.py', 'w') as f:
        f.write(test_script_content)
    
    print("✅ Created test script: test_decimal_fix.py")
    print("🚀 Running test...")
    print("-" * 60)
    
    # Run the test
    try:
        result = subprocess.run([sys.executable, 'test_decimal_fix.py'], 
                              capture_output=True, text=True, timeout=120)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
        # Analyze results
        if 'Decimal is not JSON serializable' in result.stdout or 'Decimal is not JSON serializable' in result.stderr:
            print("\n❌ DECIMAL SERIALIZATION FIX FAILED")
            print("The error is still present - need further debugging")
        elif 'SUCCESS - Decimal serialization working correctly' in result.stdout:
            print("\n✅ DECIMAL SERIALIZATION FIX SUCCESSFUL")
            print("The AI Control Plane now handles Decimal objects correctly")
        else:
            print("\n⚠️ TEST INCONCLUSIVE")
            print("Unable to determine if the fix worked")
        
    except subprocess.TimeoutExpired:
        print("\n⏰ TEST TIMED OUT")
        print("The test took longer than 2 minutes - may be waiting for user input")
    except Exception as e:
        print(f"\n❌ TEST EXECUTION FAILED: {e}")
    
    print("\n" + "="*80)
    print("🧪 TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_ai_control_plane_fix()