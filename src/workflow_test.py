#!/usr/bin/env python3
"""
Complete governance workflow test - using requests library
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_phases(phases):
    """Pretty print phase statuses"""
    phase_map = {
        'observe': ('1', 'OBSERVE'),
        'analyze': ('2', 'ANALYZE'),
        'plan': ('3', 'PLAN'),
        'simulate': ('4', 'SIMULATE'),
        'execute': ('5', 'EXECUTE'),
        'learn': ('6', 'LEARN')
    }
    
    for key in ['observe', 'analyze', 'plan', 'simulate', 'execute', 'learn']:
        if key in phases:
            phase = phases[key]
            num, name = phase_map[key]
            status = phase.get('status', 'unknown')
            message = phase.get('message', '')
            
            if status == 'completed':
                symbol = '[OK]'
            elif status == 'pending':
                symbol = '[WAIT]'
            else:
                symbol = '[???]'
            
            print(f"  {symbol} Phase {num} ({name}): {status}")
            if message:
                print(f"       -> {message}")

def test_full_workflow():
    """Test the complete approval workflow"""
    
    print_section("STEP 1: SUBMIT COMMAND")
    
    command = "mask salary in HEALTH_RECORDS for analyst role"
    print(f"[CMD] {command}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/process",
            json={"command": command},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        session_id = data.get('session_id') or data.get('request_id')
        print(f"\n[OK] Status: {data.get('status')}")
        print(f"[OK] Current Phase: {data.get('current_phase')}")
        print(f"[OK] Session ID: {session_id}")
        
        phases = data.get('phases', {})
        print("\n[PHASES]:")
        print_phases(phases)
        
        # Verify phase 4 is pending
        phase_4 = phases.get('simulate', {})
        if phase_4.get('status') == 'pending':
            print(f"\n[SUCCESS] Phase 4 is PENDING - awaiting approval!")
        else:
            print(f"\n[!] Phase 4 status: {phase_4.get('status')} (expected 'pending')")
        
    except Exception as e:
        print(f"[ERROR] Failed to submit command: {e}")
        return
    
    time.sleep(1)
    
    # STEP 2: Approve
    print_section("STEP 2: APPROVE CHANGES")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/approve/{session_id}",
            json={"approved": True, "comment": "Approved for testing"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"[OK] Approval Status: {data.get('status')}")
        print(f"[OK] Message: {data.get('message', '')}")
        print(f"[OK] Approved: {data.get('approved')}")
        
    except Exception as e:
        print(f"[ERROR] Failed to approve: {e}")
        return
    
    time.sleep(1)
    
    # STEP 3: Continue execution
    print_section("STEP 3: CONTINUE EXECUTION (Phases 5-6)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/continue-execution/{session_id}",
            json={},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        print(f"[OK] Execution Status: {data.get('status')}")
        print(f"[OK] Message: {data.get('message', '')}")
        
        # Get phases
        phases = data.get('phases', {})
        if phases:
            print("\n[FINAL PHASES]:")
            print_phases(phases)
        
        # Check all phases completed
        if phases.get('execute', {}).get('status') == 'completed':
            print(f"\n[SUCCESS] Phase 5 (EXECUTE) is COMPLETED!")
        if phases.get('learn', {}).get('status') == 'completed':
            print(f"[SUCCESS] Phase 6 (LEARN) is COMPLETED!")
        
        # Print execution details
        details = data.get('execution_details', {})
        if details:
            print("\n[EXECUTION DETAILS]:")
            print(f"  * Table: {details.get('table')}")
            print(f"  * Rows Modified: {details.get('rows_modified')}")
            print(f"  * Columns Masked: {details.get('columns_masked')}")
            print(f"  * Masking Types: {details.get('masking_types')}")
        
    except Exception as e:
        print(f"[ERROR] Failed to continue execution: {e}")
        return
    
    print_section("TEST COMPLETE - ALL PHASES EXECUTED!")
    print("[OK] Workflow: Command -> Phases 1-4 -> Approval -> Phases 5-6")

if __name__ == "__main__":
    test_full_workflow()
