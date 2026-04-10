# Role Detection and Masking Flow Diagram

## System Architecture

```
User Query
    │
    ├─────────────────────────────────────────────────────────┐
    │                                                           │
    ▼                                                           ▼
Extract Role Directive                              Get Available Roles
"mask ssn for analyst"                              from Snowflake
    │                                                   │
    │ Extract: ANALYST_ROLE                            │ SHOW ROLES
    │ Pattern: "for" (not negated)                     │
    │                                                   ▼
    │                                   [ACCOUNTADMIN, ANALYST_ROLE,
    │                                    HR_ROLE, SYSADMIN, ...]
    │                                           │
    │                                           │ Filter for admin keywords
    │                                           │ ('admin', 'sysadmin', 'security', 'steward')
    │                                           │
    │                                           ▼
    │                                   [ACCOUNTADMIN, SYSADMIN, SECURITYADMIN]
    │                                           │
    └──────────────────────┬────────────────────┘
                           │
                           ▼
        ┌─────────────────────────────────────┐
        │  Role Directive Dict                │
        ├─────────────────────────────────────┤
        │ role: 'ANALYST_ROLE'                │
        │ masked_for_roles: ['ANALYST_ROLE']  │
        │ visible_for_roles: [                │
        │   'ACCOUNTADMIN',                   │
        │   'SYSADMIN',                       │
        │   'SECURITYADMIN'                   │
        │ ]                                   │
        └─────────────────────────────────────┘
                           │
                           ▼
        Generate SQL with actual role names
                           │
                           ▼
    ┌───────────────────────────────────────────────────────┐
    │ CASE WHEN CURRENT_ROLE() IN                           │
    │   ('ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN')       │
    │ THEN val  -- Unmasked                                │
    │ ELSE CONCAT('***-**-', RIGHT(val, 4))  -- Masked     │
    │ END                                                    │
    └───────────────────────────────────────────────────────┘
```

## Role Visibility Matrix

### Query: "mask ssn for analyst"

```
Role             │ SQL Condition                    │ Result
─────────────────┼──────────────────────────────────┼────────────────
ANALYST_ROLE     │ IN admin list? NO               │ MASKED ●●●-●●-6789
ACCOUNTADMIN     │ IN admin list? YES              │ UNMASKED 123-45-6789
SYSADMIN         │ IN admin list? YES              │ UNMASKED 123-45-6789
SECURITYADMIN    │ IN admin list? YES              │ UNMASKED 123-45-6789
HR_ROLE          │ IN admin list? NO               │ MASKED ●●●-●●-6789
PUBLIC           │ IN admin list? NO               │ MASKED ●●●-●●-6789
```

### Query: "mask ssn not for analyst"

```
Role             │ SQL Condition                    │ Result
─────────────────┼──────────────────────────────────┼────────────────
ANALYST_ROLE     │ IN visible list? YES             │ UNMASKED 123-45-6789
ACCOUNTADMIN     │ IN visible list? NO              │ MASKED ●●●-●●-6789
SYSADMIN         │ IN visible list? NO              │ MASKED ●●●-●●-6789
SECURITYADMIN    │ IN visible list? NO              │ MASKED ●●●-●●-6789
HR_ROLE          │ IN visible list? NO              │ MASKED ●●●-●●-6789
PUBLIC           │ IN visible list? NO              │ MASKED ●●●-●●-6789
```

### Query: "mask ssn" (default)

```
Role             │ SQL Condition                    │ Result
─────────────────┼──────────────────────────────────┼────────────────
ANALYST_ROLE     │ IN admin list? NO               │ MASKED ●●●-●●-6789
ACCOUNTADMIN     │ IN admin list? YES              │ UNMASKED 123-45-6789
SYSADMIN         │ IN admin list? YES              │ UNMASKED 123-45-6789
SECURITYADMIN    │ IN admin list? YES              │ UNMASKED 123-45-6789
HR_ROLE          │ IN admin list? NO               │ MASKED ●●●-●●-6789
PUBLIC           │ IN admin list? NO               │ MASKED ●●●-●●-6789
```

## Method Call Hierarchy

```
User Query: "mask ssn for analyst roles"
    │
    ├─ _extract_explicit_table_name()
    │  └─ Returns: "CUSTOMERS" or empty string
    │
    ├─ _extract_entities()
    │  └─ Returns: ["CUSTOMERS", "EMAIL", "SSN"]
    │
    ├─ _extract_role_directive()  ◄─── CALLS NEW METHODS
    │  │
    │  ├─ _get_available_snowflake_roles()
    │  │  │ Executes: SHOW ROLES
    │  │  └─ Returns: ['ACCOUNTADMIN', 'ANALYST_ROLE', 'HR_ROLE', 'SYSADMIN', ...]
    │  │
    │  ├─ _get_admin_roles()
    │  │  │ Gets available roles
    │  │  │ Filters for keywords: 'admin', 'sysadmin', 'security', 'steward'
    │  │  └─ Returns: ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN']
    │  │
    │  └─ Returns: {
    │      'role': 'ANALYST_ROLE',
    │      'visible_for_roles': ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN'],
    │      'masked_for_roles': ['ANALYST_ROLE']
    │     }
    │
    └─ _generate_masking_sql()
       │ Uses visible_for_roles and masked_for_roles
       └─ Returns: CASE WHEN CURRENT_ROLE() IN (...)
```

## Data Flow: Old vs New

### Old System (❌ Broken)

```
User Query
    │
    ▼
_extract_role_directive()
    │
    ├─ Hardcoded: visible_for_roles = ['ADMIN', 'DATA_STEWARD']
    │                                  ▲                    ▲
    │                                  │                    │
    │                          DOESN'T EXIST!      DOESN'T EXIST!
    │
    ▼
_generate_masking_sql()
    │
    ├─ CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD')
    │                                 ▲               ▲
    │                       ERROR!    ERROR!
    │
    ▼
SQL Execution FAILS ❌
```

### New System (✅ Works)

```
User Query
    │
    ▼
_extract_role_directive()
    │
    ├─ Call: _get_admin_roles()
    │   ├─ Call: _get_available_snowflake_roles()
    │   │   └─ SHOW ROLES → ['ACCOUNTADMIN', 'ANALYST_ROLE', 'SYSADMIN', 'SECURITYADMIN', ...]
    │   │
    │   └─ Filter for admin keywords
    │       └─ ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN']
    │
    ├─ visible_for_roles = ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN']
    │                        ▲                 ▲                ▲
    │                     REAL ROLE      REAL ROLE        REAL ROLE
    │
    ▼
_generate_masking_sql()
    │
    ├─ CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN')
    │                                 ▲                    ▲             ▲
    │                             ✅ Works             ✅ Works      ✅ Works
    │
    ▼
SQL Execution SUCCEEDS ✅
```

## Role Auto-Detection Logic

```
_get_admin_roles()
    │
    ├─ Get all available roles
    │  └─ SHOW ROLES in Snowflake
    │
    ├─ Filter by keywords
    │  ├─ 'admin'      → Matches ACCOUNTADMIN ✅
    │  ├─ 'sysadmin'   → Matches SYSADMIN ✅
    │  ├─ 'security'   → Matches SECURITYADMIN ✅
    │  ├─ 'steward'    → Matches any *_STEWARD roles
    │  └─ ...
    │
    └─ Return matched roles
       └─ ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN']
```

## Masking Policy SQL Generation

### Step 1: Extract Information

```
Query: "mask ssn for analyst roles in CUSTOMERS table"
         │              │              │
         │              │              └─ Table: CUSTOMERS
         │              └─ Role: ANALYST_ROLE
         └─ Action: mask
```

### Step 2: Get System Information

```
Available Roles:
  ├─ ACCOUNTADMIN
  ├─ ANALYST_ROLE
  ├─ HR_ROLE
  ├─ SYSADMIN
  ├─ SECURITYADMIN
  └─ ...

Admin Roles (Auto-detected):
  ├─ ACCOUNTADMIN  ◄─ keyword: admin
  ├─ SYSADMIN      ◄─ keyword: sysadmin
  └─ SECURITYADMIN ◄─ keyword: security
```

### Step 3: Build Masking Policy

```
For: ANALYST_ROLE
Pattern: "for" (normal masking)

visible_for_roles (see unmasked):
  ├─ ACCOUNTADMIN
  ├─ SYSADMIN
  └─ SECURITYADMIN

masked_for_roles (see masked):
  └─ ANALYST_ROLE
```

### Step 4: Generate SQL

```sql
CREATE OR REPLACE MASKING POLICY ssn_mask_analyst AS (val STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN')
       THEN val
       ELSE CONCAT('***-**-', RIGHT(val, 4))
  END;

ALTER TABLE CUSTOMERS
  MODIFY COLUMN SSN SET MASKING POLICY ssn_mask_analyst;
```

## Testing the Flow

```
Initialize Control Plane
    │
    ├─ Check: _get_available_snowflake_roles()
    │  └─ ✅ Returns ['ACCOUNTADMIN', 'ANALYST_ROLE', 'HR_ROLE', ...]
    │
    ├─ Check: _get_admin_roles()
    │  └─ ✅ Returns ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN']
    │
    ├─ Check: _extract_role_directive()
    │  └─ ✅ Returns dict with actual role names
    │
    ├─ Check: _generate_masking_sql()
    │  └─ ✅ Generates SQL with actual role names
    │
    └─ ✅ ALL TESTS PASS - System ready to use
```

## Code Location in ai_control_plane.py

```
class AIControlPlane:
    │
    ├─ _get_available_snowflake_roles()  ◄─── NEW METHOD (Lines ~1800-1820)
    │  └─ Fetches roles from Snowflake
    │
    ├─ _get_admin_roles()  ◄─── NEW METHOD (Lines ~1822-1840)
    │  └─ Detects admin/privileged roles
    │
    ├─ _extract_role_directive()  ◄─── UPDATED METHOD (Lines ~1842-1900)
    │  └─ Now uses actual admin roles
    │
    ├─ _generate_masking_sql()  ◄─── Uses role_directive parameter
    │  └─ Generates SQL with real role names
    │
    └─ ... other methods
```
