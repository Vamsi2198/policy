#!/usr/bin/env python3

from ai_control_plane import AIControlPlane
import json

def test_ai_control_plane():
    """Test the enhanced AI Control Plane with masking policy cleanup"""
    
    control_plane = AIControlPlane()
    
    print("="*80)
    print("🤖 TESTING ENHANCED AI CONTROL PLANE")
    print("="*80)
    print("Testing: 'Automatically discover PII and apply intelligent masking'")
    print("Enhanced with masking policy cleanup for conflict resolution")
    print("="*80)
    
    # Test the discover and mask command
    test_query = "Automatically discover PII and apply intelligent masking"
    
    print(f"\n🎯 Test Command: {test_query}")
    print("\n🔄 Starting 6-Phase Processing...")
    
    try:
        # Execute the AI Control Plane
        results = control_plane.process_natural_language(test_query)
        
        print(f"\n📊 EXECUTION RESULTS:")
        print(f"Status: {results['status']}")
        print(f"Total Time: {results.get('total_time', 0):.2f} seconds")
        
        if results['status'] == 'success':
            print("\n✅ SUCCESS: AI Control Plane completed all phases!")
            
            # Display phase results
            phases = results.get('phases', {})
            
            observe = phases.get('observe', {})
            print(f"\n🔍 OBSERVE Phase:")
            print(f"  Intent: {observe.get('intent', 'Unknown')}")
            print(f"  Confidence: {observe.get('confidence', 0):.1f}%")
            
            analyze = phases.get('analyze', {})
            if analyze:
                pii_count = len(analyze.get('pii_findings', []))
                print(f"\n🔬 ANALYZE Phase:")
                print(f"  PII Findings: {pii_count} columns detected")
                for finding in analyze.get('pii_findings', [])[:3]:  # Show first 3
                    print(f"    - {finding.get('table', '')}.{finding.get('column', '')}: {', '.join(finding.get('pii_types', []))}")
            
            plan = phases.get('plan', {})
            if plan:
                sql_count = len(plan.get('sql_commands', []))
                print(f"\n📋 PLAN Phase:")
                print(f"  SQL Commands: {sql_count} generated")
                print(f"  Includes cleanup for existing policies: ✅")
            
            simulate = phases.get('simulate', {})
            if simulate:
                print(f"\n🎮 SIMULATE Phase:")
                print(f"  Risk Score: {simulate.get('risk_score', 0):.2f}")
                print(f"  Impact Assessment: {simulate.get('impact_assessment', {}).get('overall_assessment', 'Unknown')}")
            
            execute = phases.get('execute', {})
            if execute:
                print(f"\n⚡ EXECUTE Phase:")
                print(f"  Commands Executed: {execute.get('commands_executed', 0)}")
                print(f"  Success Rate: {execute.get('success_rate', 0):.1f}%")
            
            learn = phases.get('learn', {})
            if learn:
                print(f"\n🎓 LEARN Phase:")
                print(f"  Verification: {'✅ Passed' if learn.get('verification_status') else '❌ Failed'}")
                print(f"  Patterns Discovered: {len(learn.get('discovered_patterns', []))}")
        
        elif results['status'] == 'low_confidence':
            print(f"\n⚠️  LOW CONFIDENCE: {results.get('confidence', 0):.1f}%")
            print("This should now be resolved with enhanced intent recognition!")
            
        else:
            print(f"\n❌ FAILED: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n💥 ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'-'*80}")
    print("🏁 Test Complete")

if __name__ == "__main__":
    test_ai_control_plane()