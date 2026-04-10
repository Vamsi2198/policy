#!/usr/bin/env python3
"""
Test AI Control Plane with Discovery Request
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_control_plane import AIControlPlane

def test_discovery_request():
    """Test automatic PII discovery request"""
    
    print("🧪 TESTING AI CONTROL PLANE - PII DISCOVERY")
    print("=" * 60)
    
    # Initialize control plane
    control_plane = AIControlPlane()
    
    # Test query
    test_query = "Automatically discover PII and apply intelligent masking"
    
    print(f"📝 Test Query: '{test_query}'")
    
    # Test intent extraction
    intent = control_plane._extract_intent(test_query)
    print(f"🎯 Extracted Intent: {intent}")
    
    # Test confidence calculation
    confidence = control_plane._calculate_observation_confidence(
        test_query, intent, ['customers'], {}
    )
    print(f"📊 Confidence Score: {confidence:.1%}")
    
    print(f"\n✅ Test Results:")
    print(f"   Intent Recognition: {'✅ PASS' if intent == 'DISCOVER_AND_MASK' else '❌ FAIL'}")
    print(f"   Confidence Level: {'✅ PASS' if confidence >= 0.8 else '❌ FAIL'}")
    
    if intent == 'DISCOVER_AND_MASK' and confidence >= 0.8:
        print(f"\n🎉 AI Control Plane should now process this request successfully!")
        print(f"   The low confidence issue has been resolved.")
    else:
        print(f"\n⚠️  Still need to debug further.")

if __name__ == "__main__":
    test_discovery_request()