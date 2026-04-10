#!/usr/bin/env python3
"""
Check the actual response structure
"""
import subprocess
import json
import time

BASE_URL = "http://localhost:5000"

def test_workflow():
    print("\n[Submitting command...]")
    cmd = f'curl -X POST "{BASE_URL}/api/process" -H "Content-Type: application/json" -d "{{\\"command\\": \\"mask salary in HEALTH_RECORDS for analyst role\\"}}"'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}")
        return
    
    response = json.loads(result.stdout)
    
    print("\n[FULL RESPONSE]:")
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    test_workflow()
