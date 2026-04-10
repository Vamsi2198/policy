#!/usr/bin/env python3
"""
Policy Audit Tracker
====================

This module tracks policy execution audit logs, recording how many times
each policy has been executed and on which tables/assets.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict


class PolicyAuditTracker:
    """
    Tracks and logs policy execution audits.
    Stores data in JSON files in a structured folder hierarchy.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize the policy audit tracker.
        
        Args:
            base_path: Base directory for storing audit files
        """
        if base_path is None:
            base_path = os.path.join(os.path.dirname(__file__), 'policy_audits')
        
        self.base_path = Path(base_path)
        self._ensure_directory_structure()
        
        # File paths
        self.audit_log_file = self.base_path / 'policy_audit_log.json'
        self.execution_stats_file = self.base_path / 'execution_statistics.json'
        
        # Initialize files if they don't exist
        self._initialize_files()
        
        print(f"✅ Policy Audit Tracker initialized at: {self.base_path}")
    
    def _ensure_directory_structure(self):
        """Create directory structure if it doesn't exist"""
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _initialize_files(self):
        """Initialize audit files with empty structures if they don't exist"""
        if not self.audit_log_file.exists():
            self._save_json(self.audit_log_file, {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "description": "Policy execution audit log"
                },
                "audit_entries": []
            })
        
        if not self.execution_stats_file.exists():
            self._save_json(self.execution_stats_file, {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "policy_statistics": {}
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
    # Audit Logging
    # ============================================
    
    def log_policy_execution(self,
                            policy_name: str,
                            target_table: str,
                            target_columns: List[str],
                            execution_status: str,
                            rows_affected: int = 0,
                            execution_time: float = 0.0,
                            user: str = "system",
                            error_message: str = None,
                            metadata: Dict[str, Any] = None) -> str:
        """
        Log a policy execution.
        
        Args:
            policy_name: Name of the executed policy
            target_table: Table on which policy was executed
            target_columns: Columns affected by the policy
            execution_status: SUCCESS, FAILED, PARTIAL
            rows_affected: Number of rows affected
            execution_time: Execution time in seconds
            user: User who triggered the execution
            error_message: Error message if failed
            metadata: Additional execution metadata
            
        Returns:
            Audit entry ID
        """
        audit_id = str(uuid.uuid4())
        
        audit_entry = {
            "audit_id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "policy_name": policy_name,
            "target_table": target_table,
            "target_columns": target_columns,
            "execution_status": execution_status,
            "rows_affected": rows_affected,
            "execution_time": execution_time,
            "user": user,
            "error_message": error_message,
            "metadata": metadata or {}
        }
        
        # Load existing audit log
        data = self._load_json(self.audit_log_file)
        
        # Add new entry
        data['audit_entries'].append(audit_entry)
        
        # Update metadata
        data['metadata']['last_updated'] = datetime.now().isoformat()
        data['metadata']['total_executions'] = len(data['audit_entries'])
        
        # Save audit log
        self._save_json(self.audit_log_file, data)
        
        # Update statistics
        self._update_statistics(policy_name, target_table, execution_status, rows_affected)
        
        print(f"📊 Policy execution logged: {policy_name} on {target_table} ({execution_status}) - ID: {audit_id}")
        return audit_id
    
    def _update_statistics(self, 
                          policy_name: str, 
                          target_table: str, 
                          status: str,
                          rows_affected: int):
        """Update execution statistics"""
        data = self._load_json(self.execution_stats_file)
        
        # Initialize policy stats if not exists
        if policy_name not in data['policy_statistics']:
            data['policy_statistics'][policy_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_rows_affected": 0,
                "tables_affected": {},
                "first_executed": datetime.now().isoformat(),
                "last_executed": datetime.now().isoformat()
            }
        
        policy_stats = data['policy_statistics'][policy_name]
        
        # Update counts
        policy_stats['total_executions'] += 1
        if status == "SUCCESS":
            policy_stats['successful_executions'] += 1
        elif status == "FAILED":
            policy_stats['failed_executions'] += 1
        
        policy_stats['total_rows_affected'] += rows_affected
        policy_stats['last_executed'] = datetime.now().isoformat()
        
        # Update per-table statistics
        if target_table not in policy_stats['tables_affected']:
            policy_stats['tables_affected'][target_table] = {
                "execution_count": 0,
                "rows_affected": 0,
                "last_executed": None
            }
        
        table_stats = policy_stats['tables_affected'][target_table]
        table_stats['execution_count'] += 1
        table_stats['rows_affected'] += rows_affected
        table_stats['last_executed'] = datetime.now().isoformat()
        
        # Update metadata
        data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Save statistics
        self._save_json(self.execution_stats_file, data)
    
    # ============================================
    # Query Methods
    # ============================================
    
    def get_audit_log(self,
                     policy_name: str = None,
                     target_table: str = None,
                     status: str = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve audit log entries with optional filtering.
        
        Args:
            policy_name: Filter by policy name
            target_table: Filter by target table
            status: Filter by execution status
            limit: Maximum number of entries to return
            
        Returns:
            List of audit entries
        """
        data = self._load_json(self.audit_log_file)
        entries = data.get('audit_entries', [])
        
        # Apply filters
        if policy_name:
            entries = [e for e in entries if e['policy_name'] == policy_name]
        
        if target_table:
            entries = [e for e in entries if e['target_table'] == target_table]
        
        if status:
            entries = [e for e in entries if e['execution_status'] == status]
        
        # Sort by timestamp (most recent first)
        entries.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        return entries[:limit]
    
    def get_policy_statistics(self, policy_name: str = None) -> Dict[str, Any]:
        """
        Get execution statistics for policies.
        
        Args:
            policy_name: Specific policy name (optional, returns all if None)
            
        Returns:
            Statistics dictionary
        """
        data = self._load_json(self.execution_stats_file)
        
        if policy_name:
            return data.get('policy_statistics', {}).get(policy_name, {})
        
        return data.get('policy_statistics', {})
    
    def get_table_audit_summary(self, table_name: str) -> Dict[str, Any]:
        """
        Get audit summary for a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Summary of all policies executed on this table
        """
        data = self._load_json(self.execution_stats_file)
        all_stats = data.get('policy_statistics', {})
        
        table_summary = {
            "table_name": table_name,
            "policies_executed": [],
            "total_executions": 0,
            "total_rows_affected": 0
        }
        
        for policy_name, policy_stats in all_stats.items():
            tables_affected = policy_stats.get('tables_affected', {})
            if table_name in tables_affected:
                table_info = tables_affected[table_name]
                table_summary['policies_executed'].append({
                    "policy_name": policy_name,
                    "execution_count": table_info['execution_count'],
                    "rows_affected": table_info['rows_affected'],
                    "last_executed": table_info['last_executed']
                })
                table_summary['total_executions'] += table_info['execution_count']
                table_summary['total_rows_affected'] += table_info['rows_affected']
        
        return table_summary
    
    def get_recent_executions(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get policy executions from the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of recent executions
        """
        data = self._load_json(self.audit_log_file)
        entries = data.get('audit_entries', [])
        
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        recent_entries = [
            e for e in entries
            if datetime.fromisoformat(e['timestamp']).timestamp() > cutoff_time
        ]
        
        recent_entries.sort(key=lambda x: x['timestamp'], reverse=True)
        return recent_entries
    
    def get_top_policies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top policies by execution count.
        
        Args:
            limit: Number of top policies to return
            
        Returns:
            List of top policies with statistics
        """
        data = self._load_json(self.execution_stats_file)
        all_stats = data.get('policy_statistics', {})
        
        # Create list with policy name and stats
        policy_list = [
            {
                "policy_name": name,
                **stats
            }
            for name, stats in all_stats.items()
        ]
        
        # Sort by total executions
        policy_list.sort(key=lambda x: x['total_executions'], reverse=True)
        
        return policy_list[:limit]
    
    def get_top_tables(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top tables by policy execution count.
        
        Args:
            limit: Number of top tables to return
            
        Returns:
            List of top tables with statistics
        """
        data = self._load_json(self.execution_stats_file)
        all_stats = data.get('policy_statistics', {})
        
        # Aggregate by table
        table_aggregates = defaultdict(lambda: {
            "execution_count": 0,
            "rows_affected": 0,
            "policies": []
        })
        
        for policy_name, policy_stats in all_stats.items():
            for table_name, table_stats in policy_stats.get('tables_affected', {}).items():
                table_aggregates[table_name]['execution_count'] += table_stats['execution_count']
                table_aggregates[table_name]['rows_affected'] += table_stats['rows_affected']
                table_aggregates[table_name]['policies'].append(policy_name)
        
        # Convert to list
        table_list = [
            {
                "table_name": name,
                **stats,
                "policy_count": len(stats['policies'])
            }
            for name, stats in table_aggregates.items()
        ]
        
        # Sort by execution count
        table_list.sort(key=lambda x: x['execution_count'], reverse=True)
        
        return table_list[:limit]
    
    # ============================================
    # Dashboard Data
    # ============================================
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary for dashboard display.
        
        Returns:
            Summary statistics for dashboard
        """
        audit_data = self._load_json(self.audit_log_file)
        stats_data = self._load_json(self.execution_stats_file)
        
        all_entries = audit_data.get('audit_entries', [])
        all_stats = stats_data.get('policy_statistics', {})
        
        # Calculate totals
        total_executions = len(all_entries)
        successful = len([e for e in all_entries if e['execution_status'] == 'SUCCESS'])
        failed = len([e for e in all_entries if e['execution_status'] == 'FAILED'])
        
        # Recent activity
        recent_24h = self.get_recent_executions(hours=24)
        recent_7d = self.get_recent_executions(hours=168)  # 7 days
        
        return {
            "overview": {
                "total_executions": total_executions,
                "successful_executions": successful,
                "failed_executions": failed,
                "success_rate": (successful / total_executions * 100) if total_executions > 0 else 0,
                "total_policies": len(all_stats),
                "recent_24h": len(recent_24h),
                "recent_7d": len(recent_7d)
            },
            "top_policies": self.get_top_policies(limit=5),
            "top_tables": self.get_top_tables(limit=5),
            "recent_executions": recent_24h[:10],
            "storage_location": str(self.base_path)
        }
    
    # ============================================
    # Export Methods
    # ============================================
    
    def export_audit_data(self, output_dir: str = None) -> Dict[str, str]:
        """
        Export audit data to separate files.
        
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
        
        # Export audit log
        audit_file = output_path / f'audit_log_{timestamp}.json'
        audit_data = self._load_json(self.audit_log_file)
        self._save_json(audit_file, audit_data)
        export_files['audit_log'] = str(audit_file)
        
        # Export statistics
        stats_file = output_path / f'statistics_{timestamp}.json'
        stats_data = self._load_json(self.execution_stats_file)
        self._save_json(stats_file, stats_data)
        export_files['statistics'] = str(stats_file)
        
        print(f"📦 Audit data exported to: {output_path}")
        return export_files


# ============================================
# Convenience Functions
# ============================================

def get_audit_tracker(base_path: str = None) -> PolicyAuditTracker:
    """
    Get or create an audit tracker instance.
    
    Args:
        base_path: Base directory for audit storage
        
    Returns:
        PolicyAuditTracker instance
    """
    return PolicyAuditTracker(base_path=base_path)


# ============================================
# Demo / Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Policy Audit Tracker - Demo")
    print("=" * 60)
    
    # Create audit tracker
    tracker = get_audit_tracker()
    
    # Log some policy executions
    print("\n1. Logging Policy Executions:")
    
    # Successful execution
    audit_id1 = tracker.log_policy_execution(
        policy_name="PII_MASKING_POLICY",
        target_table="customers",
        target_columns=["email", "phone", "ssn"],
        execution_status="SUCCESS",
        rows_affected=15000,
        execution_time=2.5,
        user="admin"
    )
    
    # Another successful execution
    audit_id2 = tracker.log_policy_execution(
        policy_name="PII_MASKING_POLICY",
        target_table="employees",
        target_columns=["email", "salary"],
        execution_status="SUCCESS",
        rows_affected=500,
        execution_time=0.8,
        user="system"
    )
    
    # Failed execution
    audit_id3 = tracker.log_policy_execution(
        policy_name="FINANCIAL_DATA_POLICY",
        target_table="transactions",
        target_columns=["account_number"],
        execution_status="FAILED",
        rows_affected=0,
        execution_time=0.1,
        user="system",
        error_message="Connection timeout"
    )
    
    # Get audit log
    print("\n2. Retrieving Audit Log:")
    audit_log = tracker.get_audit_log(limit=5)
    print(f"   Found {len(audit_log)} audit entries")
    for entry in audit_log:
        print(f"   - {entry['policy_name']} on {entry['target_table']} ({entry['execution_status']}) at {entry['timestamp']}")
    
    # Get policy statistics
    print("\n3. Policy Statistics:")
    stats = tracker.get_policy_statistics()
    print(f"   {json.dumps(stats, indent=2)}")
    
    # Get table summary
    print("\n4. Table Audit Summary:")
    table_summary = tracker.get_table_audit_summary("customers")
    print(f"   {json.dumps(table_summary, indent=2)}")
    
    # Get dashboard summary
    print("\n5. Dashboard Summary:")
    dashboard = tracker.get_dashboard_summary()
    print(f"   {json.dumps(dashboard, indent=2)}")
    
    # Export audit data
    print("\n6. Exporting Audit Data:")
    exports = tracker.export_audit_data()
    for key, path in exports.items():
        print(f"   {key}: {path}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
