#!/usr/bin/env python3
"""
Test S3 Data Processing Workflow
=================================
This script demonstrates the complete S3 → Masking → Snowflake workflow.

Usage:
    python test_s3_workflow.py
"""

import os
import sys

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_s3_chatbot():
    """Test the S3 chatbot interface"""
    print("="*80)
    print("🧪 TESTING S3 DATA CHATBOT WORKFLOW")
    print("="*80)
    print("\nThis test will:")
    print("1. Load data from s3.json")
    print("2. Apply masking policies based on your query")
    print("3. Insert masked data into Snowflake MY_TABLE")
    print("="*80)
    
    try:
        from control_pannel import run_s3_data_chatbot
        
        print("\n✅ Starting S3 Data Chatbot...")
        print("You can type queries like:")
        print("  - 'Mask all email addresses'")
        print("  - 'Hide SSN and salary data'")
        print("  - 'Protect all PII and insert to Snowflake'")
        print("\n" + "="*80)
        
        run_s3_data_chatbot()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n💡 Make sure you're running from the src directory:")
        print("   cd src")
        print("   python test_s3_workflow.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_s3_direct():
    """Test direct S3 processing without chatbot"""
    print("="*80)
    print("🧪 TESTING DIRECT S3 DATA PROCESSING")
    print("="*80)
    
    try:
        from s3_data_handler import S3DataHandler, SnowflakeInserter
        from control_pannel import ControlPlaneEngine
        
        # Load S3 data
        print("\n📂 Loading S3 data...")
        s3_handler = S3DataHandler()
        print(f"✅ Loaded {len(s3_handler.original_data)} records")
        
        # Show schema
        schema = s3_handler.get_schema()
        print(f"\n📊 Schema: {len(schema['columns'])} columns")
        for col in schema['columns']:
            print(f"   - {col['name']} ({col['type']})")
        
        # Apply masking
        print("\n🔐 Applying masking policies...")
        test_query = "Mask all email and SSN data"
        policy_result = s3_handler.apply_masking_policies(test_query)
        
        print(f"✅ Applied {len(policy_result.policies_applied)} policies:")
        for policy in policy_result.policies_applied:
            print(f"   🛡️  {policy['field']}: {policy['policy']}")
        
        # Show before/after
        print("\n📋 BEFORE (First record):")
        print(f"   {policy_result.original_data[0]}")
        
        print("\n📋 AFTER (First record):")
        print(f"   {policy_result.masked_data[0]}")
        
        # Connect to Snowflake
        print("\n🔌 Connecting to Snowflake...")
        engine = ControlPlaneEngine()
        if engine.connect_platform():
            print("✅ Connected to Snowflake")
            
            # Prepare and insert
            print("\n📊 Preparing data for Snowflake...")
            snowflake_records = s3_handler.prepare_for_snowflake_insert(policy_result.masked_data)
            print(f"✅ Prepared {len(snowflake_records)} records")
            
            print("\n🚀 Inserting to MY_TABLE...")
            inserter = SnowflakeInserter(engine.connector)
            insert_result = inserter.insert_data(snowflake_records)
            
            if insert_result['success']:
                print(f"✅ Successfully inserted {insert_result['rows_inserted']} rows")
                
                # Verify
                verification = inserter.verify_insertion()
                print(f"\n📊 Verification:")
                print(f"   Total rows in MY_TABLE: {verification['total_rows']}")
                print(f"\n   Sample from MY_TABLE:")
                for i, row in enumerate(verification.get('sample_data', [])[:2], 1):
                    print(f"   {i}. ID={row.get('ID')}, Data={row.get('DATA')[:80]}...")
            else:
                print(f"❌ Insertion failed: {insert_result.get('error')}")
        else:
            print("❌ Failed to connect to Snowflake")
            print("   (This is expected if config.yaml is not set up)")
        
        print("\n" + "="*80)
        print("✅ Direct S3 processing test completed!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_ai_control_plane_s3():
    """Test S3 processing through AI Control Plane"""
    print("="*80)
    print("🧪 TESTING AI CONTROL PLANE S3 WORKFLOW")
    print("="*80)
    
    try:
        from ai_control_plane import AIControlPlane
        
        print("\n🤖 Initializing AI Control Plane...")
        ai_control = AIControlPlane()
        print("✅ AI Control Plane initialized")
        
        test_query = "Mask all sensitive PII data and insert to Snowflake"
        print(f"\n🎯 Processing query: '{test_query}'")
        
        def progress_callback(phase, total, name, message):
            print(f"   [{phase}/{total}] {name}: {message}")
        
        print("\n📡 Processing with 5-phase S3 workflow...")
        results = ai_control.process_s3_data(
            test_query,
            progress_callback=progress_callback
        )
        
        print(f"\n✅ Processing completed!")
        print(f"   Status: {results.get('status')}")
        print(f"   Source: {results.get('source')}")
        print(f"   Target: {results.get('target')}")
        
        if 'phases' in results:
            print(f"\n📊 Phase Results:")
            for phase_name, phase_data in results['phases'].items():
                print(f"   {phase_name.upper()}: {phase_data.get('status')}")
        
        print("\n" + "="*80)
        print("✅ AI Control Plane S3 test completed!")
        print("="*80)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   AI Control Plane not available")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test S3 Data Processing Workflow')
    parser.add_argument('--chatbot', action='store_true', help='Run S3 chatbot (interactive)')
    parser.add_argument('--direct', action='store_true', help='Run direct S3 processing test')
    parser.add_argument('--ai', action='store_true', help='Run AI Control Plane S3 test')
    parser.add_argument('--all', action='store_true', help='Run all tests (non-interactive)')
    
    args = parser.parse_args()
    
    if args.chatbot:
        test_s3_chatbot()
    elif args.direct:
        test_s3_direct()
    elif args.ai:
        test_ai_control_plane_s3()
    elif args.all:
        print("\n" + "="*80)
        print("🧪 RUNNING ALL S3 WORKFLOW TESTS")
        print("="*80 + "\n")
        
        print("\n1️⃣ DIRECT S3 PROCESSING TEST")
        print("-"*80)
        test_s3_direct()
        
        print("\n\n2️⃣ AI CONTROL PLANE S3 TEST")
        print("-"*80)
        test_ai_control_plane_s3()
        
        print("\n\n" + "="*80)
        print("✅ ALL TESTS COMPLETED!")
        print("="*80)
        print("\n💡 To run the interactive chatbot, use:")
        print("   python test_s3_workflow.py --chatbot")
    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("   python test_s3_workflow.py --chatbot    # Interactive chatbot")
        print("   python test_s3_workflow.py --direct     # Direct processing test")
        print("   python test_s3_workflow.py --ai         # AI Control Plane test")
        print("   python test_s3_workflow.py --all        # Run all tests")

if __name__ == '__main__':
    main()
