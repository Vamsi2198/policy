"""
Quick test to check if unmask intent is working
"""

import yaml
from ai_control_plane import AIControlPlane
from control_pannel import ControlPlaneEngine

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create engine and control plane
engine = ControlPlaneEngine(config)
control_plane = AIControlPlane(engine, config)

# Test unmask command
test_queries = [
    "unmask the customers table",
    "remove masking from customers",
    "unmask pii in customers"
]

print("\n" + "="*80)
print("TESTING UNMASK INTENT DETECTION")
print("="*80)

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    print("-" * 80)
    
    try:
        # Just test the observe phase to see what intent is detected
        result = control_plane.process(query)
        
        intent = result.get('intent', 'unknown')
        phases = result.get('phases', {})
        observe = phases.get('observe', {})
        plan = phases.get('plan', {})
        
        print(f"   Intent Detected: {intent}")
        print(f"   Observe Intent: {observe.get('intent', 'N/A')}")
        
        # Check SQL commands
        sql_commands = plan.get('sql_commands', [])
        print(f"\n   SQL Commands ({len(sql_commands)}):")
        for i, cmd in enumerate(sql_commands[:5], 1):
            # Check if it's UNSET or DROP (unmask) vs SET (mask)
            cmd_upper = cmd.upper()
            if 'UNSET' in cmd_upper:
                print(f"   {i}. ✅ UNMASK: {cmd[:80]}...")
            elif 'DROP MASKING POLICY' in cmd_upper:
                print(f"   {i}. ✅ UNMASK: {cmd[:80]}...")
            elif 'SET MASKING POLICY' in cmd_upper:
                print(f"   {i}. ❌ WRONG (MASK): {cmd[:80]}...")
            elif 'CREATE MASKING POLICY' in cmd_upper:
                print(f"   {i}. ❌ WRONG (CREATE): {cmd[:80]}...")
            else:
                print(f"   {i}. {cmd[:80]}...")
        
        # Verdict
        has_unmask = any('UNSET' in cmd.upper() or 'DROP MASKING POLICY' in cmd.upper() 
                        for cmd in sql_commands)
        has_mask = any('SET MASKING POLICY' in cmd.upper() or 'CREATE MASKING POLICY' in cmd.upper() 
                      for cmd in sql_commands)
        
        if has_unmask and not has_mask:
            print(f"\n   ✅ CORRECT: Generates UNMASK commands")
        elif has_mask:
            print(f"\n   ❌ WRONG: Still generating MASK commands!")
        else:
            print(f"\n   ⚠️  UNKNOWN: No clear mask/unmask commands found")
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
