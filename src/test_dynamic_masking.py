#!/usr/bin/env python3
"""
Quick test to verify dynamic masking based on user query
"""

from s3_data_handler import S3DataHandler
import json

def test_email_only():
    """Test masking only email"""
    print("\n" + "="*60)
    print("TEST 1: Mask only EMAIL")
    print("="*60)
    
    handler = S3DataHandler()
    result = handler.apply_masking_policies("Mask all email", pii_findings=None)
    
    print(f"\n📊 Policies Applied: {len(result.policies_applied)}")
    print(f"📋 Fields Affected: {result.affected_fields}")
    
    print(f"\n🔍 Before:")
    print(json.dumps(result.original_data[0], indent=2))
    
    print(f"\n🔒 After:")
    print(json.dumps(result.masked_data[0], indent=2))
    
    # Verify only email is masked
    assert len(result.affected_fields) == 1, f"Expected 1 field, got {len(result.affected_fields)}"
    assert 'email' in result.affected_fields, "Email should be masked"
    assert result.masked_data[0]['name'] == result.original_data[0]['name'], "Name should NOT be masked"
    assert result.masked_data[0]['ssn'] == result.original_data[0]['ssn'], "SSN should NOT be masked"
    print("\n✅ PASS: Only email masked!")

def test_email_and_ssn():
    """Test masking email and SSN"""
    print("\n" + "="*60)
    print("TEST 2: Mask EMAIL and SSN")
    print("="*60)
    
    handler = S3DataHandler()
    result = handler.apply_masking_policies("Mask all email and SSN", pii_findings=None)
    
    print(f"\n📊 Policies Applied: {len(result.policies_applied)}")
    print(f"📋 Fields Affected: {result.affected_fields}")
    
    print(f"\n🔍 Before:")
    print(json.dumps(result.original_data[0], indent=2))
    
    print(f"\n🔒 After:")
    print(json.dumps(result.masked_data[0], indent=2))
    
    # Verify only email and ssn are masked
    assert len(result.affected_fields) == 2, f"Expected 2 fields, got {len(result.affected_fields)}"
    assert 'email' in result.affected_fields, "Email should be masked"
    assert 'ssn' in result.affected_fields, "SSN should be masked"
    assert result.masked_data[0]['name'] == result.original_data[0]['name'], "Name should NOT be masked"
    assert result.masked_data[0]['address'] == result.original_data[0]['address'], "Address should NOT be masked"
    print("\n✅ PASS: Only email and SSN masked!")

def test_all_pii():
    """Test masking all PII"""
    print("\n" + "="*60)
    print("TEST 3: Mask ALL PII")
    print("="*60)
    
    handler = S3DataHandler()
    result = handler.apply_masking_policies("Mask all PII data", pii_findings=None)
    
    print(f"\n📊 Policies Applied: {len(result.policies_applied)}")
    print(f"📋 Fields Affected: {result.affected_fields}")
    
    print(f"\n🔍 Before:")
    print(json.dumps(result.original_data[0], indent=2))
    
    print(f"\n🔒 After:")
    print(json.dumps(result.masked_data[0], indent=2))
    
    # Verify multiple fields are masked
    assert len(result.affected_fields) >= 3, f"Expected 3+ fields, got {len(result.affected_fields)}"
    print(f"\n✅ PASS: All PII fields masked! ({len(result.affected_fields)} fields)")

def test_no_masking():
    """Test when no masking keywords in query"""
    print("\n" + "="*60)
    print("TEST 4: NO masking (query without PII keywords)")
    print("="*60)
    
    handler = S3DataHandler()
    result = handler.apply_masking_policies("Show me the data", pii_findings=None)
    
    print(f"\n📊 Policies Applied: {len(result.policies_applied)}")
    print(f"📋 Fields Affected: {result.affected_fields}")
    
    # Verify no fields are masked
    assert len(result.affected_fields) == 0, f"Expected 0 fields, got {len(result.affected_fields)}"
    assert result.masked_data[0] == result.original_data[0], "Data should be unchanged"
    print("\n✅ PASS: No masking applied!")

if __name__ == "__main__":
    try:
        test_email_only()
        test_email_and_ssn()
        test_all_pii()
        test_no_masking()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED - Dynamic masking working correctly!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
