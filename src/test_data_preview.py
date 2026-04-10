"""
Test data preview endpoint with role-based views
"""
import requests
import json

API_URL = "http://localhost:5000"

def test_data_preview():
    """Test the data preview endpoint"""
    
    # First, let's check if we have any active sessions
    print("=" * 60)
    print("Testing Data Preview with Role-Based Views")
    print("=" * 60)
    
    # Test with a sample session_id
    # In a real scenario, you would get this from the /api/process endpoint
    session_id = "test_session_123"
    
    # Test the data preview endpoint
    print(f"\n📡 Testing /api/data-preview/{session_id}")
    
    try:
        response = requests.get(f"{API_URL}/api/data-preview/{session_id}")
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"\n✅ Success! Data Preview:")
            print(json.dumps(data, indent=2))
            
            # Show the data comparison
            if 'table' in data:
                print(f"\n📊 Table: {data['table']}")
                print(f"📋 Columns: {', '.join(data.get('columns', []))}")
                
                print("\n🔓 BEFORE (Unmasked - ACCOUNTADMIN):")
                for idx, row in enumerate(data.get('before', [])):
                    print(f"  Row {idx + 1}: {row}")
                
                print("\n🔒 AFTER (HR_ROLE View):")
                for idx, row in enumerate(data.get('after_hr', [])):
                    print(f"  Row {idx + 1}: {row}")
                
                print("\n🔒 AFTER (ANALYST_ROLE View):")
                for idx, row in enumerate(data.get('after_analyst', [])):
                    print(f"  Row {idx + 1}: {row}")
        else:
            print(f"\n❌ Error: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 60)

def test_continue_with_preview():
    """Test continue execution with data preview"""
    
    print("\n" + "=" * 60)
    print("Testing Continue Execution with Data Preview")
    print("=" * 60)
    
    session_id = "test_session_123"
    
    print(f"\n📡 Testing /api/continue-execution/{session_id}")
    
    try:
        response = requests.post(f"{API_URL}/api/continue-execution/{session_id}")
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"\n✅ Success! Execution result with data preview:")
            
            # Show data preview if available
            if 'data_preview' in data:
                preview = data['data_preview']
                print(f"\n📊 Table: {preview.get('table', 'N/A')}")
                print(f"📋 Columns: {', '.join(preview.get('columns', []))}")
                
                print("\n🔓 BEFORE (Unmasked):")
                for idx, row in enumerate(preview.get('before', [])):
                    print(f"  Row {idx + 1}: {row}")
                
                print("\n🔒 AFTER (HR_ROLE):")
                for idx, row in enumerate(preview.get('after_hr', [])):
                    print(f"  Row {idx + 1}: {row}")
                
                print("\n🔒 AFTER (ANALYST_ROLE):")
                for idx, row in enumerate(preview.get('after_analyst', [])):
                    print(f"  Row {idx + 1}: {row}")
            else:
                print("\n⚠️ No data preview in response")
                print(json.dumps(data, indent=2))
        else:
            print(f"\n❌ Error: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Test both endpoints
    test_data_preview()
    test_continue_with_preview()
    
    print("\n💡 Tips:")
    print("1. Make sure API server is running on localhost:5000")
    print("2. Execute a governance command first to create a session")
    print("3. Approve the action to enable continue-execution")
    print("4. Then test the data preview endpoints")
