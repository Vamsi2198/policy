#!/usr/bin/env python3
"""
Quick test for frontend-only approval system
"""

import requests
import json
import time

def test_frontend_approval():
    """Test that the system processes without terminal prompts"""
    try:
        print("🧪 Testing frontend-only approval system...")
        
        # Test command
        test_command = "mask PII data in customers table"
        print(f"📝 Command: '{test_command}'")
        
        # Send request with a timeout
        print("⏱️  Sending request...")
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:5000/api/process',
            json={'command': test_command},
            timeout=60  # 60 second timeout
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏰ Processing time: {processing_time:.2f}s")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! No terminal prompts!")
            
            # Check for approval details in simulate phase
            if 'phases' in result and 'simulate' in result['phases']:
                simulate = result['phases']['simulate']
                if 'approval_details' in simulate:
                    approval = simulate['approval_details']
                    print(f"🎭 Approval handled: {approval.get('reason', 'N/A')}")
                    
                    if 'simulation_details' in approval:
                        sim_details = approval['simulation_details']
                        print(f"📈 Rows affected: {sim_details.get('rows_affected', 0)}")
                        print(f"📊 Risk level: {sim_details.get('risk_level', 'Unknown')}")
                        print(f"⏱️  Estimated time: {sim_details.get('estimated_time', 0)}s")
                    
                    print("✅ Frontend approval system working!")
                else:
                    print("⚠️  No approval details found in response")
            else:
                print("⚠️  No simulate phase found in response")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this might indicate a terminal prompt is still active")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Atlan Actions API - Frontend Approval Mode")
    print("="*60)
    
    success = test_frontend_approval()
    
    if success:
        print("\n🎉 SUCCESS: Frontend-only approval system is working!")
        print("💡 You can now use the web dashboard without terminal prompts")
    else:
        print("\n❌ FAILED: There may still be terminal prompts or other issues")
    
    print(f"\n🌐 Dashboard available at: http://localhost:5000")