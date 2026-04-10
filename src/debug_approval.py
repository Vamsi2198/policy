#!/usr/bin/env python3
"""
Debug the approval and continue-execution endpoints
"""
import subprocess
import json

BASE_URL = "http://localhost:5000"

def test_approval_flow():
    print("\n" + "="*70)
    print("  DEBUGGING: Approval and Continue-Execution Endpoints")
    print("="*70)
    
    # First, get a session ID by submitting a command
    print("\n[1] Submitting command to get session ID...")
    cmd = f'curl -s -X POST "{BASE_URL}/api/process" -H "Content-Type: application/json" -d "{{\\"command\\": \\"mask salary in HEALTH_RECORDS\\"}}"'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    response = json.loads(result.stdout)
    session_id = response.get('session_id') or response.get('request_id')
    
    print(f"[OK] Session ID: {session_id}")
    print(f"[OK] Current Phase: {response.get('current_phase')}")
    print(f"[OK] Status: {response.get('status')}")
    
    # Now test the approval endpoint
    print(f"\n[2] Testing APPROVAL endpoint for session {session_id}...")
    approval_payload = json.dumps({"approved": True, "comment": "Test approval"})
    
    # Use proper escaping for PowerShell
    cmd = f'''curl -s -X POST "{BASE_URL}/api/approve/{session_id}" -H "Content-Type: application/json" -d '{approval_payload}' '''
    
    print(f"[CMD] {cmd[:100]}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(f"[STDOUT] {result.stdout}")
    print(f"[STDERR] {result.stderr}")
    print(f"[RETURN CODE] {result.returncode}")
    
    if result.stdout:
        try:
            approval_response = json.loads(result.stdout)
            print(f"\n[APPROVAL RESPONSE]:")
            print(json.dumps(approval_response, indent=2))
        except:
            print(f"[!] Could not parse approval response")
    
    # Now test the continue-execution endpoint
    print(f"\n[3] Testing CONTINUE-EXECUTION endpoint for session {session_id}...")
    cmd = f'curl -s -X POST "{BASE_URL}/api/continue-execution/{session_id}" -H "Content-Type: application/json" -d "{{}}"'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(f"[STDOUT] {result.stdout[:200]}...")
    print(f"[STDERR] {result.stderr}")
    print(f"[RETURN CODE] {result.returncode}")
    
    if result.stdout:
        try:
            exec_response = json.loads(result.stdout)
            print(f"\n[CONTINUE-EXECUTION RESPONSE]:")
            print(json.dumps(exec_response, indent=2))
        except:
            print(f"[!] Could not parse continue-execution response")

if __name__ == "__main__":
    test_approval_flow()
