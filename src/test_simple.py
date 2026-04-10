#!/usr/bin/env python3
"""
Simple Health Check Test
"""
import requests
import time

def test_health():
    print("🏥 Testing server health...")
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_simple_query():
    print("\n🔍 Testing simple query...")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/process", 
            json={"query": "test"}, 
            timeout=30
        )
        print(f"✅ Query test: {response.status_code}")
        result = response.json()
        print(f"Status: {result.get('status')}")
        print(f"Execution time: {result.get('execution_time', 0):.2f}s")
        return True
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Atlan Actions System Test")
    print("=" * 30)
    
    if test_health():
        test_simple_query()
    else:
        print("Server not responding, check if it's running.")