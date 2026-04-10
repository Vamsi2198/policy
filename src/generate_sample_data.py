#!/usr/bin/env python3
"""
Generate Sample Data for Metadata and Audit
============================================

This script populates sample data for demonstration.
"""

import sys
import os

# Add the src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from atlan_metadata_store import get_metadata_store
from policy_audit_tracker import get_audit_tracker
from datetime import datetime, timedelta
import random

def generate_sample_metadata():
    """Generate sample metadata"""
    print("📝 Generating sample metadata...")
    store = get_metadata_store()
    
    policies = [
        "PII_MASKING_POLICY",
        "FINANCIAL_DATA_POLICY",
        "GDPR_COMPLIANCE_POLICY",
        "EMAIL_MASKING_POLICY"
    ]
    
    tables = ["CUSTOMERS", "EMPLOYEES", "TRANSACTIONS", "ORDERS"]
    
    # Generate policy changes
    for i in range(10):
        policy = random.choice(policies)
        table = random.choice(tables)
        change_type = random.choice(["CREATE", "UPDATE", "APPLY"])
        
        store.add_policy_change(
            policy_name=policy,
            change_type=change_type,
            affected_assets=[f"PUBLIC.{table}.EMAIL", f"PUBLIC.{table}.PHONE"],
            change_details={
                "masking_type": "EMAIL_MASK",
                "columns": ["EMAIL", "PHONE"],
                "table": table
            },
            user="admin" if i % 2 == 0 else "system"
        )
    
    # Generate lineage
    for i in range(15):
        source_table = random.choice(tables)
        target_table = random.choice(tables)
        
        store.add_lineage_entry(
            source_asset=f"RAW.{source_table}",
            target_asset=f"STAGING.{target_table}_MASKED",
            transformation=random.choice(["PII_MASKING", "DATA_TRANSFORM", "AGGREGATION"]),
            lineage_type=random.choice(["DATAFLOW", "PROCESS", "POLICY"]),
            process_name=f"etl_workflow_{i}"
        )
    
    print("✅ Sample metadata generated!")

def generate_sample_audit():
    """Generate sample audit data"""
    print("📊 Generating sample audit data...")
    tracker = get_audit_tracker()
    
    policies = [
        "PII_MASKING_POLICY",
        "FINANCIAL_DATA_POLICY",
        "GDPR_COMPLIANCE_POLICY",
        "EMAIL_MASKING_POLICY"
    ]
    
    tables = ["CUSTOMERS", "EMPLOYEES", "TRANSACTIONS", "ORDERS"]
    
    # Generate audit logs
    for i in range(20):
        policy = random.choice(policies)
        table = random.choice(tables)
        status = random.choice(["SUCCESS", "SUCCESS", "SUCCESS", "FAILED"])  # 75% success rate
        
        tracker.log_policy_execution(
            policy_name=policy,
            target_table=table,
            target_columns=["EMAIL", "PHONE", "SSN"][:random.randint(1, 3)],
            execution_status=status,
            rows_affected=random.randint(100, 50000) if status == "SUCCESS" else 0,
            execution_time=random.uniform(0.5, 10.0),
            user="admin" if i % 3 == 0 else "system",
            error_message="Connection timeout" if status == "FAILED" else None
        )
    
    print("✅ Sample audit data generated!")

def main():
    """Main function"""
    print("\n" + "="*60)
    print("  Generating Sample Data for Dashboard")
    print("="*60 + "\n")
    
    try:
        generate_sample_metadata()
        generate_sample_audit()
        
        print("\n" + "="*60)
        print("  ✅ Sample Data Generation Complete!")
        print("="*60)
        print("\nRefresh your browser to see the data!")
        print("Navigate to: http://localhost:5000")
        print("\nTabs:")
        print("  📊 Atlan Metadata - View policy changes and lineage")
        print("  📋 Audit Logs - View execution statistics and logs")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
