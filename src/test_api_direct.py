#!/usr/bin/env python3
"""
Test API Endpoint Directly
"""
import requests
import json

url = "http://localhost:5000/api/process"
data = {"query": "test connection"}

print("🔍 Testing API endpoint...")
print(f"URL: {url}")
print(f"Data: {data}")

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")