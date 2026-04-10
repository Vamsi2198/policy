#!/usr/bin/env python3
"""
Demo: AI Control Plane Auto-Execution
Shows the complete 6-phase autonomous flow with auto-approval
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_control_plane import AIControlPlane

def demo_auto_execution():
    """Demonstrate auto-execution of AI Control Plane"""
    print("=" * 80)
    print("🚀 AI CONTROL PLANE - AUTO-EXECUTION DEMO")
    print("=" * 80)
    
    # Initialize with auto-approval
    control_plane = AIControlPlane("config.yaml", use_llm=False)
    
    # Override the approval method to auto-approve
    original_get_approval = control_plane._get_human_approval
    def auto_approve(sql_commands, impact_summary):
        print("🤖 AUTO-APPROVING execution...")
        return True
    control_plane._get_human_approval = auto_approve
    
    # Test queries to demonstrate different capabilities
    test_queries = [
        "mask NAME column in EMPLOYEES table",
        "show all masking policies",
        "create policy for email protection"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"🧪 TEST {i}: {query}")
        print('='*60)
        
        try:
            results = control_plane.process_natural_language(query)
            
            if results and results.get('success'):
                print(f"✅ SUCCESS: {results.get('phases_completed', 0)} phases completed")
                print(f"📊 SQL Commands: {len(results.get('sql_commands', []))}")
                print(f"🎯 Intent: {results.get('intent', 'Unknown')}")
                print(f"📈 Confidence: {results.get('confidence', 0):.2f}")
            else:
                print(f"⚠️  Partial execution or planning-only mode")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "-"*40)
    
    # Restore original method
    control_plane._get_human_approval = original_get_approval
    
    print("\n" + "="*80)
    print("🎯 AUTO-EXECUTION DEMO COMPLETED")
    print("="*80)

if __name__ == "__main__":
    demo_auto_execution()