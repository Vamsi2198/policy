"""
Comprehensive test file for unmask functionality
Tests unmask intent detection, SQL generation, and execution
"""

import snowflake.connector
import yaml
from ai_control_plane import AIControlPlane
from control_pannel import ControlPlaneEngine
import json
from datetime import datetime

def load_config():
    """Load Snowflake configuration"""
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config

def test_1_check_current_masking_policies():
    """Test 1: Check what masking policies currently exist"""
    print("\n" + "="*80)
    print("TEST 1: Checking Current Masking Policies")
    print("="*80)
    
    config = load_config()
    platform = config['platform']
    
    try:
        conn = snowflake.connector.connect(
            account=platform['account'],
            user=platform['user'],
            password=platform['password'],
            warehouse=platform['warehouse'],
            database=platform['database'],
            schema=platform['schema'],
            role=platform['role']
        )
        
        cursor = conn.cursor()
        
        # Show all masking policies
        print("\n📋 Existing Masking Policies:")
        cursor.execute("SHOW MASKING POLICIES")
        policies = cursor.fetchall()
        for policy in policies:
            print(f"  - {policy[1]} (created: {policy[0]})")
        
        # Show which columns have masking policies
        print("\n📋 Columns with Masking Policies Applied:")
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, MASKING_POLICY_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'PUBLIC'
            AND MASKING_POLICY_NAME IS NOT NULL
            ORDER BY TABLE_NAME, COLUMN_NAME
        """)
        masked_columns = cursor.fetchall()
        for row in masked_columns:
            print(f"  - {row[0]}.{row[1]} → {row[2]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Test 1 PASSED: Successfully queried current state")
        return True, policies, masked_columns
        
    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {str(e)}")
        return False, None, None

def test_2_unmask_intent_recognition():
    """Test 2: Verify unmask intent is correctly detected"""
    print("\n" + "="*80)
    print("TEST 2: Testing Unmask Intent Recognition")
    print("="*80)
    
    test_queries = [
        "unmask the customers table",
        "remove masking from customers",
        "unmask pii in customers",
        "remove masking policies from customers table",
        "disable masking on customers"
    ]
    
    config = load_config()
    engine = ControlPlaneEngine(config)
    control_plane = AIControlPlane(engine, config)
    
    results = []
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            # Call the intent recognition
            result = control_plane.process(query)
            intent = result.get('intent', 'unknown')
            print(f"   Detected intent: {intent}")
            
            # Check if intent is correctly identified
            if 'unmask' in intent.lower() or 'remove' in intent.lower():
                print(f"   ✅ Correctly identified as unmask operation")
                results.append(True)
            else:
                print(f"   ❌ WRONG! Detected as '{intent}' instead of unmask")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Intent Recognition Success Rate: {success_rate:.1f}%")
    
    if all(results):
        print("✅ Test 2 PASSED: All unmask queries correctly identified")
        return True
    else:
        print("❌ Test 2 FAILED: Some queries misidentified")
        return False

def test_3_unmask_sql_generation():
    """Test 3: Generate unmask SQL commands"""
    print("\n" + "="*80)
    print("TEST 3: Testing Unmask SQL Generation")
    print("="*80)
    
    config = load_config()
    engine = ControlPlaneEngine(config)
    control_plane = AIControlPlane(engine, config)
    
    query = "unmask all pii columns in customers table"
    print(f"\n🔍 Query: '{query}'")
    
    try:
        result = control_plane.process(query)
        
        print(f"\n📋 Intent: {result.get('intent', 'unknown')}")
        print(f"📋 Status: {result.get('status', 'unknown')}")
        
        # Check phases
        phases = result.get('phases', {})
        
        # Check PLAN phase for SQL commands
        plan_phase = phases.get('PLAN', {})
        sql_commands = plan_phase.get('sql_commands', [])
        
        print(f"\n📋 Generated SQL Commands ({len(sql_commands)} commands):")
        for i, cmd in enumerate(sql_commands, 1):
            print(f"\n  Command {i}:")
            print(f"    {cmd[:200]}..." if len(cmd) > 200 else f"    {cmd}")
        
        # Validate commands contain unmask operations
        unmask_keywords = ['ALTER TABLE', 'UNSET MASKING POLICY', 'DROP MASKING POLICY']
        valid_commands = []
        
        for cmd in sql_commands:
            cmd_upper = cmd.upper()
            if 'UNSET MASKING POLICY' in cmd_upper or 'DROP MASKING POLICY' in cmd_upper:
                valid_commands.append(True)
            else:
                valid_commands.append(False)
                print(f"\n⚠️  Warning: Command doesn't contain UNSET/DROP: {cmd[:100]}")
        
        if valid_commands and all(valid_commands):
            print("\n✅ Test 3 PASSED: All commands are valid unmask operations")
            return True, sql_commands
        else:
            print("\n❌ Test 3 FAILED: Commands don't appear to be unmask operations")
            return False, sql_commands
            
    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, []

def test_4_execute_unmask():
    """Test 4: Execute unmask workflow"""
    print("\n" + "="*80)
    print("TEST 4: Executing Unmask Workflow")
    print("="*80)
    
    config = load_config()
    platform = config['platform']
    
    try:
        conn = snowflake.connector.connect(
            account=platform['account'],
            user=platform['user'],
            password=platform['password'],
            warehouse=platform['warehouse'],
            database=platform['database'],
            schema=platform['schema'],
            role=platform['role']
        )
        
        cursor = conn.cursor()
        
        # Get masked columns
        print("\n📋 Finding masked columns to unmask...")
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME, MASKING_POLICY_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'PUBLIC'
            AND TABLE_NAME = 'CUSTOMERS'
            AND MASKING_POLICY_NAME IS NOT NULL
        """)
        masked_columns = cursor.fetchall()
        
        print(f"Found {len(masked_columns)} masked columns:")
        for row in masked_columns:
            print(f"  - {row[0]}.{row[1]} → {row[2]}")
        
        if not masked_columns:
            print("\n⚠️  No masked columns found. Nothing to unmask.")
            return True
        
        # Unmask each column
        print("\n🔧 Unmasking columns...")
        unmasked_count = 0
        policies_to_drop = set()
        
        for table_name, column_name, policy_name in masked_columns:
            try:
                sql = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} UNSET MASKING POLICY"
                print(f"\n  Executing: {sql}")
                cursor.execute(sql)
                print(f"  ✅ Unmasked {table_name}.{column_name}")
                unmasked_count += 1
                policies_to_drop.add(policy_name)
            except Exception as e:
                print(f"  ❌ Failed to unmask {table_name}.{column_name}: {str(e)}")
        
        # Drop the masking policies
        print(f"\n🔧 Dropping {len(policies_to_drop)} masking policies...")
        for policy_name in policies_to_drop:
            try:
                sql = f"DROP MASKING POLICY IF EXISTS {policy_name}"
                print(f"\n  Executing: {sql}")
                cursor.execute(sql)
                print(f"  ✅ Dropped policy {policy_name}")
            except Exception as e:
                print(f"  ❌ Failed to drop policy {policy_name}: {str(e)}")
        
        # Verify policies are removed
        print("\n📋 Verifying unmask completed...")
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'PUBLIC'
            AND TABLE_NAME = 'CUSTOMERS'
            AND MASKING_POLICY_NAME IS NOT NULL
        """)
        remaining_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 Results:")
        print(f"  - Unmasked columns: {unmasked_count}")
        print(f"  - Dropped policies: {len(policies_to_drop)}")
        print(f"  - Remaining masked columns: {remaining_count}")
        
        if remaining_count == 0:
            print("\n✅ Test 4 PASSED: All masking policies successfully removed")
            return True
        else:
            print("\n⚠️  Test 4 WARNING: Some masked columns remain")
            return False
            
    except Exception as e:
        print(f"\n❌ Test 4 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_5_verify_unmask_complete():
    """Test 5: Verify no masking policies remain"""
    print("\n" + "="*80)
    print("TEST 5: Verifying Unmask Completion")
    print("="*80)
    
    config = load_config()
    platform = config['platform']
    
    try:
        conn = snowflake.connector.connect(
            account=platform['account'],
            user=platform['user'],
            password=platform['password'],
            warehouse=platform['warehouse'],
            database=platform['database'],
            schema=platform['schema'],
            role=platform['role']
        )
        
        cursor = conn.cursor()
        
        # Check for any masking policies
        cursor.execute("SHOW MASKING POLICIES")
        policies = cursor.fetchall()
        
        print(f"\n📋 Remaining Masking Policies: {len(policies)}")
        for policy in policies:
            print(f"  - {policy[1]}")
        
        # Check for any masked columns
        cursor.execute("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'PUBLIC'
            AND MASKING_POLICY_NAME IS NOT NULL
        """)
        masked_count = cursor.fetchone()[0]
        
        print(f"📋 Masked Columns: {masked_count}")
        
        cursor.close()
        conn.close()
        
        if len(policies) == 0 and masked_count == 0:
            print("\n✅ Test 5 PASSED: All masking completely removed")
            return True
        else:
            print("\n⚠️  Test 5 WARNING: Some masking artifacts remain")
            return False
            
    except Exception as e:
        print(f"\n❌ Test 5 FAILED: {str(e)}")
        return False

def run_all_tests():
    """Run all unmask tests"""
    print("\n" + "="*80)
    print("🚀 UNMASK WORKFLOW COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # Test 1: Check current state
    results['test_1'], policies, masked_columns = test_1_check_current_masking_policies()
    
    # Test 2: Intent recognition (only if we have masked data)
    if masked_columns:
        results['test_2'] = test_2_unmask_intent_recognition()
        
        # Test 3: SQL generation
        results['test_3'], sql_commands = test_3_unmask_sql_generation()
    else:
        print("\n⚠️  Skipping tests 2-3: No masked columns found")
        results['test_2'] = None
        results['test_3'] = None
    
    # Test 4: Execute unmask
    results['test_4'] = test_4_execute_unmask()
    
    # Test 5: Verify completion
    results['test_5'] = test_5_verify_unmask_complete()
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    run_all_tests()
