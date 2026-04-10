#!/usr/bin/env python3
"""
AI Control Plane Demo - Shows the 6-phase autonomous system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_control_plane import AIControlPlane
import json

def demo_control_plane():
    """Demonstrate AI Control Plane capabilities"""
    
    print("="*80)
    print("🤖 AI CONTROL PLANE DEMO")
    print("6-Phase Autonomous Data Governance System")
    print("="*80)
    
    # Initialize control plane
    control_plane = AIControlPlane()
    
    # Demo scenarios
    test_scenarios = [
        "mask pii in customers table",
        "implement gdpr right to be forgotten for user@example.com",
        "hide sensitive data in employee records"
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"🎯 DEMO SCENARIO {i}: '{scenario}'")
        print(f"{'='*60}")
        
        try:
            # Process through 6-phase control plane
            results = control_plane.process_natural_language(scenario)
            
            print(f"\n📊 EXECUTION RESULTS:")
            print(f"Status: {results['status']}")
            
            if results['status'] == 'success':
                print(f"Total Time: {results.get('total_time', 0):.2f} seconds")
                
                # Show phase results
                phases = results.get('phases', {})
                print(f"\n🔄 PHASE RESULTS:")
                
                for phase_name, phase_data in phases.items():
                    print(f"  📡 {phase_name.upper()}:")
                    if phase_name == 'observe':
                        print(f"     Intent: {phase_data.get('intent', 'N/A')}")
                        print(f"     Entities: {phase_data.get('target_entities', [])}")
                        print(f"     Confidence: {phase_data.get('confidence', 0):.1%}")
                    elif phase_name == 'analyze':
                        pii_count = len(phase_data.get('pii_findings', []))
                        risk_score = phase_data.get('risk_score', 0)
                        print(f"     PII Findings: {pii_count}")
                        print(f"     Risk Score: {risk_score:.2f}")
                    elif phase_name == 'plan':
                        sql_count = len(phase_data.get('sql_commands', []))
                        impact = phase_data.get('estimated_impact', {})
                        print(f"     SQL Commands: {sql_count}")
                        print(f"     Tables Affected: {impact.get('tables_affected', 0)}")
                    elif phase_name == 'execute':
                        success = phase_data.get('success', False)
                        rows = phase_data.get('rows_affected', 0)
                        print(f"     Success: {'✅' if success else '❌'}")
                        print(f"     Rows Affected: {rows:,}")
                    elif phase_name == 'learn':
                        patterns = len(phase_data.get('discovered_patterns', []))
                        recs = len(phase_data.get('recommendations', []))
                        print(f"     Patterns Found: {patterns}")
                        print(f"     Recommendations: {recs}")
                
                # Show key recommendations
                learn_phase = phases.get('learn', {})
                recommendations = learn_phase.get('recommendations', [])
                if recommendations:
                    print(f"\n💡 AI RECOMMENDATIONS:")
                    for rec in recommendations[:3]:
                        print(f"  • {rec}")
            
            elif results['status'] == 'low_confidence':
                print(f"Confidence too low: {results.get('confidence', 0):.1%}")
                print(f"Message: {results.get('message', 'N/A')}")
                print("Suggestions:")
                for suggestion in results.get('suggestions', []):
                    print(f"  • {suggestion}")
            
            else:
                print(f"Error: {results.get('error', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Demo scenario failed: {e}")
    
    print(f"\n{'='*80}")
    print("🎉 AI CONTROL PLANE DEMO COMPLETED!")
    print("This demonstrates the 6-phase autonomous governance system:")
    print("1. OBSERVE - Parse intent and scan database")
    print("2. ANALYZE - ML PII detection and risk assessment") 
    print("3. PLAN - Generate execution strategy with rollback")
    print("4. SIMULATE - Show impact and get approval")
    print("5. EXECUTE - Run policies and update metadata")
    print("6. LEARN - Verify results and recommend next actions")
    print(f"{'='*80}")

if __name__ == "__main__":
    demo_control_plane()