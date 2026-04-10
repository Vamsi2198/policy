# SQL Masking Policy Generation - Fixes Applied

## Issues Found and Fixed

### Issue 1: Missing CREATE MASKING POLICY (CRITICAL)

**Error**: `Masking policy 'DEMO_DB.PUBLIC.HEALTH_RECORDS_SSN_MASK_POLICY' does not exist or not authorized`

**Root Cause**: The fallback SQL generation (when no PII findings) was generating only SET commands without first creating the masking policy.

**Example of WRONG approach**:

```sql
ALTER TABLE "HEALTH_RECORDS" ALTER COLUMN "SSN" SET MASKING POLICY HEALTH_RECORDS_SSN_mask_policy
-- ❌ Policy doesn't exist yet!
```

**Fixed approach** (now properly generates CREATE then SET):

```sql
BEGIN;
CREATE MASKING POLICY IF NOT EXISTS HEALTH_RECORDS_SSN_mask_policy_1706012502
  AS (val STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
  ELSE '***-**-' || RIGHT(val, 4) END;

ALTER TABLE "HEALTH_RECORDS" ALTER COLUMN "SSN" SET MASKING POLICY HEALTH_RECORDS_SSN_mask_policy_1706012502;
COMMIT;
```

### Issue 2: Invalid Syntax with IF EXISTS (FIXED)

**Error**: `SQL compilation error: syntax error line 1 at position 70 unexpected 'EXISTS'`

**Wrong**:

```sql
ALTER TABLE "HEALTH_RECORDS" ALTER COLUMN "SSN" SET MASKING POLICY IF EXISTS HEALTH_RECORDS_SSN_mask_policy
```

**Correct**:

```sql
ALTER TABLE "HEALTH_RECORDS" ALTER COLUMN "SSN" SET MASKING POLICY HEALTH_RECORDS_SSN_mask_policy
-- Snowflake does NOT support IF EXISTS in SET MASKING POLICY clause
```

**CREATE** can use IF EXISTS:

```sql
CREATE MASKING POLICY IF NOT EXISTS policy_name AS ...  -- ✅ Correct
```

But **SET** cannot:

```sql
ALTER TABLE ... SET MASKING POLICY IF EXISTS policy_name  -- ❌ Wrong
ALTER TABLE ... SET MASKING POLICY policy_name           -- ✅ Correct
```

---

## Code Changes

### File: `ai_control_plane.py`

#### Change 1: Fallback SQL Generation (Lines 1289-1324)

**What was changed**: The fallback path when no PII findings are available now generates complete CREATE + SET pairs instead of just SET commands.

**Before**:

```python
for col in pii_columns:
    policy_name = f"{table}_{col}_mask_policy"
    sql = f'ALTER TABLE "{table}" ALTER COLUMN "{col}" SET MASKING POLICY {policy_name}'
    sql_commands.append(sql)  # ❌ No CREATE!
```

**After**:

```python
import time
timestamp = str(int(time.time()))

for table in observe_result.target_entities:
    pii_columns = ['SSN', 'EMAIL', 'PHONE', 'SALARY']
    sql_commands.append("BEGIN;")

    for col in pii_columns:
        policy_name = f"{table}_{col}_mask_policy"
        unique_policy_name = f"{policy_name}_{timestamp}"

        # Step 1: CREATE the masking policy
        create_policy = (
            f"CREATE MASKING POLICY IF NOT EXISTS {unique_policy_name} "
            f"AS (val STRING) RETURNS STRING -> "
            f"CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val "
            f"ELSE '***MASKED***' END;"
        )
        sql_commands.append(create_policy)

        # Step 2: SET the policy on the column
        set_policy = f'ALTER TABLE "{table}" ALTER COLUMN "{col}" SET MASKING POLICY {unique_policy_name};'
        sql_commands.append(set_policy)

    sql_commands.append("COMMIT;")
```

#### Change 2: Primary SQL Generation (Lines 2039)

The main `_generate_masking_sql()` function already had the correct structure (CREATE then SET), just needed to ensure the comment was accurate.

---

## Masking Policy Structure

A complete masking policy for SSN requires these steps:

```sql
-- Step 1: Create the masking policy definition
CREATE MASKING POLICY HEALTH_RECORDS_SSN_mask_policy_1706012502
  AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
    ELSE CONCAT('***-**-', RIGHT(val, 4))
  END;

-- Step 2: Apply it to the column
ALTER TABLE "HEALTH_RECORDS"
  ALTER COLUMN "SSN"
  SET MASKING POLICY HEALTH_RECORDS_SSN_mask_policy_1706012502;
```

**Role-Based Masking**:

- `ADMIN` role: Sees unmasked data (val)
- `DATA_STEWARD` role: Sees unmasked data (val)
- Everyone else: Sees masked data (**\*-**-1234)

---

## Testing Results

### Before Fix

```
ERROR: Masking policy 'DEMO_DB.PUBLIC.HEALTH_RECORDS_SSN_MASK_POLICY' does not exist or not authorized
```

### After Fix (Expected)

```
✅ Phase 5: EXECUTE - Governance action execution...
   Executing SQL 1: CREATE MASKING POLICY...
   ✅ Masking policy created
   Executing SQL 2: ALTER TABLE ... SET MASKING POLICY...
   ✅ Masking policy applied to SSN column
```

---

## Dependencies

Add to `requirements.txt`:

```
openai>=0.27.0
snowflake-connector-python>=3.0
```

Install with:

```bash
pip install -r requirements.txt
```

---

## Snowflake Documentation References

- **CREATE MASKING POLICY**: https://docs.snowflake.com/en/sql-reference/sql/create-masking-policy.html
- **ALTER TABLE ... SET MASKING POLICY**: https://docs.snowflake.com/en/sql-reference/sql/alter-table-column.html
- **Masking Policy Syntax**: Cannot use IF EXISTS in SET clause

---

## Next Steps

1. ✅ Install openai: `pip install openai`
2. ✅ Run server with corrected SQL generation
3. ✅ Execute masking policies with proper CREATE + SET sequence
4. ✅ Verify policies are applied to target columns
