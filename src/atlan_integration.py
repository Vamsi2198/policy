#!/usr/bin/env python3
"""
Atlan Integration Module - Mock API Connectivity
=================================================

This module provides mock API connectivity for Atlan integration,
simulating the behavior of the Atlan API for development and testing purposes.
"""

import os
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AtlanAsset:
    """Represents an Atlan asset (table, column, etc.)"""
    guid: str
    qualified_name: str
    name: str
    type_name: str
    status: str = "ACTIVE"
    attributes: Dict[str, Any] = None
    classifications: List[str] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.classifications is None:
            self.classifications = []


@dataclass
class AtlanPolicy:
    """Represents an Atlan governance policy"""
    guid: str
    name: str
    description: str
    policy_type: str
    status: str = "ACTIVE"
    resources: List[str] = None
    actions: List[str] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.resources is None:
            self.resources = []
        if self.actions is None:
            self.actions = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


class MockAtlanAPI:
    """
    Mock Atlan API client that simulates API responses
    for development and testing without requiring actual Atlan connectivity.
    """
    
    def __init__(self, base_url: str = None, api_token: str = None):
        """
        Initialize the mock Atlan API client.
        
        Args:
            base_url: Atlan instance base URL (ignored in mock mode)
            api_token: API token for authentication (ignored in mock mode)
        """
        self.base_url = base_url or "https://mock.atlan.com"
        self.api_token = api_token or "mock_token_123"
        self.mock_mode = True
        
        # Initialize mock data storage
        self._assets: Dict[str, AtlanAsset] = {}
        self._policies: Dict[str, AtlanPolicy] = {}
        self._lineage: Dict[str, List[str]] = {}
        self._audit_logs: List[Dict[str, Any]] = []
        
        # Initialize with some sample data
        self._initialize_mock_data()
        
        print(f"✅ Mock Atlan API initialized (Mode: MOCK)")
        print(f"   Base URL: {self.base_url}")
        print(f"   Assets: {len(self._assets)}")
        print(f"   Policies: {len(self._policies)}")
    
    def _initialize_mock_data(self):
        """Initialize mock data for testing"""
        # Create mock tables
        tables = [
            ("customers", "default.customers", ["customer_id", "name", "email", "phone", "ssn"]),
            ("orders", "default.orders", ["order_id", "customer_id", "amount", "order_date"]),
            ("employees", "default.employees", ["emp_id", "name", "email", "salary", "department"]),
            ("transactions", "default.transactions", ["txn_id", "account_number", "amount", "timestamp"])
        ]
        
        for table_name, qualified_name, columns in tables:
            # Create table asset
            table_guid = f"table_{table_name}_{random.randint(1000, 9999)}"
            table_asset = AtlanAsset(
                guid=table_guid,
                qualified_name=qualified_name,
                name=table_name,
                type_name="Table",
                attributes={
                    "database": "default",
                    "schema": "public",
                    "columns": columns,
                    "row_count": random.randint(1000, 100000)
                }
            )
            self._assets[table_guid] = table_asset
            
            # Create column assets
            for col_name in columns:
                col_guid = f"column_{table_name}_{col_name}_{random.randint(1000, 9999)}"
                col_asset = AtlanAsset(
                    guid=col_guid,
                    qualified_name=f"{qualified_name}.{col_name}",
                    name=col_name,
                    type_name="Column",
                    attributes={
                        "table": table_name,
                        "data_type": self._infer_data_type(col_name),
                        "parent_guid": table_guid
                    },
                    classifications=self._infer_classifications(col_name)
                )
                self._assets[col_guid] = col_asset
        
        # Create some mock policies
        self._create_mock_policies()
    
    def _infer_data_type(self, column_name: str) -> str:
        """Infer data type from column name"""
        if 'id' in column_name.lower():
            return 'INTEGER'
        elif 'email' in column_name.lower():
            return 'VARCHAR'
        elif 'date' in column_name.lower() or 'time' in column_name.lower():
            return 'TIMESTAMP'
        elif 'amount' in column_name.lower() or 'salary' in column_name.lower():
            return 'DECIMAL'
        else:
            return 'VARCHAR'
    
    def _infer_classifications(self, column_name: str) -> List[str]:
        """Infer PII classifications from column name"""
        classifications = []
        column_lower = column_name.lower()
        
        if 'email' in column_lower:
            classifications.append('PII_EMAIL')
        if 'phone' in column_lower:
            classifications.append('PII_PHONE')
        if 'ssn' in column_lower:
            classifications.append('PII_SSN')
        if 'account' in column_lower:
            classifications.append('PII_FINANCIAL')
        if 'name' in column_lower and column_lower != 'table_name':
            classifications.append('PII_NAME')
        
        return classifications
    
    def _create_mock_policies(self):
        """Create mock governance policies"""
        policies = [
            ("PII_MASKING_POLICY", "Mask all PII data", "MASKING", ["PII_EMAIL", "PII_PHONE", "PII_SSN"]),
            ("FINANCIAL_DATA_POLICY", "Protect financial data", "ACCESS_CONTROL", ["PII_FINANCIAL"]),
            ("AUDIT_LOG_POLICY", "Log all access to sensitive data", "AUDIT", ["PII_*"])
        ]
        
        for policy_name, description, policy_type, resources in policies:
            policy_guid = f"policy_{policy_type}_{random.randint(1000, 9999)}"
            policy = AtlanPolicy(
                guid=policy_guid,
                name=policy_name,
                description=description,
                policy_type=policy_type,
                resources=resources,
                actions=["READ", "WRITE"] if policy_type != "AUDIT" else ["*"]
            )
            self._policies[policy_guid] = policy
    
    def _simulate_api_delay(self):
        """Simulate realistic API response delay"""
        time.sleep(random.uniform(0.1, 0.3))
    
    def _log_audit(self, action: str, resource: str, user: str = "system", details: Dict = None):
        """Log audit entry"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "resource": resource,
            "user": user,
            "status": "SUCCESS",
            "details": details or {}
        }
        self._audit_logs.append(audit_entry)
    
    # ============================================
    # Asset Management APIs
    # ============================================
    
    def search_assets(self, query: str = "*", asset_type: str = None, 
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for assets in Atlan.
        
        Args:
            query: Search query string
            asset_type: Filter by asset type (Table, Column, etc.)
            limit: Maximum number of results
            
        Returns:
            List of matching assets
        """
        self._simulate_api_delay()
        
        results = []
        for asset in self._assets.values():
            # Apply type filter
            if asset_type and asset.type_name != asset_type:
                continue
            
            # Apply search query
            if query != "*":
                if query.lower() not in asset.name.lower() and \
                   query.lower() not in asset.qualified_name.lower():
                    continue
            
            results.append(asdict(asset))
            
            if len(results) >= limit:
                break
        
        self._log_audit("SEARCH_ASSETS", f"query={query}, type={asset_type}", 
                       details={"results_count": len(results)})
        
        print(f"🔍 Mock API: Found {len(results)} assets matching '{query}'")
        return results
    
    def get_asset(self, guid: str) -> Optional[Dict[str, Any]]:
        """
        Get asset by GUID.
        
        Args:
            guid: Asset GUID
            
        Returns:
            Asset details or None if not found
        """
        self._simulate_api_delay()
        
        asset = self._assets.get(guid)
        if asset:
            self._log_audit("GET_ASSET", guid)
            return asdict(asset)
        
        return None
    
    def create_asset(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new asset in Atlan.
        
        Args:
            asset_data: Asset data
            
        Returns:
            Created asset with GUID
        """
        self._simulate_api_delay()
        
        # Generate GUID
        guid = f"asset_{asset_data.get('type_name', 'unknown')}_{random.randint(1000, 9999)}"
        
        # Create asset
        asset = AtlanAsset(
            guid=guid,
            qualified_name=asset_data.get('qualified_name', f"default.{guid}"),
            name=asset_data.get('name', guid),
            type_name=asset_data.get('type_name', 'Asset'),
            status=asset_data.get('status', 'ACTIVE'),
            attributes=asset_data.get('attributes', {}),
            classifications=asset_data.get('classifications', [])
        )
        
        self._assets[guid] = asset
        self._log_audit("CREATE_ASSET", guid, details=asset_data)
        
        print(f"✅ Mock API: Created asset {guid} ({asset.name})")
        return asdict(asset)
    
    def update_asset(self, guid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing asset.
        
        Args:
            guid: Asset GUID
            updates: Fields to update
            
        Returns:
            Updated asset
        """
        self._simulate_api_delay()
        
        asset = self._assets.get(guid)
        if not asset:
            raise ValueError(f"Asset {guid} not found")
        
        # Apply updates
        if 'name' in updates:
            asset.name = updates['name']
        if 'status' in updates:
            asset.status = updates['status']
        if 'attributes' in updates:
            asset.attributes.update(updates['attributes'])
        if 'classifications' in updates:
            asset.classifications = updates['classifications']
        
        self._log_audit("UPDATE_ASSET", guid, details=updates)
        
        print(f"✅ Mock API: Updated asset {guid}")
        return asdict(asset)
    
    def add_classification(self, guid: str, classification: str) -> bool:
        """
        Add a classification to an asset.
        
        Args:
            guid: Asset GUID
            classification: Classification name
            
        Returns:
            Success status
        """
        self._simulate_api_delay()
        
        asset = self._assets.get(guid)
        if not asset:
            return False
        
        if classification not in asset.classifications:
            asset.classifications.append(classification)
        
        self._log_audit("ADD_CLASSIFICATION", guid, 
                       details={"classification": classification})
        
        print(f"✅ Mock API: Added classification '{classification}' to {guid}")
        return True
    
    def remove_classification(self, guid: str, classification: str) -> bool:
        """
        Remove a classification from an asset.
        
        Args:
            guid: Asset GUID
            classification: Classification name
            
        Returns:
            Success status
        """
        self._simulate_api_delay()
        
        asset = self._assets.get(guid)
        if not asset:
            return False
        
        if classification in asset.classifications:
            asset.classifications.remove(classification)
        
        self._log_audit("REMOVE_CLASSIFICATION", guid,
                       details={"classification": classification})
        
        print(f"✅ Mock API: Removed classification '{classification}' from {guid}")
        return True
    
    # ============================================
    # Policy Management APIs
    # ============================================
    
    def get_policies(self, policy_type: str = None) -> List[Dict[str, Any]]:
        """
        Get governance policies.
        
        Args:
            policy_type: Filter by policy type
            
        Returns:
            List of policies
        """
        self._simulate_api_delay()
        
        policies = []
        for policy in self._policies.values():
            if policy_type and policy.policy_type != policy_type:
                continue
            policies.append(asdict(policy))
        
        self._log_audit("GET_POLICIES", f"type={policy_type}",
                       details={"count": len(policies)})
        
        print(f"📋 Mock API: Retrieved {len(policies)} policies")
        return policies
    
    def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new governance policy.
        
        Args:
            policy_data: Policy configuration
            
        Returns:
            Created policy with GUID
        """
        self._simulate_api_delay()
        
        # Generate GUID
        guid = f"policy_{policy_data.get('policy_type', 'custom')}_{random.randint(1000, 9999)}"
        
        # Create policy
        policy = AtlanPolicy(
            guid=guid,
            name=policy_data.get('name', f"Policy_{guid}"),
            description=policy_data.get('description', ''),
            policy_type=policy_data.get('policy_type', 'CUSTOM'),
            status=policy_data.get('status', 'ACTIVE'),
            resources=policy_data.get('resources', []),
            actions=policy_data.get('actions', [])
        )
        
        self._policies[guid] = policy
        self._log_audit("CREATE_POLICY", guid, details=policy_data)
        
        print(f"✅ Mock API: Created policy {guid} ({policy.name})")
        return asdict(policy)
    
    def update_policy(self, guid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing policy.
        
        Args:
            guid: Policy GUID
            updates: Fields to update
            
        Returns:
            Updated policy
        """
        self._simulate_api_delay()
        
        policy = self._policies.get(guid)
        if not policy:
            raise ValueError(f"Policy {guid} not found")
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        policy.updated_at = datetime.now().isoformat()
        
        self._log_audit("UPDATE_POLICY", guid, details=updates)
        
        print(f"✅ Mock API: Updated policy {guid}")
        return asdict(policy)
    
    def delete_policy(self, guid: str) -> bool:
        """
        Delete a policy.
        
        Args:
            guid: Policy GUID
            
        Returns:
            Success status
        """
        self._simulate_api_delay()
        
        if guid in self._policies:
            del self._policies[guid]
            self._log_audit("DELETE_POLICY", guid)
            print(f"✅ Mock API: Deleted policy {guid}")
            return True
        
        return False
    
    # ============================================
    # Lineage APIs
    # ============================================
    
    def get_lineage(self, guid: str, direction: str = "BOTH", 
                   depth: int = 3) -> Dict[str, Any]:
        """
        Get lineage information for an asset.
        
        Args:
            guid: Asset GUID
            direction: UPSTREAM, DOWNSTREAM, or BOTH
            depth: Maximum depth to traverse
            
        Returns:
            Lineage graph
        """
        self._simulate_api_delay()
        
        # Generate mock lineage
        lineage = {
            "base_entity_guid": guid,
            "lineage_direction": direction,
            "lineage_depth": depth,
            "relations": []
        }
        
        # Add some mock upstream/downstream relations
        if direction in ["UPSTREAM", "BOTH"]:
            for i in range(random.randint(1, 3)):
                lineage["relations"].append({
                    "from_guid": f"upstream_{i}",
                    "to_guid": guid,
                    "process_guid": f"process_{i}",
                    "relationship_type": "CONSUMES"
                })
        
        if direction in ["DOWNSTREAM", "BOTH"]:
            for i in range(random.randint(1, 3)):
                lineage["relations"].append({
                    "from_guid": guid,
                    "to_guid": f"downstream_{i}",
                    "process_guid": f"process_{i}",
                    "relationship_type": "PRODUCES"
                })
        
        self._log_audit("GET_LINEAGE", guid, 
                       details={"direction": direction, "depth": depth})
        
        print(f"🔗 Mock API: Retrieved lineage for {guid}")
        return lineage
    
    # ============================================
    # Audit & Monitoring APIs
    # ============================================
    
    def get_audit_logs(self, start_time: str = None, end_time: str = None,
                      action: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get audit logs.
        
        Args:
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            action: Filter by action type
            limit: Maximum number of logs
            
        Returns:
            List of audit log entries
        """
        self._simulate_api_delay()
        
        logs = self._audit_logs.copy()
        
        # Apply filters
        if action:
            logs = [log for log in logs if log['action'] == action]
        
        # Sort by timestamp (most recent first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply limit
        logs = logs[:limit]
        
        print(f"📊 Mock API: Retrieved {len(logs)} audit log entries")
        return logs
    
    def get_usage_metrics(self, resource_guid: str = None) -> Dict[str, Any]:
        """
        Get usage metrics for assets.
        
        Args:
            resource_guid: Specific resource GUID (optional)
            
        Returns:
            Usage metrics
        """
        self._simulate_api_delay()
        
        metrics = {
            "total_queries": random.randint(100, 10000),
            "unique_users": random.randint(10, 100),
            "avg_response_time_ms": random.uniform(50, 500),
            "last_accessed": datetime.now().isoformat(),
            "popular_queries": [
                {"query": "SELECT * FROM customers", "count": random.randint(10, 100)},
                {"query": "SELECT email FROM customers", "count": random.randint(5, 50)}
            ]
        }
        
        if resource_guid:
            metrics["resource_guid"] = resource_guid
        
        print(f"📈 Mock API: Retrieved usage metrics")
        return metrics
    
    # ============================================
    # Utility Methods
    # ============================================
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get connection status and health information.
        
        Returns:
            Connection status details
        """
        return {
            "connected": True,
            "mode": "MOCK",
            "base_url": self.base_url,
            "timestamp": datetime.now().isoformat(),
            "assets_count": len(self._assets),
            "policies_count": len(self._policies),
            "audit_logs_count": len(self._audit_logs),
            "health": "HEALTHY"
        }
    
    def reset_mock_data(self):
        """Reset all mock data to initial state"""
        self._assets.clear()
        self._policies.clear()
        self._lineage.clear()
        self._audit_logs.clear()
        self._initialize_mock_data()
        print("🔄 Mock API: Data reset to initial state")
    
    def export_mock_data(self, filepath: str):
        """
        Export mock data to a JSON file.
        
        Args:
            filepath: Output file path
        """
        data = {
            "assets": [asdict(asset) for asset in self._assets.values()],
            "policies": [asdict(policy) for policy in self._policies.values()],
            "audit_logs": self._audit_logs,
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Mock API: Data exported to {filepath}")
    
    def import_mock_data(self, filepath: str):
        """
        Import mock data from a JSON file.
        
        Args:
            filepath: Input file path
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Import assets
        self._assets.clear()
        for asset_data in data.get('assets', []):
            asset = AtlanAsset(**asset_data)
            self._assets[asset.guid] = asset
        
        # Import policies
        self._policies.clear()
        for policy_data in data.get('policies', []):
            policy = AtlanPolicy(**policy_data)
            self._policies[policy.guid] = policy
        
        # Import audit logs
        self._audit_logs = data.get('audit_logs', [])
        
        print(f"📥 Mock API: Data imported from {filepath}")
        print(f"   Assets: {len(self._assets)}, Policies: {len(self._policies)}, Logs: {len(self._audit_logs)}")


# ============================================
# Convenience Functions
# ============================================

def create_mock_client(base_url: str = None, api_token: str = None) -> MockAtlanAPI:
    """
    Create a mock Atlan API client.
    
    Args:
        base_url: Atlan instance base URL (ignored in mock mode)
        api_token: API token (ignored in mock mode)
        
    Returns:
        MockAtlanAPI instance
    """
    return MockAtlanAPI(base_url=base_url, api_token=api_token)


def get_atlan_client(mode: str = "mock", **kwargs) -> MockAtlanAPI:
    """
    Get an Atlan API client (mock or real).
    
    Args:
        mode: "mock" for mock client, "real" for actual Atlan client
        **kwargs: Additional arguments for client initialization
        
    Returns:
        Atlan API client instance
    """
    if mode == "mock":
        return create_mock_client(**kwargs)
    else:
        # In production, this would return the real Atlan client
        # For now, we only support mock mode
        print("⚠️  Real Atlan client not implemented, falling back to mock mode")
        return create_mock_client(**kwargs)


# ============================================
# Demo / Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Atlan Mock API - Demo")
    print("=" * 60)
    
    # Create mock client
    client = create_mock_client()
    
    # Test connection
    print("\n1. Testing Connection Status:")
    status = client.get_connection_status()
    print(f"   Status: {json.dumps(status, indent=2)}")
    
    # Search assets
    print("\n2. Searching for Assets:")
    assets = client.search_assets(query="customers", asset_type="Table")
    print(f"   Found {len(assets)} assets")
    for asset in assets[:2]:
        print(f"   - {asset['name']} ({asset['type_name']})")
    
    # Get policies
    print("\n3. Getting Policies:")
    policies = client.get_policies()
    print(f"   Found {len(policies)} policies")
    for policy in policies:
        print(f"   - {policy['name']} ({policy['policy_type']})")
    
    # Add classification
    print("\n4. Adding Classification:")
    if assets:
        asset_guid = assets[0]['guid']
        success = client.add_classification(asset_guid, "SENSITIVE_DATA")
        print(f"   Classification added: {success}")
    
    # Get audit logs
    print("\n5. Getting Audit Logs:")
    logs = client.get_audit_logs(limit=5)
    print(f"   Found {len(logs)} audit log entries")
    for log in logs[:3]:
        print(f"   - {log['action']} on {log['resource']} at {log['timestamp']}")
    
    # Export mock data
    print("\n6. Exporting Mock Data:")
    export_path = "atlan_mock_data_export.json"
    client.export_mock_data(export_path)
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
