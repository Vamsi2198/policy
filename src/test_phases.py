#!/usr/bin/env python3
"""
Simple test file to debug the complete 4-6 stage execution
"""
import sys
sys.path.insert(0, '.')

import json
from datetime import datetime

# Simulate the API workflow manually
def test_phases():
    print("\n" + "="*70)
    print("  TESTING: Complete Phase Execution (1-6)")
    print("="*70)
    
    # Simulate phase_progress dictionary like in the server
    session_id = "test_session_12345"
    phase_progress = {
        session_id: {
            'command': 'mask salary in HEALTH_RECORDS',
            'current_phase': 0,
            'start_time': datetime.now().isoformat(),
            'phases': {
                '1': {'name': 'OBSERVE', 'status': 'pending', 'message': ''},
                '2': {'name': 'ANALYZE', 'status': 'pending', 'message': ''},
                '3': {'name': 'PLAN', 'status': 'pending', 'message': ''},
                '4': {'name': 'SIMULATE', 'status': 'pending', 'message': ''},
                '5': {'name': 'EXECUTE', 'status': 'pending', 'message': ''},
                '6': {'name': 'LEARN', 'status': 'pending', 'message': ''},
            },
            'approval': {}
        }
    }
    
    print("\n[INITIAL STATE]")
    print(f"Session: {session_id}")
    print("Phases: All pending")
    
    # STEP 1: Simulate /api/process endpoint - runs phases 1-4
    print("\n" + "="*70)
    print("  STEP 1: /api/process endpoint (Phases 1-4)")
    print("="*70)
    
    # Simulate phases 1-3 completing
    phase_progress[session_id]['phases']['1']['status'] = 'completed'
    phase_progress[session_id]['phases']['1']['message'] = 'Schema analyzed'
    
    phase_progress[session_id]['phases']['2']['status'] = 'completed'
    phase_progress[session_id]['phases']['2']['message'] = 'PII detected in 3 columns'
    
    phase_progress[session_id]['phases']['3']['status'] = 'completed'
    phase_progress[session_id]['phases']['3']['message'] = 'Masking policy created'
    
    # Phase 4 should be PENDING (awaiting approval)
    phase_progress[session_id]['phases']['4']['status'] = 'pending'
    phase_progress[session_id]['phases']['4']['message'] = 'Awaiting approval'
    
    phase_progress[session_id]['current_phase'] = 4
    
    # Build response
    response = {
        'status': 'pending_approval',
        'current_phase': 4,
        'session_id': session_id,
        'command': phase_progress[session_id]['command'],
        'phases': {
            'observe': {'status': 'completed', 'message': 'Schema analyzed'},
            'analyze': {'status': 'completed', 'message': 'PII detected in 3 columns'},
            'plan': {'status': 'completed', 'message': 'Masking policy created'},
            'simulate': {'status': 'pending', 'message': 'Awaiting approval'},
            'execute': {'status': 'pending', 'message': 'Ready to execute'},
            'learn': {'status': 'pending', 'message': 'Ready to learn'}
        },
        'pii_findings': [
            {'column': 'EMAIL', 'type': 'EMAIL_ADDRESS', 'masking_type': 'MASK'},
            {'column': 'PHONE', 'type': 'PHONE_NUMBER', 'masking_type': 'MASK'},
            {'column': 'SSN', 'type': 'US_SSN', 'masking_type': 'HASH'}
        ],
        'proposed_changes': {
            'table': 'HEALTH_RECORDS',
            'operation': 'APPLY_MASKING_POLICY',
            'affected_rows': 10000,
            'columns_affected': ['SALARY', 'EMAIL', 'PHONE', 'SSN']
        }
    }
    
    print("\n[RESPONSE FROM /api/process]")
    print(f"Status: {response['status']}")
    print(f"Current Phase: {response['current_phase']}")
    print("\nPhase Status:")
    for phase_name, phase_data in response['phases'].items():
        print(f"  - {phase_name.upper()}: {phase_data['status']} ({phase_data['message']})")
    
    phase_4_status = response['phases'].get('simulate', {}).get('status')
    if phase_4_status == 'pending':
        print("\n[OK] Phase 4 (SIMULATE) is PENDING - CORRECT!")
    else:
        print(f"\n[ERROR] Phase 4 should be PENDING but is: {phase_4_status}")
    
    # STEP 2: Approve the action
    print("\n" + "="*70)
    print("  STEP 2: /api/approve endpoint")
    print("="*70)
    
    approval_payload = {
        'approved': True,
        'comment': 'Approved for testing'
    }
    
    print(f"\nApproval Request:")
    print(f"  Session: {session_id}")
    print(f"  Approved: {approval_payload['approved']}")
    print(f"  Comment: {approval_payload['comment']}")
    
    # Store approval
    phase_progress[session_id]['approval'] = {
        'approved': True,
        'reason': approval_payload['comment'],
        'timestamp': datetime.now().isoformat()
    }
    
    approval_response = {
        'status': 'success',
        'approved': True,
        'session_id': session_id,
        'message': 'Action approved. Ready to execute phases 5-6.'
    }
    
    print(f"\n[APPROVAL RESPONSE]")
    print(f"Status: {approval_response['status']}")
    print(f"Approved: {approval_response['approved']}")
    print(f"Message: {approval_response['message']}")
    
    # STEP 3: Continue execution (phases 5-6)
    print("\n" + "="*70)
    print("  STEP 3: /api/continue-execution endpoint (Phases 5-6)")
    print("="*70)
    
    # Check if approval exists
    if not phase_progress[session_id]['approval'].get('approved'):
        print(f"\n[ERROR] Action not approved!")
        return False
    
    print(f"\n[OK] Approval found: {phase_progress[session_id]['approval']}")
    
    # Execute phases 5-6
    print("\nExecuting Phase 5 (EXECUTE)...")
    phase_progress[session_id]['phases']['5']['status'] = 'completed'
    phase_progress[session_id]['phases']['5']['message'] = 'Masking policy applied to HEALTH_RECORDS'
    
    print("Executing Phase 6 (LEARN)...")
    phase_progress[session_id]['phases']['6']['status'] = 'completed'
    phase_progress[session_id]['phases']['6']['message'] = 'Execution recorded in audit log'
    
    # IMPORTANT: Also mark phase 4 as completed now that approval is given
    print("Marking Phase 4 (SIMULATE) as completed (approval was given)...")
    phase_progress[session_id]['phases']['4']['status'] = 'completed'
    phase_progress[session_id]['phases']['4']['message'] = 'Simulation completed'
    
    phase_progress[session_id]['current_phase'] = 6
    
    # Build continue-execution response
    continue_response = {
        'status': 'success',
        'current_phase': 6,
        'session_id': session_id,
        'message': 'Governance policy successfully executed',
        'phases': {
            'observe': {'status': 'completed', 'message': 'Schema analyzed'},
            'analyze': {'status': 'completed', 'message': 'PII detected'},
            'plan': {'status': 'completed', 'message': 'Masking policy created'},
            'simulate': {'status': 'completed', 'message': 'Simulation completed'},
            'execute': {'status': 'completed', 'message': 'Masking policy applied'},
            'learn': {'status': 'completed', 'message': 'Execution logged'}
        },
        'execution_details': {
            'table': 'HEALTH_RECORDS',
            'columns_masked': ['SALARY', 'EMAIL', 'PHONE', 'SSN'],
            'rows_modified': 10000,
            'masking_types': {'SALARY': 'MASK', 'EMAIL': 'MASK', 'PHONE': 'MASK', 'SSN': 'HASH'}
        }
    }
    
    print(f"\n[CONTINUE-EXECUTION RESPONSE]")
    print(f"Status: {continue_response['status']}")
    print(f"Current Phase: {continue_response['current_phase']}")
    print("\nFinal Phase Status:")
    for phase_name, phase_data in continue_response['phases'].items():
        status_symbol = "[DONE]" if phase_data['status'] == 'completed' else "[WAIT]"
        print(f"  {status_symbol} {phase_name.upper()}: {phase_data['status']}")
    
    print("\n[EXECUTION DETAILS]")
    exec_details = continue_response['execution_details']
    print(f"  Table: {exec_details['table']}")
    print(f"  Rows Modified: {exec_details['rows_modified']}")
    print(f"  Columns Masked: {exec_details['columns_masked']}")
    print(f"  Masking Types: {exec_details['masking_types']}")
    
    # Verify all phases completed
    all_completed = all(
        phase_progress[session_id]['phases'][str(i)]['status'] == 'completed' 
        for i in range(1, 7)
    )
    
    print("\n" + "="*70)
    if all_completed:
        print("  [SUCCESS] ALL 6 PHASES COMPLETED!")
        print("  Workflow: Command -> Phases 1-4 -> Approval -> Phases 5-6")
        return True
    else:
        print("  [ERROR] Not all phases completed")
        for i in range(1, 7):
            status = phase_progress[session_id]['phases'][str(i)]['status']
            print(f"    Phase {i}: {status}")
        return False
    
if __name__ == "__main__":
    success = test_phases()
    sys.exit(0 if success else 1)
