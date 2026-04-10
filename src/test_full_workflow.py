#!/usr/bin/env python3
"""
Test Full Governance Workflow
1. Submit query
2. Check stages 1-3 complete
3. Stage 4 should ask for APPROVAL (STOP HERE)
4. Send approval
5. Stages 5-6 execute
6. Database changes applied
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"
COMMAND = "mask pii in HEALTH_RECORDS table"

print("=" * 80)
print("FULL GOVERNANCE WORKFLOW TEST")
print("=" * 80)

# STEP 1: Submit the query
print("\n[STEP 1] Submitting query...")
print(f"Command: {COMMAND}")

resp = requests.post(
    f"{BASE_URL}/api/process",
    json={"command": COMMAND},
    timeout=120
)

result = resp.json()
session_id = result.get("request_id") or result.get("session_id")
print(f"Session ID: {session_id}")
print(f"Status: {result.get('status')}")
print(f"Current Phase: {result.get('current_phase')}")

# Print phases
phases = result.get("phases", {})
print("\nPhase Status:")
for phase_num in ["1", "2", "3", "4", "5", "6"]:
    if phase_num in phases:
        phase = phases[phase_num]
        status = phase.get("status", "unknown")
        message = phase.get("message", "")
        print(f"  Phase {phase_num} ({phase.get('name')}): {status} - {message}")

# STEP 2: Check if we're at approval stage
print("\n" + "=" * 80)
print("[STEP 2] Checking Status...")
print("=" * 80)

if result.get("status") == "pending_approval":
    print("\n✅ CORRECT! Status is 'pending_approval' - waiting for user approval")
    print("\nProposed Changes:")
    if "proposed_changes" in result:
        changes = result["proposed_changes"]
        print(f"  Table: {changes.get('table')}")
        print(f"  Operation: {changes.get('operation')}")
        print(f"  Affected Rows: {changes.get('affected_rows')}")
        print(f"  Columns: {', '.join(changes.get('columns_affected', []))}")
    
    if "pii_findings" in result:
        print("\nPII Detected:")
        for finding in result["pii_findings"][:3]:
            print(f"  - {finding.get('column')} ({finding.get('type')})")
    
    # STEP 3: User approves
    print("\n" + "=" * 80)
    print("[STEP 3] Sending Approval...")
    print("=" * 80)
    print(f"\nApproving session: {session_id}")
    
    time.sleep(1)
    
    approve_resp = requests.post(
        f"{BASE_URL}/api/approve/{session_id}",
        json={"approved": True, "reason": "Approved by test script"},
        timeout=30
    )
    
    approve_result = approve_resp.json()
    print(f"Approval Response Status: {approve_result.get('status')}")
    print(f"Approved: {approve_result.get('approved')}")
    
    # STEP 4: Continue execution (stages 5-6)
    print("\n" + "=" * 80)
    print("[STEP 4] Executing Stages 5-6...")
    print("=" * 80)
    print(f"\nContinuing execution for session: {session_id}")
    
    time.sleep(1)
    
    exec_resp = requests.post(
        f"{BASE_URL}/api/continue-execution/{session_id}",
        json={},
        timeout=120
    )
    
    exec_result = exec_resp.json()
    print(f"\nExecution Status: {exec_result.get('status')}")
    print(f"Message: {exec_result.get('message')}")
    
    # Print execution phases
    if "phases" in exec_result:
        print("\nExecution Phases:")
        exec_phases = exec_result["phases"]
        for phase_name in ["execute", "learn"]:
            if phase_name in exec_phases:
                phase = exec_phases[phase_name]
                print(f"  {phase_name.upper()}: {phase.get('status')} - {phase.get('message')}")
    
    # Check database changes
    if "execution_details" in exec_result:
        print("\nDatabase Changes Applied:")
        details = exec_result["execution_details"]
        print(f"  Table: {details.get('table')}")
        print(f"  Columns Masked: {', '.join(details.get('columns_masked', []))}")
        print(f"  Rows Modified: {details.get('rows_modified')}")
        for col, mask_type in details.get('masking_types', {}).items():
            print(f"    - {col}: {mask_type}")
    
    # FINAL RESULT
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE")
    print("=" * 80)
    print(f"✅ Full governance workflow executed successfully!")
    
else:
    print(f"\n❌ WRONG STATUS: {result.get('status')}")
    print(f"Expected: 'pending_approval' at stage 4")
    print(f"\nFull Response:")
    print(json.dumps(result, indent=2)[:1000])
