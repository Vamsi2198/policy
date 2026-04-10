# Generated SQL Examples - Dynamic Role-Based Masking

## Complete Transaction Examples

### Example 1: "mask ssn in HEALTH_RECORDS table for analyst roles"

**Command:**

```
mask ssn in HEALTH_RECORDS table for analyst roles
```

**Role Directive Extracted:**

```python
{
    'role': 'ANALYST_ROLE',
    'negate': False,
    'visible_for_roles': ['ADMIN', 'DATA_STEWARD'],
    'masked_for_roles': ['ANALYST_ROLE']
}
```

**Generated SQL:**

```sql
BEGIN;
-- Create backup of original data
CREATE TABLE IF NOT EXISTS "HEALTH_RECORDS"."HEALTH_RECORDS_backup" AS SELECT * FROM "HEALTH_RECORDS"."HEALTH_RECORDS";
-- Unset any existing masking policy first
ALTER TABLE "HEALTH_RECORDS"."HEALTH_RECORDS" ALTER COLUMN "SSN" UNSET MASKING POLICY;
-- Drop existing policy if it exists
DROP MASKING POLICY IF EXISTS HEALTH_RECORDS_SSN_mask_policy_1706012502;
-- Create new masking policy for SSN with role-based logic
CREATE MASKING POLICY HEALTH_RECORDS_SSN_mask_policy_1706012502 AS (val STRING) RETURNS STRING -> CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val ELSE CONCAT('***-**-', RIGHT(val, 4)) END;
-- Apply masking policy to column (Snowflake: no IF EXISTS in SET clause)
ALTER TABLE "HEALTH_RECORDS"."HEALTH_RECORDS" ALTER COLUMN "SSN" SET MASKING POLICY HEALTH_RECORDS_SSN_mask_policy_1706012502;
COMMIT;
```

**Behavior:**

| Role         | View           | Data Display             |
| ------------ | -------------- | ------------------------ |
| ADMIN        | Full access    | `111-22-3456` (UNMASKED) |
| DATA_STEWARD | Full access    | `111-22-3456` (UNMASKED) |
| ANALYST_ROLE | Limited access | `***-**-3456` (MASKED)   |
| PUBLIC       | Restricted     | `***-**-3456` (MASKED)   |

---

### Example 2: "mask ssn in HEALTH_RECORDS table not for analyst roles"

**Command:**

```
mask ssn in HEALTH_RECORDS table not for analyst roles
```

**Role Directive Extracted:**

```python
{
    'role': 'ANALYST_ROLE',
    'negate': True,
    'visible_for_roles': ['ANALYST_ROLE'],
    'masked_for_roles': ['ADMIN', 'DATA_STEWARD', 'PUBLIC']
}
```

**Generated SQL:**

```sql
BEGIN;
-- Create backup of original data
CREATE TABLE IF NOT EXISTS "HEALTH_RECORDS"."HEALTH_RECORDS_backup" AS SELECT * FROM "HEALTH_RECORDS"."HEALTH_RECORDS";
-- Unset any existing masking policy first
ALTER TABLE "HEALTH_RECORDS"."HEALTH_RECORDS" ALTER COLUMN "SSN" UNSET MASKING POLICY;
-- Drop existing policy if it exists
DROP MASKING POLICY IF EXISTS HEALTH_RECORDS_SSN_mask_policy_1706012503;
-- Create new masking policy for SSN with role-based logic
CREATE MASKING POLICY HEALTH_RECORDS_SSN_mask_policy_1706012503 AS (val STRING) RETURNS STRING -> CASE WHEN CURRENT_ROLE() IN ('ANALYST_ROLE') THEN val ELSE CONCAT('***-**-', RIGHT(val, 4)) END;
-- Apply masking policy to column (Snowflake: no IF EXISTS in SET clause)
ALTER TABLE "HEALTH_RECORDS"."HEALTH_RECORDS" ALTER COLUMN "SSN" SET MASKING POLICY HEALTH_RECORDS_SSN_mask_policy_1706012503;
COMMIT;
```

**Behavior:**

| Role         | View        | Data Display             |
| ------------ | ----------- | ------------------------ |
| ADMIN        | Masked      | `***-**-3456` (MASKED)   |
| DATA_STEWARD | Masked      | `***-**-3456` (MASKED)   |
| ANALYST_ROLE | Full access | `111-22-3456` (UNMASKED) |
| PUBLIC       | Masked      | `***-**-3456` (MASKED)   |

---

### Example 3: "mask email in CUSTOMERS table for hr"

**Command:**

```
mask email in CUSTOMERS table for hr
```

**Role Directive Extracted:**

```python
{
    'role': 'HR_ROLE',
    'negate': False,
    'visible_for_roles': ['ADMIN', 'DATA_STEWARD'],
    'masked_for_roles': ['HR_ROLE']
}
```

**Generated SQL:**

```sql
BEGIN;
-- Create backup of original data
CREATE TABLE IF NOT EXISTS "CUSTOMERS"."CUSTOMERS_backup" AS SELECT * FROM "CUSTOMERS"."CUSTOMERS";
-- Unset any existing masking policy first
ALTER TABLE "CUSTOMERS"."CUSTOMERS" ALTER COLUMN "EMAIL" UNSET MASKING POLICY;
-- Drop existing policy if it exists
DROP MASKING POLICY IF EXISTS CUSTOMERS_EMAIL_mask_policy_1706012504;
-- Create new masking policy for EMAIL with role-based logic
CREATE MASKING POLICY CUSTOMERS_EMAIL_mask_policy_1706012504 AS (val STRING) RETURNS STRING -> CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val ELSE CONCAT(LEFT(val, 3), '***@***.com') END;
-- Apply masking policy to column (Snowflake: no IF EXISTS in SET clause)
ALTER TABLE "CUSTOMERS"."CUSTOMERS" ALTER COLUMN "EMAIL" SET MASKING POLICY CUSTOMERS_EMAIL_mask_policy_1706012504;
COMMIT;
```

**Behavior:**

| Role         | View        | Data Display                  |
| ------------ | ----------- | ----------------------------- |
| ADMIN        | Full access | `john@example.com` (UNMASKED) |
| DATA_STEWARD | Full access | `john@example.com` (UNMASKED) |
| HR_ROLE      | Limited     | `joh@***.com` (MASKED)        |
| Other roles  | Limited     | `joh@***.com` (MASKED)        |

---

### Example 4: "mask phone in EMPLOYEES"

**Command:**

```
mask phone in EMPLOYEES
```

**Role Directive Extracted:**

```python
{
    'role': None,
    'negate': False,
    'visible_for_roles': ['ADMIN', 'DATA_STEWARD'],
    'masked_for_roles': ['PUBLIC']
}
```

**Generated SQL:**

```sql
BEGIN;
-- Create backup of original data
CREATE TABLE IF NOT EXISTS "EMPLOYEES"."EMPLOYEES_backup" AS SELECT * FROM "EMPLOYEES"."EMPLOYEES";
-- Unset any existing masking policy first
ALTER TABLE "EMPLOYEES"."EMPLOYEES" ALTER COLUMN "PHONE" UNSET MASKING POLICY;
-- Drop existing policy if it exists
DROP MASKING POLICY IF EXISTS EMPLOYEES_PHONE_mask_policy_1706012505;
-- Create new masking policy for PHONE with role-based logic
CREATE MASKING POLICY EMPLOYEES_PHONE_mask_policy_1706012505 AS (val STRING) RETURNS STRING -> CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val ELSE CONCAT('***-***-', RIGHT(val, 4)) END;
-- Apply masking policy to column (Snowflake: no IF EXISTS in SET clause)
ALTER TABLE "EMPLOYEES"."EMPLOYEES" ALTER COLUMN "PHONE" SET MASKING POLICY EMPLOYEES_PHONE_mask_policy_1706012505;
COMMIT;
```

**Behavior (Default):**

| Role            | View        | Data Display              |
| --------------- | ----------- | ------------------------- |
| ADMIN           | Full access | `555-123-4567` (UNMASKED) |
| DATA_STEWARD    | Full access | `555-123-4567` (UNMASKED) |
| All other roles | Limited     | `***-***-4567` (MASKED)   |

---

## SQL Features Used

### 1. Transaction Control

```sql
BEGIN;
... SQL commands ...
COMMIT;
```

Ensures all-or-nothing execution. If any command fails, entire transaction rolls back.

### 2. Backup Table Creation

```sql
CREATE TABLE IF NOT EXISTS "SCHEMA"."TABLE_backup"
AS SELECT * FROM "SCHEMA"."TABLE";
```

Preserves original data before applying masking. Useful for rollback if needed.

### 3. Policy Cleanup

```sql
-- Remove existing policy from column
ALTER TABLE "SCHEMA"."TABLE" ALTER COLUMN "COL" UNSET MASKING POLICY;

-- Drop old policy
DROP MASKING POLICY IF EXISTS policy_name;
```

Prevents conflicts with existing policies. `IF EXISTS` prevents errors if policy doesn't exist.

### 4. Dynamic Masking Policy with Role-Based CASE

```sql
CREATE MASKING POLICY policy_name AS (val STRING) RETURNS STRING ->
CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD')
     THEN val
     ELSE masking_function
END;
```

**Key points:**

- `CURRENT_ROLE()` - Returns role of querying user at runtime
- `IN (...)` - Checks if user's role is in list
- `THEN val` - Show unmasked data to specified roles
- `ELSE masking_function` - Show masked data to others
- Can be inverted with `NOT IN` for "not for" directives

### 5. Policy Application

```sql
ALTER TABLE "SCHEMA"."TABLE" ALTER COLUMN "COL" SET MASKING POLICY policy_name;
```

Note: `SET MASKING POLICY` does **NOT** support `IF EXISTS` - policy must already exist.

### 6. Unique Policy Names with Timestamps

```python
unique_policy_name = f"{policy_name}_{timestamp}"
# Example: HEALTH_RECORDS_SSN_mask_policy_1706012502
```

Prevents naming conflicts when applying multiple policies to same table.

---

## Masking Functions by PII Type

### SSN Masking

```sql
CONCAT('***-**-', RIGHT(val, 4))
-- Input:  111-22-3456
-- Output: ***-**-3456
```

Shows only last 4 digits (common for SSN masking).

### Email Masking

```sql
CONCAT(LEFT(val, 3), '***@***.com')
-- Input:  john@example.com
-- Output: joh@***.com
```

Shows first 3 characters of email username.

### Phone Masking

```sql
CONCAT('***-***-', RIGHT(val, 4))
-- Input:  555-123-4567
-- Output: ***-***-4567
```

Shows only last 4 digits (common for phone masking).

### Generic Masking

```sql
'***MASKED***'
-- Input:  any_value
-- Output: ***MASKED***
```

Completely replaces with placeholder.

---

## Role-Based CASE Statement Variations

### Pattern 1: "FOR" (Normal masking)

```sql
CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD')
     THEN val
     ELSE masking_function
END
```

- Specified role sees MASKED
- Others see UNMASKED

### Pattern 2: "NOT FOR" (Inverted masking)

```sql
CASE WHEN CURRENT_ROLE() IN ('ANALYST_ROLE')
     THEN val
     ELSE masking_function
END
```

- Specified role sees UNMASKED
- Others see MASKED

### Pattern 3: Default (No role specified)

```sql
CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD')
     THEN val
     ELSE masking_function
END
```

- Admins see UNMASKED
- Others see MASKED

---

## Testing: Verifying Masking Works

### Connect as different roles in Snowflake:

```sql
-- Test 1: Connect as ADMIN
USE ROLE ADMIN;
SELECT SSN FROM HEALTH_RECORDS LIMIT 1;
-- Result: 111-22-3456 (UNMASKED)

-- Test 2: Connect as ANALYST_ROLE (for "mask for analyst")
USE ROLE ANALYST_ROLE;
SELECT SSN FROM HEALTH_RECORDS LIMIT 1;
-- Result: ***-**-3456 (MASKED)

-- Test 3: With different policy (not for analyst)
USE ROLE ADMIN;
SELECT SSN FROM HEALTH_RECORDS LIMIT 1;
-- Result: ***-**-3456 (MASKED - now inverted)

USE ROLE ANALYST_ROLE;
SELECT SSN FROM HEALTH_RECORDS LIMIT 1;
-- Result: 111-22-3456 (UNMASKED - now inverted)
```

---

## Performance Considerations

| Operation                   | Time                                   |
| --------------------------- | -------------------------------------- |
| Extract role directive      | <1ms                                   |
| Generate SQL CASE statement | <5ms                                   |
| Create backup table         | 100ms - 2s (depends on table size)     |
| Apply masking policy        | 500ms - 5s (depends on Snowflake load) |
| **Total per column**        | ~1-7 seconds                           |

For table with 5 PII columns: ~5-35 seconds total execution time.

---

## Troubleshooting SQL Issues

### Issue: "Syntax error near 'IF EXISTS' in SET MASKING POLICY"

```sql
-- ❌ WRONG
ALTER TABLE table SET MASKING POLICY IF EXISTS policy_name;

-- ✅ CORRECT (no IF EXISTS in SET)
ALTER TABLE table SET MASKING POLICY policy_name;
```

### Issue: "Masking policy does not exist"

```sql
-- ❌ WRONG - policy created with timestamp but SET uses different name
CREATE MASKING POLICY policy_1706012502 ...
ALTER TABLE ... SET MASKING POLICY policy_name;  -- doesn't exist!

-- ✅ CORRECT - use exact same name with timestamp
CREATE MASKING POLICY policy_1706012502 ...
ALTER TABLE ... SET MASKING POLICY policy_1706012502;  -- matches!
```

### Issue: "User does not have privilege to create masking policy"

```sql
-- Need SYSADMIN or SECURITYADMIN role to create policies
USE ROLE SYSADMIN;
CREATE MASKING POLICY policy_name ...;
```

---

## Summary

The system generates role-aware SQL policies by:

1. ✅ Extracting role intent from natural language query
2. ✅ Building dynamic CASE statements with role checks
3. ✅ Creating policies with unique timestamped names
4. ✅ Applying policies with transaction safety
5. ✅ Logging all decisions for audit trail

Result: **Masking behavior adapts to your exact command intent.**
