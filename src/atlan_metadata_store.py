#!/usr/bin/env python3
"""
Atlan Metadata Store
====================

This module manages metadata storage for policy changes and lineage
information stored in Atlan, using JSON files for persistence.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class AtlanMetadataStore:
    """
    Manages metadata storage for Atlan policy changes and lineage.
    Stores data in JSON files in a structured folder hierarchy.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize the metadata store.
        
        Args:
            base_path: Base directory for storing metadata files
        """
        if base_path is None:
            base_path = os.path.join(os.path.dirname(__file__), 'atlan_metadata')
        
        self.base_path = Path(base_path)
        self._ensure_directory_structure()
        
        # File paths
        self.policy_changes_file = self.base_path / 'policy_changes.json'
        self.lineage_file = self.base_path / 'lineage_metadata.json'
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        print(f"✅ Atlan Metadata Store initialized at: {self.base_path}")
    
    def _ensure_directory_structure(self):
        """Create directory structure if it doesn't exist"""
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _initialize_files(self):
        """Initialize metadata files with empty structures if they don't exist"""
        if not self.policy_changes_file.exists():
            self._save_json(self.policy_changes_file, {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "description": "Policy changes metadata stored in Atlan"
                },
                "changes": []
            })
        
        if not self.lineage_file.exists():
            self._save_json(self.lineage_file, {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "description": "Data lineage metadata stored in Atlan"
                },
                "lineage_entries": []
            })
    
    def _load_json(self, filepath: Path) -> Dict[str, Any]:
        """Load JSON data from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, filepath: Path, data: Dict[str, Any]):
        """Save JSON data to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ============================================
    # Policy Changes Management
    # ============================================
    
    def add_policy_change(self, 
                         policy_name: str,
                         change_type: str,
                         affected_assets: List[str],
                         change_details: Dict[str, Any],
                         atlan_guid: str = None,
                         user: str = "system") -> str:
        """
        Record a policy change in the metadata store.
        
        Args:
            policy_name: Name of the policy
            change_type: Type of change (CREATE, UPDATE, DELETE, APPLY)
            affected_assets: List of affected asset GUIDs or names
            change_details: Detailed information about the change
            atlan_guid: Atlan GUID for this policy
            user: User who made the change
            
        Returns:
            Change record ID
        """
        change_id = str(uuid.uuid4())
        
        # ADDED: Enhanced logging to track what policy is being applied to which table
        log_message = f"\n📝 POLICY CHANGE: {policy_name} ({change_type}) on {affected_assets}"
        if change_details:
            log_message += f"\n   Table: {change_details.get('table', 'N/A')}"
            log_message += f"\n   Columns: {change_details.get('columns', [])}"
        
        change_record = {
            "change_id": change_id,
            "timestamp": datetime.now().isoformat(),
            "policy_name": policy_name,
            "change_type": change_type,
            "affected_assets": affected_assets,
            "change_details": change_details,
            "atlan_guid": atlan_guid or f"atlan_policy_{uuid.uuid4().hex[:8]}",
            "user": user,
            "status": "COMPLETED",
            "atlan_synced": True
        }
        
        # Load existing data
        data = self._load_json(self.policy_changes_file)
        
        # Add new change
        data['changes'].append(change_record)
        
        # Update metadata
        data['metadata']['last_updated'] = datetime.now().isoformat()
        data['metadata']['total_changes'] = len(data['changes'])
        
        # Save
        self._save_json(self.policy_changes_file, data)
        
        print(f"📝 Policy change recorded: {policy_name} ({change_type}) - ID: {change_id}")
        return change_id
    
    def get_policy_changes(self, 
                          policy_name: str = None,
                          change_type: str = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve policy changes with optional filtering.
        
        Args:
            policy_name: Filter by policy name
            change_type: Filter by change type
            limit: Maximum number of records to return
            
        Returns:
            List of change records
        """
        data = self._load_json(self.policy_changes_file)
        changes = data.get('changes', [])
        
        # Apply filters
        if policy_name:
            changes = [c for c in changes if c['policy_name'] == policy_name]
        
        if change_type:
            changes = [c for c in changes if c['change_type'] == change_type]
        
        # Sort by timestamp (most recent first)
        changes.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        return changes[:limit]
    
    def get_policy_history(self, policy_name: str) -> List[Dict[str, Any]]:
        """
        Get complete history of changes for a specific policy.
        
        Args:
            policy_name: Name of the policy
            
        Returns:
            List of all changes for this policy
        """
        return self.get_policy_changes(policy_name=policy_name, limit=None)
    
    def get_recent_changes(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get policy changes from the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent changes
        """
        data = self._load_json(self.policy_changes_file)
        changes = data.get('changes', [])
        
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        recent_changes = [
            c for c in changes
            if datetime.fromisoformat(c['timestamp']).timestamp() > cutoff_time
        ]
        
        recent_changes.sort(key=lambda x: x['timestamp'], reverse=True)
        return recent_changes
    
    # ============================================
    # Lineage Management
    # ============================================
    
    def add_lineage_entry(self,
                         source_asset: str,
                         target_asset: str,
                         transformation: str,
                         lineage_type: str = "DATAFLOW",
                         process_name: str = None,
                         atlan_guid: str = None,
                         metadata: Dict[str, Any] = None) -> str:
        """
        Record a data lineage entry.
        
        Args:
            source_asset: Source asset identifier
            target_asset: Target asset identifier
            transformation: Description of transformation
            lineage_type: Type of lineage (DATAFLOW, PROCESS, POLICY)
            process_name: Name of the process/workflow
            atlan_guid: Atlan GUID for this lineage
            metadata: Additional metadata
            
        Returns:
            Lineage entry ID
        """
        lineage_id = str(uuid.uuid4())
        
        lineage_entry = {
            "lineage_id": lineage_id,
            "timestamp": datetime.now().isoformat(),
            "source_asset": source_asset,
            "target_asset": target_asset,
            "transformation": transformation,
            "lineage_type": lineage_type,
            "process_name": process_name or "unknown_process",
            "atlan_guid": atlan_guid or f"atlan_lineage_{uuid.uuid4().hex[:8]}",
            "metadata": metadata or {},
            "atlan_synced": True
        }
        
        # Load existing data
        data = self._load_json(self.lineage_file)
        
        # Add new entry
        data['lineage_entries'].append(lineage_entry)
        
        # Update metadata
        data['metadata']['last_updated'] = datetime.now().isoformat()
        data['metadata']['total_entries'] = len(data['lineage_entries'])
        
        # Save
        self._save_json(self.lineage_file, data)
        
        print(f"🔗 Lineage entry recorded: {source_asset} -> {target_asset} - ID: {lineage_id}")
        return lineage_id
    
    def get_lineage_entries(self,
                           asset: str = None,
                           lineage_type: str = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve lineage entries with optional filtering.
        
        Args:
            asset: Filter by source or target asset
            lineage_type: Filter by lineage type
            limit: Maximum number of records to return
            
        Returns:
            List of lineage entries
        """
        data = self._load_json(self.lineage_file)
        entries = data.get('lineage_entries', [])
        
        # Apply filters
        if asset:
            entries = [e for e in entries 
                      if e['source_asset'] == asset or e['target_asset'] == asset]
        
        if lineage_type:
            entries = [e for e in entries if e['lineage_type'] == lineage_type]
        
        # Sort by timestamp (most recent first)
        entries.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        return entries[:limit]
    
    def get_upstream_lineage(self, asset: str, depth: int = 3) -> List[Dict[str, Any]]:
        """
        Get upstream lineage for an asset.
        
        Args:
            asset: Asset identifier
            depth: Maximum depth to traverse
            
        Returns:
            List of upstream lineage entries
        """
        data = self._load_json(self.lineage_file)
        entries = data.get('lineage_entries', [])
        
        upstream = []
        current_assets = {asset}
        
        for _ in range(depth):
            new_assets = set()
            for entry in entries:
                if entry['target_asset'] in current_assets:
                    upstream.append(entry)
                    new_assets.add(entry['source_asset'])
            
            if not new_assets:
                break
            current_assets = new_assets
        
        return upstream
    
    def get_downstream_lineage(self, asset: str, depth: int = 3) -> List[Dict[str, Any]]:
        """
        Get downstream lineage for an asset.
        
        Args:
            asset: Asset identifier
            depth: Maximum depth to traverse
            
        Returns:
            List of downstream lineage entries
        """
        data = self._load_json(self.lineage_file)
        entries = data.get('lineage_entries', [])
        
        downstream = []
        current_assets = {asset}
        
        for _ in range(depth):
            new_assets = set()
            for entry in entries:
                if entry['source_asset'] in current_assets:
                    downstream.append(entry)
                    new_assets.add(entry['target_asset'])
            
            if not new_assets:
                break
            current_assets = new_assets
        
        return downstream
    
    # ============================================
    # Statistics and Summary
    # ============================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics for the metadata store.
        
        Returns:
            Dictionary with statistics
        """
        policy_data = self._load_json(self.policy_changes_file)
        lineage_data = self._load_json(self.lineage_file)
        
        # Count changes by type
        changes = policy_data.get('changes', [])
        change_types = {}
        for change in changes:
            change_type = change['change_type']
            change_types[change_type] = change_types.get(change_type, 0) + 1
        
        # Count lineage by type
        entries = lineage_data.get('lineage_entries', [])
        lineage_types = {}
        for entry in entries:
            lineage_type = entry['lineage_type']
            lineage_types[lineage_type] = lineage_types.get(lineage_type, 0) + 1
        
        # Recent activity (last 24 hours)
        recent_changes = self.get_recent_changes(hours=24)
        
        return {
            "policy_changes": {
                "total": len(changes),
                "by_type": change_types,
                "recent_24h": len(recent_changes)
            },
            "lineage_entries": {
                "total": len(entries),
                "by_type": lineage_types
            },
            "storage_location": str(self.base_path),
            "last_policy_update": policy_data.get('metadata', {}).get('last_updated'),
            "last_lineage_update": lineage_data.get('metadata', {}).get('last_updated')
        }
    
    def export_all_metadata(self, output_dir: str = None) -> Dict[str, str]:
        """
        Export all metadata to separate files.
        
        Args:
            output_dir: Directory for export files
            
        Returns:
            Dictionary with export file paths
        """
        if output_dir is None:
            output_dir = self.base_path / 'exports'
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        export_files = {}
        
        # Export policy changes
        policy_file = output_path / f'policy_changes_{timestamp}.json'
        policy_data = self._load_json(self.policy_changes_file)
        self._save_json(policy_file, policy_data)
        export_files['policy_changes'] = str(policy_file)
        
        # Export lineage
        lineage_file = output_path / f'lineage_{timestamp}.json'
        lineage_data = self._load_json(self.lineage_file)
        self._save_json(lineage_file, lineage_data)
        export_files['lineage'] = str(lineage_file)
        
        print(f"📦 Metadata exported to: {output_path}")
        return export_files


# ============================================
# Convenience Functions
# ============================================

def get_metadata_store(base_path: str = None) -> AtlanMetadataStore:
    """
    Get or create a metadata store instance.
    
    Args:
        base_path: Base directory for metadata storage
        
    Returns:
        AtlanMetadataStore instance
    """
    return AtlanMetadataStore(base_path=base_path)


# ============================================
# Demo / Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Atlan Metadata Store - Demo")
    print("=" * 60)
    
    # Create metadata store
    store = get_metadata_store()
    
    # Add policy changes
    print("\n1. Adding Policy Changes:")
    change_id1 = store.add_policy_change(
        policy_name="PII_MASKING_POLICY",
        change_type="CREATE",
        affected_assets=["customers.email", "customers.phone"],
        change_details={
            "masking_type": "EMAIL_MASK",
            "columns": ["email", "phone"],
            "table": "customers"
        },
        user="admin"
    )
    
    change_id2 = store.add_policy_change(
        policy_name="PII_MASKING_POLICY",
        change_type="APPLY",
        affected_assets=["customers.email"],
        change_details={
            "rows_affected": 15000,
            "execution_time": 2.5
        },
        user="system"
    )
    
    # Add lineage entries
    print("\n2. Adding Lineage Entries:")
    lineage_id1 = store.add_lineage_entry(
        source_asset="raw.customers",
        target_asset="staging.customers_masked",
        transformation="PII_MASKING",
        lineage_type="POLICY",
        process_name="pii_masking_workflow",
        metadata={"policy": "PII_MASKING_POLICY"}
    )
    
    lineage_id2 = store.add_lineage_entry(
        source_asset="staging.customers_masked",
        target_asset="prod.customers",
        transformation="DATA_SYNC",
        lineage_type="DATAFLOW",
        process_name="daily_etl"
    )
    
    # Get policy changes
    print("\n3. Retrieving Policy Changes:")
    changes = store.get_policy_changes(limit=5)
    print(f"   Found {len(changes)} policy changes")
    for change in changes:
        print(f"   - {change['policy_name']} ({change['change_type']}) at {change['timestamp']}")
    
    # Get lineage
    print("\n4. Retrieving Lineage:")
    lineage = store.get_lineage_entries(limit=5)
    print(f"   Found {len(lineage)} lineage entries")
    for entry in lineage:
        print(f"   - {entry['source_asset']} -> {entry['target_asset']} ({entry['transformation']})")
    
    # Get statistics
    print("\n5. Statistics:")
    stats = store.get_statistics()
    print(f"   {json.dumps(stats, indent=2)}")
    
    # Export metadata
    print("\n6. Exporting Metadata:")
    exports = store.export_all_metadata()
    for key, path in exports.items():
        print(f"   {key}: {path}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
