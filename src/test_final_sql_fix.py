#!/usr/bin/env python3
"""
Test the final fix for SQL generation - single line masking policy
"""

def test_final_sql_fix():
    """Test the final SQL fix with single-line masking policy statements"""
    
    print("="*80)
    print("🧪 TESTING FINAL SQL FIX - Single Line Masking Policy")
    print("="*80)
    
    def generate_fixed_masking_sql(table, column, pii_types):
        """Test the final fixed SQL generation"""
        policy_name = f"{table}_{column}_mask_policy".replace('.', '_')
        
        # Handle schema-qualified table names properly
        if '.' in table:
            table_parts = table.split('.')
            if len(table_parts) == 2:
                schema, table_name = table_parts
                full_table_name = f'"{schema}"."{table_name}"'
                backup_table_name = f'"{schema}"."{table_name}_backup"'
            else:
                full_table_name = f'"{table}"'
                backup_table_name = f'"{table}_backup"'
        else:
            full_table_name = f'"{table}"'
            backup_table_name = f'"{table}_backup"'
        
        # Choose masking function based on PII type
        if 'EMAIL_ADDRESS' in pii_types:
            mask_function = "CONCAT(LEFT(val, 3), '***@***.com')"
        elif 'PHONE_NUMBER' in pii_types:
            mask_function = "CONCAT('***-***-', RIGHT(val, 4))"
        elif 'SSN' in pii_types:
            mask_function = "CONCAT('***-**-', RIGHT(val, 4))"
        else:
            mask_function = "'***MASKED***'"
        
        # FIXED: Single line masking policy statement
        sql_commands = [
            "BEGIN;",
            f"-- Create backup of original data",
            f"CREATE TABLE IF NOT EXISTS {backup_table_name} AS SELECT * FROM {full_table_name};",
            f"-- Create masking policy for {column}",
            f"CREATE OR REPLACE MASKING POLICY {policy_name} AS (val STRING) RETURNS STRING -> CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val ELSE {mask_function} END;",
            f"-- Apply masking policy to column", 
            f"ALTER TABLE {full_table_name} MODIFY COLUMN \"{column}\" SET MASKING POLICY {policy_name};",
            "COMMIT;"
        ]
        
        return sql_commands
    
    # Test the problematic case from the error log
    test_cases = [
        ("PUBLIC.EMPLOYEES_BACKUP", "NAME", ["PERSON"]),
        ("PUBLIC.EMPLOYEES", "EMAIL", ["EMAIL_ADDRESS"]),
        ("PUBLIC.PRODUCTS", "PHONE", ["PHONE_NUMBER"])
    ]
    
    print("🎯 Testing cases that were failing:")
    
    for table, column, pii_types in test_cases:
        print(f"\n📋 Testing: {table}.{column} (PII: {pii_types})")
        print("-" * 70)
        
        sql_commands = generate_fixed_masking_sql(table, column, pii_types)
        
        for i, sql in enumerate(sql_commands, 1):
            print(f"{i}. {sql}")
            
            # Check for the specific issue
            if "CREATE OR REPLACE MASKING POLICY" in sql and "RETURNS STRING ->" in sql:
                if sql.strip().endswith("->"):
                    print(f"   ❌ INCOMPLETE: This command ends with '->' and is missing the CASE statement")
                elif "CASE WHEN" in sql and "END;" in sql:
                    print(f"   ✅ COMPLETE: This command includes the full CASE statement")
                else:
                    print(f"   ⚠️ UNKNOWN: This command structure is unclear")
    
    print(f"\n{'='*80}")
    print("🔧 KEY FIX APPLIED:")
    print("="*80)
    
    # Show the before/after comparison
    print("\n❌ BEFORE (broken - multiple lines):")
    print('f"CREATE OR REPLACE MASKING POLICY {policy_name} AS (val STRING) RETURNS STRING ->",')
    print('f"  CASE WHEN CURRENT_ROLE() IN (\'ADMIN\', \'DATA_STEWARD\') THEN val",')
    print('f"       ELSE {mask_function} END;",')
    print("   ↳ Problem: Each line executed as separate SQL command")
    
    print("\n✅ AFTER (fixed - single line):")
    print('f"CREATE OR REPLACE MASKING POLICY {policy_name} AS (val STRING) RETURNS STRING -> CASE WHEN CURRENT_ROLE() IN (\'ADMIN\', \'DATA_STEWARD\') THEN val ELSE {mask_function} END;",')
    print("   ↳ Solution: Complete SQL statement executed as one command")
    
    print(f"\n🎉 This should resolve the 'unexpected <EOF>' SQL compilation error!")
    print("="*80)

if __name__ == "__main__":
    test_final_sql_fix()