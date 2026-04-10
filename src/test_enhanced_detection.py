#!/usr/bin/env python3
"""Test enhanced keyword detection with typos and context"""

def test_enhanced_detection():
    """Test enhanced masking detection including typos"""
    
    print('🧪 TESTING ENHANCED MASKING DETECTION')
    print('='*60)
    
    test_queries = [
        ("mast the total_amount in ORDERS table", "MASKING"),  # Typo + context
        ("mask phone numbers", "MASKING"),
        ("unmask phone numbers", "UNMASKING"),
        ("hide salary information", "MASKING"),
        ("show total amounts", "REGULAR QUERY"),  # No masking keywords
        ("mast all sensitive data", "MASKING"),  # Typo + context
        ("total amount summary", "REGULAR QUERY"),  # Context but no masking keyword
        ("encrypt credit card data", "MASKING")
    ]
    
    for query, expected_type in test_queries:
        print(f'\n📝 Query: "{query}"')
        
        # Enhanced detection logic
        query_lower = query.lower()
        
        # Check for UNMASK operations first
        unmask_keywords = ['unmask', 'restore', 'unscramble', 'decrypt', 'reveal', 'show original', 'undo mask']
        is_unmask_request = any(keyword in query_lower for keyword in unmask_keywords)
        
        # Check for MASK operations - includes common typos
        masking_keywords = ['mask', 'mast', 'hide', 'anonymize', 'encrypt', 'obfuscate', 'redact', 'scramble', 'replace with']
        is_masking_request = any(keyword in query_lower for keyword in masking_keywords) and not is_unmask_request
        
        # Additional fuzzy matching for masking operations
        masking_context_words = ['total_amount', 'salary', 'phone', 'ssn', 'email', 'credit', 'card', 'sensitive']
        has_masking_context = any(word in query_lower for word in masking_context_words)
        
        # If we have masking keywords or context with sensitive data, treat as masking
        if not is_unmask_request and (is_masking_request or (has_masking_context and ('mast' in query_lower or 'mask' in query_lower))):
            is_masking_request = True
        
        # Determine final type
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
    
    print(f'\n🎉 Enhanced detection test completed!')

if __name__ == "__main__":
    test_enhanced_detection()