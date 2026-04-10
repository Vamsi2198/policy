#!/usr/bin/env python3
"""
AI Control Plane - Local Mode Test (No API Keys Required)
Simple test to verify the system works without any external API calls
"""

import os
import sys

# Temporarily disable API keys to force local mode
os.environ.pop('OPENAI_API_KEY', None)
os.environ.pop('ANTHROPIC_API_KEY', None)

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_local_mode():
    """Test AI Control Plane in pure local mode"""
    print("🧪 Testing AI Control Plane - Local Mode (No API Keys)")
    print("="*60)
    
    try:
        from ai_control_plane import AIControlPlane
        
        # Force local mode
        control_plane = AIControlPlane(use_llm=False)
        print(f"✅ Initialized in {control_plane.nl_mode} mode")
        
        # Test with a simple query
        test_query = "mask PII in customers table"
        print(f"\n🎯 Testing query: '{test_query}'")
        
        results = control_plane.process_natural_language(test_query)
        
        print(f"\n📊 RESULTS:")
        print(f"Status: {results['status']}")
        print(f"Mode: {results.get('nl_mode', 'Unknown')}")
        
        if results['status'] == 'success':
            observe = results['phases'].get('observe', {})
            analyze = results['phases'].get('analyze', {})
            print(f"Confidence: {observe.get('confidence', 0):.1%}")
            print(f"Intent: {observe.get('intent', 'Unknown')}")
            print(f"Target entities: {observe.get('target_entities', [])}")
            print(f"PII findings: {len(analyze.get('pii_findings', []))}")
            print("✅ Local mode working successfully!")
        elif results['status'] == 'low_confidence':
            print(f"⚠️ Low confidence: {results.get('confidence', 0):.1%}")
            print(f"Message: {results.get('message', 'N/A')}")
        else:
            print(f"❌ Error: {results.get('error', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_mode()