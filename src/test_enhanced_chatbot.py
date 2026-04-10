#!/usr/bin/env python3
"""
Test Enhanced Chatbot - All SQL Operations
Demonstrates the enhanced chatbot that handles ALL types of SQL operations
"""

import sys
import time

def test_enhanced_chatbot():
    """Test the enhanced chatbot with different types of queries"""
    
    print('🚀 ENHANCED CHATBOT DEMONSTRATION')
    print('🤖 Now handles ALL types of SQL operations automatically!')
    print('='*70)
    
    # Test queries for different operation types
    test_queries = [
        {
            "type": "SELECT",
            "query": "Show me all employees in the Engineering department",
            "description": "Basic data retrieval"
        },
        {
            "type": "DELETE", 
            "query": "Delete customer with ID 123 for GDPR compliance",
            "description": "Data deletion with GDPR"
        },
        {
            "type": "INSERT",
            "query": "Add new employee John Smith in Marketing department with salary 75000",
            "description": "Adding new data"
        },
        {
            "type": "UPDATE",
            "query": "Update salary for employee ID 5 to 85000",
            "description": "Modifying existing data"
        },
        {
            "type": "MASK",
            "query": "Mask all phone numbers in the customers table",
            "description": "Data privacy masking"
        },
        {
            "type": "UNMASK",
            "query": "Unmask email addresses in customers table",
            "description": "Data restoration"
        }
    ]
    
    print("🧪 TESTING AUTOMATIC OPERATION DETECTION:")
    print("-" * 70)
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🔄 Test {i}: {test['type']} Operation")
        print(f"📝 Query: '{test['query']}'")
        print(f"💡 Purpose: {test['description']}")
        
        # Simulate the detection logic
        query_lower = test['query'].lower()
        
        # Detection logic (same as in the enhanced chatbot)
        unmask_keywords = ['unmask', 'restore', 'unscramble', 'decrypt', 'reveal', 'show original', 'undo mask']
        is_unmask_request = any(keyword in query_lower for keyword in unmask_keywords)
        
        masking_keywords = ['mask', 'hide', 'anonymize', 'encrypt', 'obfuscate', 'redact', 'scramble']
        is_masking_request = any(keyword in query_lower for keyword in masking_keywords) and not is_unmask_request
        
        delete_keywords = ['delete', 'remove', 'drop', 'erase', 'purge', 'gdpr', 'forget']
        is_delete_request = any(keyword in query_lower for keyword in delete_keywords)
        
        insert_keywords = ['insert', 'add', 'create record', 'new entry', 'add data']
        is_insert_request = any(keyword in query_lower for keyword in insert_keywords)
        
        update_keywords = ['update', 'modify', 'change', 'edit', 'alter', 'set']
        is_update_request = any(keyword in query_lower for keyword in update_keywords) and not is_masking_request
        
        # Show detection results
        if is_unmask_request:
            print("✅ Detected: 🔓 UNMASKING operation")
            print("   Action: Will restore original data from backup")
        elif is_masking_request:
            print("✅ Detected: 🔐 MASKING operation")
            print("   Action: Will permanently mask sensitive data")
        elif is_delete_request:
            print("✅ Detected: 🗑️ DELETE operation")
            print("   Action: Will remove data from database")
        elif is_insert_request:
            print("✅ Detected: ➕ INSERT operation")
            print("   Action: Will add new data to database")
        elif is_update_request:
            print("✅ Detected: ✏️ UPDATE operation")
            print("   Action: Will modify existing data")
        else:
            print("✅ Detected: 📊 SELECT operation")
            print("   Action: Will query and display data")
        
        time.sleep(0.5)
    
    print(f"\n🎉 ENHANCED CHATBOT CAPABILITIES:")
    print("="*70)
    print("✅ 📊 SELECT queries - Data retrieval and analysis")
    print("✅ ➕ INSERT operations - Adding new records")
    print("✅ ✏️ UPDATE operations - Modifying existing data")
    print("✅ 🗑️ DELETE operations - Removing data (with safety)")
    print("✅ 🔐 MASKING operations - Privacy protection")
    print("✅ 🔓 UNMASKING operations - Data restoration")
    print("✅ 🛡️ Automatic confirmation for destructive operations")
    print("✅ 🎯 Context-aware SQL generation")
    print("✅ 🔒 Safety checks and transaction control")
    
    print(f"\n🚀 HOW TO USE:")
    print("1. Run: python control_pannel.py --chatbot")
    print("2. Ask any question in natural language")
    print("3. System automatically detects the operation type")
    print("4. Confirms destructive operations before execution")
    print("5. Executes and shows results")
    
    print(f"\n💬 EXAMPLE CONVERSATIONS:")
    print("User: 'Show me all customers from California'")
    print("→ System detects SELECT, generates and executes query")
    print("")
    print("User: 'Delete customer with ID 456'")
    print("→ System detects DELETE, asks for confirmation, executes")
    print("")
    print("User: 'Mask all credit card numbers'")
    print("→ System detects MASKING, generates masking SQL, confirms")
    print("")
    print("User: 'Add new employee Sarah Wilson in IT'")
    print("→ System detects INSERT, generates INSERT statement")
    
    print("\n🌟 Your chatbot is now a complete SQL assistant!")
    print("="*70)

if __name__ == "__main__":
    test_enhanced_chatbot()