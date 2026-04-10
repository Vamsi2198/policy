#!/usr/bin/env python3
"""
Test Complete 6-Phase Governance Workflow
"""
import requests
import json
import time

def test_complete_workflow():
    print("🚀 Testing Complete 6-Phase Atlan Actions Workflow...")
    print("=" * 60)
    
    # Test the governance command
    url = "http://localhost:5000/api/process"
    command = "Automatically discover PII and apply intelligent masking"
    
    print(f"📤 Sending command: '{command}'")
    print(f"🔗 Endpoint: {url}")
    print()
    
    try:
        response = requests.post(url, json={"query": command})
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Request successful!")
            print(f"📊 Response Status: {result.get('status', 'unknown')}")
            print(f"⏱️  Execution Time: {result.get('execution_time', 0):.2f}s")
            print(f"🎯 Confidence: {result.get('confidence', 0)*100:.1f}%")
            print()
            
            # Display phase results
            phases = result.get('phases', {})
            print("🔄 6-Phase Execution Results:")
            print("-" * 40)
            
            phase_names = [
                ('observe', '📡 OBSERVE'),
                ('analyze', '🧠 ANALYZE'), 
                ('plan', '📋 PLAN'),
                ('simulate', '🎭 SIMULATE'),
                ('execute', '⚡ EXECUTE'),
                ('learn', '📚 LEARN')
            ]
            
            for phase_key, phase_name in phase_names:
                phase_data = phases.get(phase_key, {})
                if phase_data:
                    print(f"{phase_name}: ✅ Completed")
                    if 'duration' in phase_data:
                        print(f"   Duration: {phase_data['duration']:.2f}s")
                    if phase_key == 'observe':
                        print(f"   Intent: {phase_data.get('intent', 'N/A')}")
                        print(f"   Entities: {len(phase_data.get('target_entities', []))} tables")
                    elif phase_key == 'analyze':
                        print(f"   PII Findings: {len(phase_data.get('pii_findings', []))} columns")
                    elif phase_key == 'execute':
                        print(f"   Policies Created: {phase_data.get('policies_created', 0)}")
                        print(f"   Atlan Sync: {phase_data.get('atlan_sync_status', {}).get('synced_items', 0)} items")
                else:
                    print(f"{phase_name}: ⏳ Pending")
                print()
            
            # Display summary metrics
            print("📈 Summary Metrics:")
            print("-" * 20)
            print(f"Tables Affected: {result.get('tables_affected', 0)}")
            print(f"Columns Protected: {result.get('columns_protected', 0)}")
            print(f"Policies Created: {result.get('policies_created', 0)}")
            print(f"Atlan Items Synced: {result.get('atlan_synced_items', 0)}")
            print()
            
            # Display recommendations
            recommendations = result.get('recommendations', [])
            if recommendations:
                print("💡 AI Recommendations:")
                print("-" * 22)
                for rec in recommendations[:3]:
                    print(f"   • {rec}")
                print()
            
            print("🎉 Complete 6-phase governance workflow executed successfully!")
            
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing workflow: {e}")

if __name__ == "__main__":
    test_complete_workflow()