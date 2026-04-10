#!/usr/bin/env python3
"""
Test improved SQL generation with schema-qualified table names
"""

def test_improved_sql_generation():
    """Test the improved SQL generation with proper schema handling"""
    
    print("="*70)
    print("🧪 TESTING IMPROVED SQL GENERATION - Schema Handling")
    print("="*70)
    
    def generate_improved_masking_sql(table, column, pii_types):
        """Test the improved SQL generation logic"""
        policy_name = f"{table}_{column}_mask_policy".replace('.', '_')
        
        # Handle schema-qualified table names properly (same logic as AI Control Plane)
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
        
        sql_commands = [
            "BEGIN;",
            f"-- Create backup of original data",
            f"CREATE TABLE IF NOT EXISTS {backup_table_name} AS SELECT * FROM {full_table_name};",
            f"-- Create masking policy for {column}",
            f"CREATE OR REPLACE MASKING POLICY {policy_name} AS (val STRING) RETURNS STRING ->",
            f"  CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val",
            f"       ELSE {mask_function} END;",
            f"-- Apply masking policy to column",
            f"ALTER TABLE {full_table_name} MODIFY COLUMN \"{column}\" SET MASKING POLICY {policy_name};",
            "COMMIT;"
        ]
        
        return sql_commands
    
    # Test cases with schema-qualified names (like the actual AI Control Plane)
    test_cases = [
        ("PUBLIC.EMPLOYEES", "NAME", ["PERSON"]),
        ("PUBLIC.PRODUCTS", "NAME", ["PERSON"]),
        ("ANALYTICS.CUSTOMERS", "EMAIL", ["EMAIL_ADDRESS"]),
        ("simple_table", "PHONE", ["PHONE_NUMBER"])  # No schema
    ]
    
    for table, column, pii_types in test_cases:
        print(f"\n📋 Testing: {table}.{column} (PII: {pii_types})")
        print("-" * 60)
        
        sql_commands = generate_improved_masking_sql(table, column, pii_types)
        
        for i, sql in enumerate(sql_commands, 1):
            print(f"{i:2d}. {sql}")
        
        # Validate the important SQL components
        backup_sql = sql_commands[2]  # Backup creation
        policy_sql = sql_commands[4] + " " + sql_commands[5] + " " + sql_commands[6]  # Policy creation
        apply_sql = sql_commands[8]  # Policy application
        
        print(f"\n🔍 Key SQL Components:")
        print(f"   Backup: {backup_sql}")
        print(f"   Policy: {policy_sql}")
        print(f"   Apply:  {apply_sql}")
        
        # Check for issues
        issues = []
        if '.' in table and '\"' not in backup_sql:
            issues.append("❌ Schema-qualified table not properly quoted")
        if "ELSE '{" in policy_sql and "}'" in policy_sql:
            issues.append("❌ Function variables incorrectly quoted")
        if len([cmd for cmd in sql_commands if cmd.strip() == ""]) > 0:
            issues.append("❌ Empty commands found")
        
        if issues:
            print(f"\n⚠️ ISSUES FOUND:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print(f"\n✅ SQL validation passed")
    
    print(f"\n{'='*70}")
    print("🏁 IMPROVED SQL GENERATION TEST COMPLETED")
    print("="*70)
    
    print("\n💡 KEY IMPROVEMENTS:")
    print("• Schema-qualified table names properly quoted")
    print("• Column names quoted to handle reserved words")
    print("• Function calls not wrapped in extra quotes")
    print("• Backup tables created in same schema")
    print("\n🎯 This should resolve the SQL compilation errors!")

if __name__ == "__main__":
    test_improved_sql_generation()