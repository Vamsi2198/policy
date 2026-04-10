#!/usr/bin/env python3
"""
Initialize Metadata Store and Audit Tracker
"""

import os
import json
from pathlib import Path
from datetime import datetime

def init_metadata_store():
    """Initialize the metadata store with required JSON files"""
    
    base_path = Path("atlan_metadata")
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize policy_changes.json
    policy_changes_file = base_path / "policy_changes.json"
    if not policy_changes_file.exists():
        policy_changes = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Policy changes metadata stored in Atlan"
            },
            "changes": []
        }
        with open(policy_changes_file, 'w') as f:
            json.dump(policy_changes, f, indent=2)
        print(f"✅ Created: {policy_changes_file}")
    else:
        print(f"✅ Already exists: {policy_changes_file}")
    
    # Initialize lineage_metadata.json
    lineage_file = base_path / "lineage_metadata.json"
    if not lineage_file.exists():
        lineage = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Data lineage metadata stored in Atlan"
            },
            "lineage_entries": []
        }
        with open(lineage_file, 'w') as f:
            json.dump(lineage, f, indent=2)
        print(f"✅ Created: {lineage_file}")
    else:
        print(f"✅ Already exists: {lineage_file}")

def init_audit_tracker():
    """Initialize the audit tracker with required JSON files"""
    
    base_path = Path("policy_audits")
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize audit_log.json
    audit_log_file = base_path / "audit_log.json"
    if not audit_log_file.exists():
        audit_log = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Policy audit log"
            },
            "audits": []
        }
        with open(audit_log_file, 'w') as f:
            json.dump(audit_log, f, indent=2)
        print(f"✅ Created: {audit_log_file}")
    else:
        print(f"✅ Already exists: {audit_log_file}")
    
    # Initialize compliance_log.json
    compliance_log_file = base_path / "compliance_log.json"
    if not compliance_log_file.exists():
        compliance_log = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "Compliance audit log"
            },
            "compliance_records": []
        }
        with open(compliance_log_file, 'w') as f:
            json.dump(compliance_log, f, indent=2)
        print(f"✅ Created: {compliance_log_file}")
    else:
        print(f"✅ Already exists: {compliance_log_file}")

if __name__ == "__main__":
    print("Initializing metadata and audit stores...\n")
    
    try:
        init_metadata_store()
        print()
        init_audit_tracker()
        print("\n✅ All metadata and audit stores initialized successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
