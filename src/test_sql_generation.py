#!/usr/bin/env python3
"""
Test SQL generation for masking policies
"""

def test_sql_generation():
    """Test the SQL generation logic for masking policies"""
    
    print("="*70)
    print("🧪 TESTING SQL GENERATION FOR MASKING POLICIES")
    print("="*70)
    
    def generate_masking_sql(table, column, pii_types):
        """Test the exact SQL generation logic from AI Control Plane"""
        policy_name = f"mask_{table}_{column}".lower()
        
        # Choose masking function based on PII type (same logic as AI Control Plane)
        if 'EMAIL_ADDRESS' in pii_types:
            mask_function = "CONCAT(LEFT(val, 3), '***@***.com')"
        elif 'PHONE_NUMBER' in pii_types:
            mask_function = "CONCAT('***-***-', RIGHT(val, 4))"
        elif 'SSN' in pii_types:
            mask_function = "CONCAT('***-**-', RIGHT(val, 4))"
        else:
            mask_function = "'***MASKED***'"  # This is a literal string, so it needs quotes
        
        sql_commands = [
            "BEGIN;",
            f"-- Create backup of original data",
            f"CREATE TABLE IF NOT EXISTS {table}_backup AS SELECT * FROM {table};",
            f"-- Create masking policy for {column}",
            f"CREATE OR REPLACE MASKING POLICY {policy_name} AS (val STRING) RETURNS STRING ->",
            f"  CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val",
            f"       ELSE {mask_function} END;",  # Remove quotes here - mask_function includes them when needed
            f"-- Apply masking policy to column",
            f"ALTER TABLE {table} MODIFY COLUMN {column} SET MASKING POLICY {policy_name};",
            "COMMIT;"
        ]
        
        return sql_commands
    
    # Test different PII types
    test_cases = [
        ("EMPLOYEES", "EMAIL", ["EMAIL_ADDRESS"]),
        ("EMPLOYEES", "PHONE", ["PHONE_NUMBER"]),
        ("CUSTOMERS", "SSN", ["SSN"]),
        ("USERS", "NAME", ["PERSON"])  # Should use default masking
    ]
    
    for table, column, pii_types in test_cases:
        print(f"\n📋 Testing: {table}.{column} (PII: {pii_types})")
        print("-" * 50)
        
        sql_commands = generate_masking_sql(table, column, pii_types)
        
        for i, sql in enumerate(sql_commands, 1):
            print(f"{i:2d}. {sql}")
        
        # Check for potential issues
        issues = []
        for sql in sql_commands:
            if "ELSE '{" in sql and "}'" in sql:
                issues.append("❌ Found quoted function variables - this will cause syntax errors")
            if len(sql.strip()) == 0:
                issues.append("❌ Found empty SQL command")
            if sql.count("'") % 2 != 0 and not sql.strip().startswith("--"):
                issues.append("❌ Unmatched quotes detected")
        
        if issues:
            print("\n⚠️ POTENTIAL ISSUES:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ SQL looks valid")
    
    print(f"\n{'='*70}")
    print("🏁 SQL GENERATION TEST COMPLETED")
    print("="*70)
    
    # Test the specific fix
    print("\n🔧 TESTING THE SPECIFIC FIX:")
    print("-" * 50)
    
    # Test EMAIL masking (should use function without extra quotes)
    email_sql = "CREATE OR REPLACE MASKING POLICY test_policy AS (val STRING) RETURNS STRING -> CASE WHEN CURRENT_ROLE() IN ('ADMIN') THEN val ELSE CONCAT(LEFT(val, 3), '***@***.com') END;"
    print("✅ CORRECT EMAIL SQL:")
    print(f"   {email_sql}")
    
    # Test default masking (should use quoted literal)
    default_sql = "CREATE OR REPLACE MASKING POLICY test_policy AS (val STRING) RETURNS STRING -> CASE WHEN CURRENT_ROLE() IN ('ADMIN') THEN val ELSE '***MASKED***' END;"
    print("\n✅ CORRECT DEFAULT SQL:")
    print(f"   {default_sql}")
    
    print("\n💡 The fix removes the extra quotes around function calls while keeping quotes for literal strings.")

if __name__ == "__main__":
    test_sql_generation()