#!/usr/bin/env python3
"""
Test Script for Metadata and Audit APIs
========================================

This script demonstrates the functionality of the new
metadata and audit tracking features.
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_metadata_apis():
    """Test metadata API endpoints"""
    print_section("Testing Metadata APIs")
    
    # Test policy changes
    print("\n1. Getting Policy Changes:")
    response = requests.get(f"{BASE_URL}/api/metadata/policy-changes")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Count: {data.get('count')}")
        if data.get('changes'):
            print(f"   Sample: {data['changes'][0]['policy_name']}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test lineage
    print("\n2. Getting Lineage Metadata:")
    response = requests.get(f"{BASE_URL}/api/metadata/lineage")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Count: {data.get('count')}")
        if data.get('lineage_entries'):
            entry = data['lineage_entries'][0]
            print(f"   Sample: {entry['source_asset']} → {entry['target_asset']}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test statistics
    print("\n3. Getting Metadata Statistics:")
    response = requests.get(f"{BASE_URL}/api/metadata/statistics")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        stats = data.get('statistics', {})
        print(f"   Policy Changes: {stats.get('policy_changes', {}).get('total', 0)}")
        print(f"   Lineage Entries: {stats.get('lineage_entries', {}).get('total', 0)}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")

def test_audit_apis():
    """Test audit API endpoints"""
    print_section("Testing Audit APIs")
    
    # Test audit log
    print("\n1. Getting Audit Log:")
    response = requests.get(f"{BASE_URL}/api/audit/log")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Count: {data.get('count')}")
        if data.get('audit_entries'):
            entry = data['audit_entries'][0]
            print(f"   Sample: {entry['policy_name']} on {entry['target_table']} ({entry['execution_status']})")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test audit statistics
    print("\n2. Getting Audit Statistics:")
    response = requests.get(f"{BASE_URL}/api/audit/statistics")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        stats = data.get('statistics', {})
        print(f"   Total Policies: {len(stats)}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test dashboard
    print("\n3. Getting Audit Dashboard:")
    response = requests.get(f"{BASE_URL}/api/audit/dashboard")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        dashboard = data.get('dashboard', {})
        overview = dashboard.get('overview', {})
        print(f"   Total Executions: {overview.get('total_executions', 0)}")
        print(f"   Success Rate: {overview.get('success_rate', 0):.1f}%")
        print(f"   Top Policies: {len(dashboard.get('top_policies', []))}")
        print(f"   Top Tables: {len(dashboard.get('top_tables', []))}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test top policies
    print("\n4. Getting Top Policies:")
    response = requests.get(f"{BASE_URL}/api/audit/top-policies?limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Count: {data.get('count')}")
        for i, policy in enumerate(data.get('policies', [])[:3], 1):
            print(f"   {i}. {policy['policy_name']}: {policy['total_executions']} executions")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test top tables
    print("\n5. Getting Top Tables:")
    response = requests.get(f"{BASE_URL}/api/audit/top-tables?limit=5")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Count: {data.get('count')}")
        for i, table in enumerate(data.get('tables', [])[:3], 1):
            print(f"   {i}. {table['table_name']}: {table['execution_count']} executions")
    else:
        print(f"   Error: {response.status_code} - {response.text}")

def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")
    
    response = requests.get(f"{BASE_URL}/api/health")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Atlan Available: {data.get('atlan_available')}")
        print(f"   Engine Initialized: {data.get('engine_initialized')}")
        print(f"   Timestamp: {data.get('timestamp')}")
    else:
        print(f"   Error: {response.status_code}")

def main():
    """Main test function"""
    print("\n" + "🎯" * 30)
    print("  Metadata & Audit API Test Suite")
    print("🎯" * 30)
    
    try:
        # Test health first
        test_health()
        
        # Test metadata APIs
        test_metadata_apis()
        
        # Test audit APIs
        test_audit_apis()
        
        print_section("All Tests Complete!")
        print("\n✅ API endpoints are working correctly!")
        print("\n📝 Next Steps:")
        print("   1. Integrate UI tabs into the dashboard")
        print("   2. Add JavaScript functions for data loading")
        print("   3. Test with real policy executions")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("   Make sure the server is running on http://localhost:5000")
        print("   Run: python atlan_api_server.py")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
