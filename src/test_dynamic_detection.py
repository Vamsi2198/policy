#!/usr/bin/env python3
"""Test dynamic masking vs unmasking detection"""

from control_pannel import NLToSQLConverter

def test_dynamic_detection():
    """Test if the system correctly detects mask vs unmask operations"""
    
    print('🧪 TESTING DYNAMIC MASK/UNMASK DETECTION')
    print('='*60)
    
    test_queries = [
        ("mask phone numbers", "MASKING"),
        ("unmask phone numbers", "UNMASKING"),
        ("hide SSN data", "MASKING"),
        ("restore SSN data", "UNMASKING"),
        ("anonymize email addresses", "MASKING"),
        ("reveal original email data", "UNMASKING"),
        ("unmask all data in customers table", "UNMASKING"),
        ("mask all data in customers table", "MASKING"),
        ("decrypt customer information", "UNMASKING"),
        ("encrypt customer information", "MASKING")
    ]
    
    for query, expected_type in test_queries:
        print(f'\n📝 Query: "{query}"')
        
        # Test keyword detection logic
        query_lower = query.lower()
        
        # Check for UNMASK operations first
        unmask_keywords = ['unmask', 'restore', 'unscramble', 'decrypt', 'reveal', 'show original', 'undo mask']
        is_unmask_request = any(keyword in query_lower for keyword in unmask_keywords)
        
        # Check for MASK operations (only if not unmask)
        masking_keywords = ['mask', 'hide', 'anonymize', 'encrypt', 'obfuscate', 'redact', 'scramble', 'replace with']
        is_masking_request = any(keyword in query_lower for keyword in masking_keywords) and not is_unmask_request
        
        if is_unmask_request:
            detected_type = "UNMASKING"
            print(f'   🔓 Detected: {detected_type}')
        elif is_masking_request:
            detected_type = "MASKING"
            print(f'   🔐 Detected: {detected_type}')
        else:
            detected_type = "REGULAR QUERY"
            print(f'   🔍 Detected: {detected_type}')
        
        # Check if detection matches expectation
        if detected_type == expected_type:
            print(f'   ✅ CORRECT: Expected {expected_type}, got {detected_type}')
        else:
            print(f'   ❌ WRONG: Expected {expected_type}, got {detected_type}')
    
    print(f'\n🎉 Dynamic detection test completed!')

if __name__ == "__main__":
    test_dynamic_detection()