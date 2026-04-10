# SQL Masking Policy - Quick Fix Reference

## The Problem ❌

```sql
-- WRONG: Trying to set a policy that doesn't exist
ALTER TABLE "HEALTH_RECORDS" ALTER COLUMN "SSN" SET MASKING POLICY HEALTH_RECORDS_SSN_mask_policy
```

**Error**: Masking policy 'HEALTH_RECORDS_SSN_MASK_POLICY' does not exist

---

## The Solution ✅

### Complete Policy Application Sequence

```sql
BEGIN;

-- 1. CREATE the masking policy (if it doesn't exist)
CREATE MASKING POLICY IF NOT EXISTS HEALTH_RECORDS_SSN_mask_policy_1706012502
AS (val STRING) RETURNS STRING ->
CASE
  WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
  ELSE CONCAT('***-**-', RIGHT(val, 4))
END;

-- 2. UNSET any existing policy first
ALTER TABLE "HEALTH_RECORDS" ALTER COLUMN "SSN" UNSET MASKING POLICY;

-- 3. SET the new policy
ALTER TABLE "HEALTH_RECORDS" ALTER COLUMN "SSN" SET MASKING POLICY HEALTH_RECORDS_SSN_mask_policy_1706012502;

COMMIT;
```

---

## Key Rules for Snowflake Masking Policies

| Statement | Syntax                       | Example                                      |
| --------- | ---------------------------- | -------------------------------------------- |
| CREATE    | Supports `IF NOT EXISTS`     | ✅ `CREATE MASKING POLICY IF NOT EXISTS ...` |
| SET       | Does NOT support `IF EXISTS` | ❌ `SET MASKING POLICY IF EXISTS ...`        |
| DROP      | Supports `IF EXISTS`         | ✅ `DROP MASKING POLICY IF EXISTS ...`       |
| UNSET     | No IF clause                 | ❌ `UNSET MASKING POLICY IF EXISTS ...`      |

---

## What Each Role Sees

```
WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
  ↓
  ACCOUNTADMIN and DATA_STEWARD roles see ORIGINAL data

ELSE CONCAT('***-**-', RIGHT(val, 4))
  ↓
  All other roles see MASKED data
  Example: 111-22-3456 becomes ****-**-3456
```

---

## Example: Full Masking Policy Setup

### Step 1: Create the Policy

```sql
CREATE MASKING POLICY IF NOT EXISTS ssn_mask_policy
AS (val STRING) RETURNS STRING ->
CASE
  WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
  ELSE CONCAT('***-**-', RIGHT(val, 4))
END;
```

### Step 2: Apply to Column

```sql
ALTER TABLE HEALTH_RECORDS ALTER COLUMN SSN SET MASKING POLICY ssn_mask_policy;
```

### Step 3: Verify

```sql
-- Check what role sees
SELECT CURRENT_ROLE();

-- Check SSN visibility
SELECT SSN FROM HEALTH_RECORDS;
-- As ADMIN: 111-22-3456 (unmasked)
-- As ANALYST: ***-**-3456 (masked)
```

---

## Common Mistakes ❌

### 1. IF EXISTS in SET clause

```sql
❌ ALTER TABLE ... SET MASKING POLICY IF EXISTS policy_name
✅ ALTER TABLE ... SET MASKING POLICY policy_name
```

### 2. Policy name case sensitivity

```sql
-- Snowflake converts to UPPERCASE internally
CREATE MASKING POLICY my_policy ...
-- Internally stored as MY_POLICY
-- Can reference as either 'my_policy' or 'MY_POLICY'
```

### 3. Missing CREATE before SET

```sql
❌ Just run SET - policy doesn't exist!
✅ Always CREATE first, then SET
```

### 4. Not handling existing policies

```sql
-- Good practice: Clean up first
DROP MASKING POLICY IF EXISTS old_policy;
CREATE MASKING POLICY IF NOT EXISTS new_policy ...
ALTER TABLE ... SET MASKING POLICY new_policy;
```

---

## Code Where This Was Fixed

**File**: `ai_control_plane.py`

### Function: `_phase_plan()` - Lines 1289-1324

Generates SQL commands for fallback masking policy application

**Key Fix**:

```python
# Now generates proper sequence:
sql_commands.append("BEGIN;")

for col in pii_columns:
    # Step 1: CREATE policy (unique name with timestamp)
    create_policy = (
        f"CREATE MASKING POLICY IF NOT EXISTS {unique_policy_name} "
        f"AS (val STRING) RETURNS STRING -> "
        f"CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val "
        f"ELSE '***MASKED***' END;"
    )
    sql_commands.append(create_policy)

    # Step 2: SET policy (no IF EXISTS)
    set_policy = f'ALTER TABLE "{table}" ALTER COLUMN "{col}" SET MASKING POLICY {unique_policy_name};'
    sql_commands.append(set_policy)

sql_commands.append("COMMIT;")
```

---

## Testing the Fix

### Before (FAILS)

```
Error: Masking policy 'HEALTH_RECORDS_SSN_MASK_POLICY' does not exist or not authorized
```

### After (SUCCEEDS)

```
✅ CREATE MASKING POLICY IF NOT EXISTS ...
✅ ALTER TABLE ... ALTER COLUMN ... SET MASKING POLICY ...
✅ Transaction committed
```

---

## References

- Snowflake Docs: https://docs.snowflake.com/en/sql-reference/sql/create-masking-policy.html
- Masking Policy Best Practices: https://docs.snowflake.com/en/user-guide/security-masking-policy.html

---

**Last Updated**: January 24, 2026
**Status**: ✅ All fixes applied and tested
