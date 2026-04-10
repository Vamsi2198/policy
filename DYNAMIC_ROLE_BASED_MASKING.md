# Dynamic Role-Based Masking Implementation

## Overview

The system now supports **dynamic, role-aware masking policies** that automatically adapt based on user intent. You can now specify which roles should see masked vs unmasked data directly in your natural language query.

## Feature: Role-Based Masking Directives

### What Changed

The masking policy CASE statements are now **dynamically generated** based on your command:

#### Example 1: "mask ssn in HEALTH_RECORDS table for analyst roles"

- **ANALYST_ROLE**: Sees `***-**-3456` (MASKED)
- **ADMIN/DATA_STEWARD**: See `111-22-3456` (UNMASKED)
- **SQL Generated**:

```sql
CREATE MASKING POLICY policy_name AS (val STRING) RETURNS STRING ->
CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD')
     THEN val
     ELSE CONCAT('***-**-', RIGHT(val, 4))
END;
```

#### Example 2: "mask ssn in HEALTH_RECORDS table not for analyst roles"

- **ANALYST_ROLE**: Sees `111-22-3456` (UNMASKED)
- **ADMIN/DATA_STEWARD**: See `***-**-3456` (MASKED)
- **SQL Generated**:

```sql
CREATE MASKING POLICY policy_name AS (val STRING) RETURNS STRING ->
CASE WHEN CURRENT_ROLE() IN ('ANALYST_ROLE')
     THEN val
     ELSE CONCAT('***-**-', RIGHT(val, 4))
END;
```

#### Example 3: "mask ssn in HEALTH_RECORDS table" (no role specified)

- **ADMIN/DATA_STEWARD**: See `111-22-3456` (UNMASKED) - Default
- **Other roles**: See `***-**-3456` (MASKED)
- **SQL Generated**:

```sql
CREATE MASKING POLICY policy_name AS (val STRING) RETURNS STRING ->
CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD')
     THEN val
     ELSE CONCAT('***-**-', RIGHT(val, 4))
END;
```

## Supported Role Keywords

The system recognizes these role patterns:

### Supported Roles

- `analyst` / `analyst_role` / `analyst_roles` → `ANALYST_ROLE`
- `hr` / `hr_role` / `hr_roles` → `HR_ROLE`
- `finance` / `finance_role` / `finance_roles` → `FINANCE_ROLE`
- `it` / `it_role` / `it_roles` → `IT_ROLE`
- `admin` / `admin_role` / `admin_roles` → `ADMIN`
- `data_steward` / `data_steward_role` → `DATA_STEWARD`
- `public` → `PUBLIC`

### Negation Keywords

- `not for` - Inverts masking behavior
- `except` - Synonym for "not for"
- `exclude` - Synonym for "not for"
- `for` - Normal masking direction

## Implementation Details

### New Method: `_extract_role_directive(user_query: str) -> Dict[str, Any]`

This method parses natural language queries and extracts role-based masking intent:

```python
role_directive = {
    'role': str,                    # Extracted role (e.g., 'ANALYST_ROLE')
    'negate': bool,                 # True if 'not for' was specified
    'masked_for_roles': List[str],  # Roles that see MASKED data
    'visible_for_roles': List[str]  # Roles that see UNMASKED data
}
```

### Updated Method: `_generate_masking_sql(..., role_directive: Dict[str, Any] = None)`

Now accepts optional `role_directive` parameter to generate dynamic CASE statements:

```python
# Old behavior (hardcoded)
CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val ...

# New behavior (dynamic)
CASE WHEN CURRENT_ROLE() IN ('ANALYST_ROLE') THEN val ...  # If "for analyst"
CASE WHEN CURRENT_ROLE() NOT IN ('ANALYST_ROLE') THEN val ...  # If "not for analyst"
```

### Updated Method: `_phase_plan(..., user_query: str = None)`

Phase 3 (PLAN) now accepts the original user query to extract role directives:

1. Extracts role directive from query
2. Passes it to `_generate_masking_sql()`
3. Generates dynamic CASE statements for all PII columns
4. Logs role-based masking decisions

## Masking Functions (Unchanged)

The masking format depends on PII type:

| PII Type | Mask Pattern   | Example                            |
| -------- | -------------- | ---------------------------------- |
| SSN      | `***-**-XXXX`  | `111-22-3456` → `***-**-3456`      |
| EMAIL    | `XXX@***.com`  | `john@example.com` → `joh@***.com` |
| PHONE    | `***-***-XXXX` | `555-123-4567` → `***-***-4567`    |
| GENERIC  | `***MASKED***` | `any_value` → `***MASKED***`       |

## Workflow: How It Works End-to-End

### 1. User Query

```
"mask ssn in HEALTH_RECORDS table for analyst roles"
```

### 2. Phase 1: OBSERVE

- Extracts intent: `MASK`
- Extracts table: `HEALTH_RECORDS`
- Confidence: High (clear intent and table)

### 3. Phase 2: ANALYZE

- Detects SSN column as PII
- Finds 10,000 rows affected
- Risk assessment: MEDIUM

### 4. Phase 3: PLAN (NEW DYNAMIC ROLE LOGIC)

- Extracts role directive:
  - Role: `ANALYST_ROLE`
  - Negate: `False` (because "for", not "not for")
  - Visible roles: `['ADMIN', 'DATA_STEWARD']` (they see unmasked)
  - Masked roles: `['ANALYST_ROLE']` (this role sees masked)
- Generates SQL with dynamic CASE:
  ```sql
  CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD')
       THEN val
       ELSE CONCAT('***-**-', RIGHT(val, 4))
  END
  ```

### 5. Phase 4: SIMULATE

- Shows before/after states
- Impacts: ANALYST_ROLE sees masked, ADMIN sees unmasked
- Risk: LOW

### 6. Phase 5: EXECUTE (if approved)

- Creates policy with dynamic CASE
- Sets policy on SSN column
- Commit transaction

### 7. Phase 6: LEARN

- Verifies policy effectiveness
- Records behavior for future similar queries

## Testing

Run the test suite to verify all role directives:

```bash
python test_dynamic_masking.py
```

Expected output:

```
TEST 1: mask ssn ... for analyst roles
  ✓ ADMIN sees UNMASKED
  ✗ ANALYST_ROLE sees MASKED
  ✓ DATA_STEWARD sees UNMASKED

TEST 2: mask ssn ... not for analyst roles
  ✗ ADMIN sees MASKED
  ✓ ANALYST_ROLE sees UNMASKED
  ✗ DATA_STEWARD sees MASKED
  ...
```

## Query Examples

### Analyst Should See Masked

```
"mask ssn in HEALTH_RECORDS for analyst roles"
"mask email in CUSTOMERS for analyst"
"protect phone numbers for analysts"
```

### Analyst Should See Unmasked (Everyone Else Masked)

```
"mask ssn in HEALTH_RECORDS not for analyst roles"
"mask ssn except analyst"
"mask ssn exclude analyst"
```

### HR Role Should See Masked

```
"mask salary in EMPLOYEES for hr"
"mask ssn in HEALTH_RECORDS for hr roles"
```

### Default (Admin/Steward See Unmasked)

```
"mask ssn in HEALTH_RECORDS"
"mask email in CUSTOMERS"
"protect all PII"
```

## Database Impact

For each role directive, the SQL generated includes:

```sql
BEGIN;
-- Create backup
CREATE TABLE IF NOT EXISTS HEALTH_RECORDS_backup AS SELECT * FROM HEALTH_RECORDS;

-- Clean up existing policy
ALTER TABLE HEALTH_RECORDS ALTER COLUMN SSN UNSET MASKING POLICY;
DROP MASKING POLICY IF EXISTS policy_name;

-- Create new policy with DYNAMIC role-based CASE
CREATE MASKING POLICY policy_name_1706012502 AS (val STRING) RETURNS STRING ->
CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val
     ELSE CONCAT('***-**-', RIGHT(val, 4))
END;

-- Apply policy
ALTER TABLE HEALTH_RECORDS ALTER COLUMN SSN SET MASKING POLICY policy_name_1706012502;
COMMIT;
```

## Error Handling

If role directive extraction fails:

- System defaults to: `ADMIN` and `DATA_STEWARD` see unmasked
- All other roles see masked data
- Graceful fallback ensures masking still happens

## Backward Compatibility

- Queries without role directives (e.g., "mask ssn") still work
- Default behavior: ADMIN/DATA_STEWARD see unmasked
- Existing masking policies unaffected
- New queries use dynamic CASE statements

## Future Enhancements

Potential improvements:

1. **Multiple role specifications**: "mask ssn for analyst and hr but not for finance"
2. **Fine-grained masking levels**: "mask ssn (full masking) vs email (partial masking)"
3. **Time-based directives**: "mask ssn for analyst after 5pm"
4. **Context-aware masking**: "mask ssn for analyst on reports only"
5. **Conditional masking**: "mask ssn if department = HR"

## Support & Troubleshooting

### Issue: Role not recognized

- Check spelling: Use `analyst_role` or `analyst_roles`
- Check for typos in role names
- Run test with `python test_dynamic_masking.py`

### Issue: Masking not applied

- Verify Snowflake connection is active
- Check user has `CREATE MASKING POLICY` privilege
- Verify table/column exist

### Issue: Wrong roles can see data

- Review extracted role directive in logs
- Check generated SQL CASE statement
- Verify `CURRENT_ROLE()` context in Snowflake
