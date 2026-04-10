# SQL Generation with Actual Snowflake Roles

## The Problem in Old Code

Your query: `"mask pii in RESIDENTIAL_ADDRESS table for analyst roles"`

### Old SQL (❌ Would fail)

```sql
CREATE OR REPLACE MASKING POLICY ssn_mask_policy AS (val STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD')  -- ❌ These roles don't exist!
       THEN val
       ELSE CONCAT('***-**-', RIGHT(val, 4))
  END;
```

**Error:** These roles (`ADMIN`, `DATA_STEWARD`) don't exist in Snowflake. The CASE statement would fail.

## The Solution with Actual Roles

### New SQL (✅ Works correctly)

```sql
-- System detects available roles and filters for admin ones
-- Available: ACCOUNTADMIN, ANALYST_ROLE, HR_ROLE, ORGADMIN, PUBLIC, SECURITYADMIN, SYSADMIN, USERADMIN
-- Admin roles detected: ACCOUNTADMIN, SYSADMIN, SECURITYADMIN

CREATE OR REPLACE MASKING POLICY ssn_mask_policy AS (val STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN')  -- ✅ Real roles!
       THEN val  -- These roles see UNMASKED data
       ELSE CONCAT('***-**-', RIGHT(val, 4))  -- Others see MASKED data
  END;
```

## Examples by Role

### Apply Policy to RESIDENTIAL_ADDRESS.SSN

For query: `"mask ssn for analyst roles"`

**Policy Created:**

```sql
CREATE OR REPLACE MASKING POLICY ssn_masking_analyst AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN') THEN val
    ELSE CONCAT('***-**-', RIGHT(val, 4))
  END;

ALTER TABLE RESIDENTIAL_ADDRESS
  MODIFY COLUMN SSN SET MASKING POLICY ssn_masking_analyst;
```

**What Each Role Sees:**

| Role          | SSN Value    | Why                                 |
| ------------- | ------------ | ----------------------------------- |
| ACCOUNTADMIN  | 123-45-6789  | In admin roles list → sees unmasked |
| SYSADMIN      | 123-45-6789  | In admin roles list → sees unmasked |
| SECURITYADMIN | 123-45-6789  | In admin roles list → sees unmasked |
| ANALYST_ROLE  | **\*-**-6789 | Not in admin list → sees masked     |
| HR_ROLE       | **\*-**-6789 | Not in admin list → sees masked     |
| PUBLIC        | **\*-**-6789 | Not in admin list → sees masked     |

## Role Detection Flow

### Step 1: Fetch Available Roles

```python
SHOW ROLES  # Snowflake command
```

Returns:

```
ACCOUNTADMIN
ANALYST_ROLE
HR_ROLE
ORGADMIN
PUBLIC
SECURITYADMIN
SNOWFLAKE_LEARNING_ROLE
SYSADMIN
USERADMIN
```

### Step 2: Detect Admin Roles

Filter for keywords: `['admin', 'sysadmin', 'security', 'steward']`

Matches:

- `ACCOUNTADMIN` ✅ (contains 'admin')
- `SYSADMIN` ✅ (contains 'sysadmin')
- `SECURITYADMIN` ✅ (contains 'security')

Result: `['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN']`

### Step 3: Extract Role Directive

Query: `"mask ssn for analyst roles"`

- Extract role: `ANALYST_ROLE`
- Pattern: `for` (not negated)
- Masked for: `['ANALYST_ROLE']`
- Visible for: `['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN']` ← From Step 2

### Step 4: Generate SQL

```sql
CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN')  -- From Step 3
     THEN val  -- Unmasked
     ELSE CONCAT('***-**-', RIGHT(val, 4))  -- Masked
END
```

## Different Scenarios

### Scenario A: "mask email for hr roles"

```python
role_directive = {
    'role': 'HR_ROLE',
    'masked_for_roles': ['HR_ROLE'],
    'visible_for_roles': ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN']
}

# SQL: CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN')
#           THEN val ELSE MASKED END
```

Result:

- HR_ROLE → Sees: **_@_**.com (MASKED)
- ACCOUNTADMIN → Sees: user@example.com (UNMASKED)
- Others → Sees: **_@_**.com (MASKED)

### Scenario B: "mask phone not for analyst"

```python
role_directive = {
    'role': 'ANALYST_ROLE',
    'masked_for_roles': ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN'],
    'visible_for_roles': ['ANALYST_ROLE']
}

# SQL: CASE WHEN CURRENT_ROLE() IN ('ANALYST_ROLE')
#           THEN val ELSE MASKED END
```

Result:

- ANALYST_ROLE → Sees: 123-456-7890 (UNMASKED)
- ACCOUNTADMIN → Sees: **_-_**-7890 (MASKED)
- SYSADMIN → Sees: **_-_**-7890 (MASKED)
- Others → Sees: **_-_**-7890 (MASKED)

### Scenario C: "mask ssn" (no role specified)

```python
role_directive = {
    'role': None,
    'masked_for_roles': ['PUBLIC'],
    'visible_for_roles': ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN']
}

# SQL: CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN')
#           THEN val ELSE MASKED END
```

Result:

- ACCOUNTADMIN → Sees: 123-45-6789 (UNMASKED) ← Admin
- SYSADMIN → Sees: 123-45-6789 (UNMASKED) ← Admin
- SECURITYADMIN → Sees: 123-45-6789 (UNMASKED) ← Admin
- All other roles → Sees: **\*-**-6789 (MASKED)

## Testing the Generated SQL

```sql
-- Check current role
SELECT CURRENT_ROLE();

-- If ANALYST_ROLE:
SELECT SSN FROM RESIDENTIAL_ADDRESS LIMIT 1;
-- Output: ***-**-6789 (MASKED because ANALYST_ROLE not in visible_for_roles)

-- If ACCOUNTADMIN:
SELECT SSN FROM RESIDENTIAL_ADDRESS LIMIT 1;
-- Output: 123-45-6789 (UNMASKED because ACCOUNTADMIN in visible_for_roles)
```

## Key Improvements

✅ **Role names are real** - No more 'ADMIN' or 'DATA_STEWARD'
✅ **Automatic detection** - Finds admin roles in your system
✅ **Correct masking** - SQL won't fail due to non-existent roles
✅ **Flexible** - Works with any set of available roles
✅ **Traceable** - Logs show which roles were detected and used
