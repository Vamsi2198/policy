#!/usr/bin/env python3
"""
Test script for AI Control Plane - Enhanced PII Discovery
Tests the fixed data sampling and enhanced intent recognition
"""

from ai_control_plane import AIControlPlane
import time

def test_enhanced_pii_discovery():
    """Test the enhanced AI Control Plane with automatic PII discovery"""
    
    print("="*80)
    print("🧪 TESTING AI CONTROL PLANE - Enhanced PII Discovery")
    print("="*80)
    print("Testing: Enhanced data sampling + improved intent recognition")
    print("Command: 'Automatically discover PII and apply intelligent masking'")
    print("="*80)
    
    # Initialize AI Control Plane
    control_plane = AIControlPlane()
    
    # Test command that previously had low confidence
    test_query = "Automatically discover PII and apply intelligent masking"
    
    print(f"\n🎯 PROCESSING: {test_query}")
    print("-"*60)
    
    start_time = time.time()
    
    # Process through 6-phase control plane
    results = control_plane.process_natural_language(test_query)
    
    end_time = time.time()
    
    # Display comprehensive results
    print(f"\n📊 AI CONTROL PLANE EXECUTION RESULTS:")
    print(f"Status: {results['status']}")
    print(f"Total Execution Time: {end_time - start_time:.2f} seconds")
    print(f"Phases Completed: {len(results.get('phases', {}))}")
    
    if results['status'] == 'success':
        print(f"\n✅ SUCCESS - All 6 phases completed successfully!")
        
        # Show detailed phase results
        phases = results.get('phases', {})
        
        # OBSERVE Phase
        if 'observe' in phases:
            observe = phases['observe']
            print(f"\n🔍 OBSERVE Phase Results:")
            print(f"   Intent: {observe.get('intent', 'N/A')}")
            print(f"   Confidence: {observe.get('confidence', 0):.1%}")
            print(f"   Target Entities: {len(observe.get('target_entities', []))}")
            print(f"   Tables Sampled: {len(observe.get('sample_data', {}))}")
            
            # Show sampling success
            sample_data = observe.get('sample_data', {})
            for table, data in sample_data.items():
                if data:
                    print(f"     ✅ {table}: {len(data)} rows sampled")
                else:
                    print(f"     ⚠️ {table}: No data sampled")
        
        # ANALYZE Phase  
        if 'analyze' in phases:
            analyze = phases['analyze']
            print(f"\n🧠 ANALYZE Phase Results:")
            print(f"   PII Findings: {len(analyze.get('pii_findings', []))}")
            print(f"   Risk Score: {analyze.get('risk_score', 0):.2f}")
            
            # Show PII findings
            pii_findings = analyze.get('pii_findings', [])
            for finding in pii_findings[:5]:  # Show first 5
                table = finding.get('table', 'Unknown')
                column = finding.get('column', 'Unknown')
                pii_types = ', '.join(finding.get('pii_types', []))
                confidence = finding.get('confidence', 0)
                method = finding.get('detection_method', 'unknown')
                print(f"     🔍 {table}.{column}: {pii_types} ({confidence:.1%} via {method})")
        
        # PLAN Phase
        if 'plan' in phases:
            plan = phases['plan']
            print(f"\n📋 PLAN Phase Results:")
            print(f"   Policies Generated: {len(plan.get('policies', []))}")
            print(f"   Actions Planned: {len(plan.get('planned_actions', []))}")
            
            for action in plan.get('planned_actions', [])[:3]:
                print(f"     📝 {action}")
        
        # SIMULATE Phase
        if 'simulate' in phases:
            simulate = phases['simulate']
            print(f"\n🎮 SIMULATE Phase Results:")
            print(f"   Simulation Success: {simulate.get('simulation_success', False)}")
            print(f"   Safety Score: {simulate.get('safety_score', 0):.2f}")
            print(f"   Risk Assessment: {simulate.get('risk_assessment', 'N/A')}")
        
        # EXECUTE Phase
        if 'execute' in phases:
            execute = phases['execute']
            print(f"\n⚡ EXECUTE Phase Results:")
            print(f"   Execution Success: {execute.get('success', False)}")
            print(f"   Policies Applied: {len(execute.get('applied_policies', []))}")
            print(f"   Records Affected: {execute.get('records_affected', 0)}")
        
        # LEARN Phase
        if 'learn' in phases:
            learn = phases['learn']
            print(f"\n🎓 LEARN Phase Results:")
            print(f"   Verification Status: {'✅ Passed' if learn.get('verification_status') else '❌ Failed'}")
            print(f"   Patterns Discovered: {len(learn.get('discovered_patterns', []))}")
            print(f"   Recommendations: {len(learn.get('recommendations', []))}")
            print(f"   Confidence Feedback: {learn.get('confidence_feedback', 0):.2f}")
            
            # Show recommendations
            for rec in learn.get('recommendations', [])[:3]:
                print(f"     💡 {rec}")
    
    elif results['status'] == 'low_confidence':
        print(f"\n❌ LOW CONFIDENCE - Cannot proceed")
        print(f"Confidence: {results.get('confidence', 0):.1%}")
        print(f"Message: {results.get('message', 'N/A')}")
        
        print(f"\nSuggestions:")
        for suggestion in results.get('suggestions', []):
            print(f"  • {suggestion}")
    
    else:
        print(f"\n❌ EXECUTION FAILED")
        print(f"Error: {results.get('error', 'Unknown error')}")
    
    print(f"\n{'='*80}")
    print("🧪 TEST COMPLETED")
    print("="*80)
    
    return results

if __name__ == "__main__":
    test_enhanced_pii_discovery()