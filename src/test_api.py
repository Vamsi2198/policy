#!/usr/bin/env python3
"""
Simple API test for Atlan Actions Engine
"""

import requests
import json
import time

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health')
        print(f"Health check - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_process():
    """Test the process endpoint"""
    try:
        test_command = "mask the PII data in users table"
        print(f"\nTesting command: '{test_command}'")
        
        response = requests.post(
            'http://localhost:5000/api/process',
            json={'command': test_command},
            timeout=30
        )
        
        print(f"Process test - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Engine processed the command.")
            print(f"Phases completed: {len(result.get('phases', []))}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Process test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Atlan Actions API...")
    
    # Test health first
    if not test_health():
        print("❌ Server is not responding")
        exit(1)
    
    print("✅ Server is healthy")
    
    # Test process endpoint
    if test_process():
        print("✅ Process endpoint working correctly")
    else:
        print("❌ Process endpoint has issues")
    
    print("\n🎯 Testing complete!")