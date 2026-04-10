#!/usr/bin/env python3
"""
Simple test to validate governance workflow using curl
"""
import subprocess
import json
import time

BASE_URL = "http://localhost:5000"

def test_workflow():
    print("\n" + "="*70)
    print("  TESTING: mask salary in HEALTH_RECORDS for analyst role")
    print("="*70)
    
    # Test 1: Submit command
    print("\n[STEP 1] Submitting command...")
    cmd = f'curl -X POST "{BASE_URL}/api/process" -H "Content-Type: application/json" -d "{{\\"command\\": \\"mask salary in HEALTH_RECORDS for analyst role\\"}}"'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}")
        return
    
    try:
        response = json.loads(result.stdout)
        print(f"[OK] Status: {response.get('status')}")
        print(f"[OK] Current Phase: {response.get('current_phase')}")
        
        session_id = response.get('session_id') or response.get('request_id')
        print(f"[OK] Session ID: {session_id}")
        
        # Check phase 4 status
        phases = response.get('phases', {})
        phase_4 = phases.get('4', {})
        print(f"\n[PHASE 4] Status: {phase_4.get('status')}")
        print(f"[PHASE 4] Message: {phase_4.get('message')}")
        
        if phase_4.get('status') == 'pending':
            print("[OK] Phase 4 is PENDING - awaiting approval!")
        else:
            print(f"[!] Phase 4 should be PENDING but got: {phase_4.get('status')}")
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse response: {e}")
        print(f"Response: {result.stdout}")

if __name__ == "__main__":
    test_workflow()
