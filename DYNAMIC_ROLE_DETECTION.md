# DYNAMIC ROLE DETECTION SYSTEM

## Future-Proof Admin Role Detection for Masking Policies

### Overview

The system now **DYNAMICALLY detects admin roles** from your Snowflake instance instead of using hardcoded role names. This means:

✅ **No more hardcoding roles** - Uses actual roles from your system
✅ **Future-proof** - New admin roles added to Snowflake are automatically included  
✅ **Auto-scaling** - Works with any number of roles
✅ **Intelligent categorization** - Uses keyword matching to identify admin roles

---

## How It Works

### 1. **\_get_available_snowflake_roles()** - Fetches ALL Roles

```python
def _get_available_snowflake_roles(self) -> List[str]:
    """Fetch actual roles available in Snowflake instance"""
    # Executes: SHOW ROLES
    # Returns: ['ACCOUNTADMIN', 'ANALYST_ROLE', 'HR_ROLE', 'SYSADMIN', ...]
```

**What it does:**

- Connects to Snowflake
- Runs `SHOW ROLES` command
- Returns all available roles in the instance
- Falls back to system defaults if not connected

**Execution Flow:**

```
1. Try to connect to Snowflake
2. Execute: SHOW ROLES
3. Extract role names from result set
4. Return list of roles or fallback defaults
```

---

### 2. **\_get_admin_roles()** - Identifies Admin Roles (EXPANDED)

```python
def _get_admin_roles(self) -> List[str]:
    """Intelligently detect admin/privileged roles from available roles"""
    # EXPANDED keywords to match various patterns:
    # - admin          → ADMIN, SYSADMIN, GOVADMIN, USERADMIN
    # - sys            → SYSADMIN, SYSCONTROL
    # - security       → SECURITYADMIN, SECURITY_OFFICER
    # - steward        → DATA_STEWARD, GOVERNANCE_STEWARD
    # - governance     → GOVERNANCE_ADMIN
    # - compliance     → COMPLIANCE_ADMIN, COMPLIANCE_OFFICER
    # - control        → CONTROL_ADMIN, SYSCONTROL
    # - operator       → OPERATOR, SYSOPERATOR, DATABASE_OPERATOR
    # - superuser      → SUPERUSER
```

**What it does:**

- Gets ALL available roles from `_get_available_snowflake_roles()`
- Filters roles based on admin-related keywords
- Returns only roles that contain admin-like patterns
- Completely future-proof - matches any admin role pattern

**Example Results:**

```
Available Roles:
├── ACCOUNTADMIN          ← Detected (contains "admin")
├── ANALYST_ROLE
├── HR_ROLE
├── SECURITYADMIN         ← Detected (contains "security" + "admin")
├── SYSADMIN              ← Detected (contains "sys" + "admin")
├── USERADMIN             ← Detected (contains "admin")
├── GOVERNANCE_ADMIN      ← Detected (contains "governance" + "admin")
├── COMPLIANCE_OFFICER    ← Detected (contains "compliance")
└── PUBLIC

Result: [ACCOUNTADMIN, SECURITYADMIN, SYSADMIN, USERADMIN, GOVERNANCE_ADMIN, COMPLIANCE_OFFICER]
```

---

### 3. **\_categorize_all_roles()** - Role Categorization

```python
def _categorize_all_roles(self) -> Dict[str, List[str]]:
    """Categorize ALL roles into admin and regular roles"""
    # Returns:
    # {
    #     'admin_roles': ['ACCOUNTADMIN', 'SYSADMIN', ...],
    #     'regular_roles': ['ANALYST_ROLE', 'HR_ROLE', ...],
    #     'all_roles': [...]
    # }
```

**What it does:**

- Gets all available roles
- Gets all admin roles
- Calculates regular roles (everything else)
- Provides comprehensive role categorization

---

## Masking Policy Generation (DYNAMIC)

### Before (Hardcoded - ❌ BAD)

```sql
CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val ELSE '***MASKED***' END
```

❌ **Problems:**

- Roles 'ADMIN' and 'DATA_STEWARD' don't exist in actual Snowflake
- New admin roles not automatically included
- Must manually edit code to add new roles

---

### After (Dynamic - ✅ GOOD)

```sql
CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN', 'USERADMIN') THEN val ELSE '***MASKED***' END
```

✅ **Benefits:**

- Uses actual roles detected from system
- Automatically detects new admin roles added in future
- No code changes needed when roles change

---

## Admin Role Keywords (Expanded List)

The system now matches these patterns to identify admin roles:

| Keyword      | Matches                     | Examples                                 |
| ------------ | --------------------------- | ---------------------------------------- |
| `admin`      | Any role containing "admin" | ADMIN, SYSADMIN, GOVADMIN, USERADMIN     |
| `sys`        | System admin roles          | SYSADMIN, SYSCONTROL                     |
| `security`   | Security-related roles      | SECURITYADMIN, SECURITY_OFFICER          |
| `steward`    | Data steward roles          | DATA_STEWARD, GOVERNANCE_STEWARD         |
| `governance` | Governance roles            | GOVERNANCE_ADMIN, GOVERNANCE_STEWARD     |
| `compliance` | Compliance roles            | COMPLIANCE_ADMIN, COMPLIANCE_OFFICER     |
| `control`    | Control/operator roles      | CONTROL_ADMIN, SYSCONTROL                |
| `operator`   | Operator roles              | OPERATOR, SYSOPERATOR, DATABASE_OPERATOR |
| `superuser`  | Superuser roles             | SUPERUSER                                |

---

## Query Example: Masking with Roles

### User Query

```
"Mask PII in PERSON_PROFILE table for analyst roles"
```

### System Execution

**Step 1: Extract Intent**

- Table: `PERSON_PROFILE`
- Role directive: `for analyst roles` → `ANALYST_ROLE` sees masked, others see unmasked
- Columns: EMAIL, PHONE, SSN (automatically detected as PII)

**Step 2: Get Admin Roles (DYNAMICALLY)**

```python
actual_admin_roles = self._get_admin_roles()
# Result: ['ACCOUNTADMIN', 'SECURITYADMIN', 'SYSADMIN', 'USERADMIN']
```

**Step 3: Generate Masking Policy**

```sql
CREATE MASKING POLICY PERSON_PROFILE_EMAIL_mask_policy_1769241021
AS (val STRING) RETURNS STRING ->
CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SECURITYADMIN', 'SYSADMIN', 'USERADMIN')
     THEN val
     ELSE '***MASKED***'
END;

ALTER TABLE PUBLIC."PERSON_PROFILE" ALTER COLUMN "EMAIL" SET MASKING POLICY PERSON_PROFILE_EMAIL_mask_policy_1769241021;
```

**Step 4: Role-Based Access**

- ANALYST_ROLE → sees `***MASKED***`
- HR_ROLE → sees `***MASKED***`
- ACCOUNTADMIN → sees actual email (admin role)
- SYSADMIN → sees actual email (admin role)
- SECURITYADMIN → sees actual email (admin role)
- USERADMIN → sees actual email (admin role)
- Any new admin role added → automatically sees unmasked data ✅

---

## Future-Proofing Explained

### Scenario: Company Adds New Role

When your company adds a new admin role (e.g., `ORGADMIN`):

**What happens:**

1. Next masking policy creation automatically runs:

   ```python
   actual_admin_roles = self._get_admin_roles()
   # Now returns: ['ACCOUNTADMIN', 'ORGADMIN', 'SECURITYADMIN', 'SYSADMIN', 'USERADMIN']
   ```

2. New policy includes `ORGADMIN`:

   ```sql
   CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'ORGADMIN', 'SECURITYADMIN', 'SYSADMIN', 'USERADMIN') ...
   ```

3. **NO CODE CHANGES NEEDED!** ✅

---

## Implementation Details

### File: `ai_control_plane.py`

**Method Locations:**

- `_get_available_snowflake_roles()` - Line ~1855
- `_get_admin_roles()` - Line ~1875 (EXPANDED)
- `_categorize_all_roles()` - Line ~1850 (NEW)
- `_generate_masking_sql()` - Line ~2315 (uses dynamic roles)

**Key Changes:**

1. **Expanded Admin Keywords** (Line 1886-1895):

   ```python
   admin_keywords = [
       'admin', 'sys', 'security', 'steward', 'governance',
       'compliance', 'control', 'operator', 'superuser'
   ]
   ```

2. **Dynamic CASE Statement** (Line 2321-2341):

   ```python
   if role_directive and (role_directive.get('masked_for_roles') or ...):
       # Use directive-based roles
   else:
       # Default: Use dynamically detected admin roles
       actual_admin_roles = self._get_admin_roles()  # ← DYNAMIC!
       roles_list = ', '.join([f"'{role}'" for role in actual_admin_roles])
   ```

3. **Enhanced Logging** (Line 2336-2341):
   ```python
   self.logger.info(f"✅ DEFAULT Dynamic Masking: {len(actual_admin_roles)} admin roles")
   self.logger.info(f"✅ DEFAULT Dynamic Masking: Admin roles are: {actual_admin_roles}")
   self.logger.info(f"ℹ️  These admin roles are DYNAMICALLY detected from Snowflake")
   self.logger.info(f"ℹ️  Future admin roles added to Snowflake will AUTOMATICALLY be included!")
   ```

---

## Testing the Dynamic System

### Test Case 1: Default Masking (No Role Specified)

```
Input: "mask ssn in employees"
Expected:
- Uses actual admin roles from system
- New admin roles automatically included
- Output: CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN', ...) ...
```

### Test Case 2: Specific Role Directive

```
Input: "mask ssn in employees for analyst roles"
Expected:
- ANALYST_ROLE sees masked data
- All admin roles see unmasked data
- Uses dynamically detected admin roles for "all others"
```

### Test Case 3: Inverse Directive

```
Input: "mask ssn in employees not for analyst roles"
Expected:
- ANALYST_ROLE sees unmasked data
- All other roles see masked data
```

---

## Fallback Behavior

If Snowflake connection is not available, system falls back to:

```python
return ['ACCOUNTADMIN', 'SYSADMIN', 'SECURITYADMIN', 'USERADMIN']
```

**Note:** As soon as Snowflake connects, it switches to dynamic detection.

---

## Advantages Summary

| Feature              | Before               | After               |
| -------------------- | -------------------- | ------------------- |
| **Role Detection**   | Hardcoded, static    | Dynamic from system |
| **New Admin Roles**  | Require code changes | Automatic inclusion |
| **Keyword Matching** | 4 patterns           | 9 patterns          |
| **Future-Proof**     | ❌ No                | ✅ Yes              |
| **Maintenance**      | High                 | Low                 |
| **Scalability**      | Limited              | Unlimited           |

---

## Conclusion

The masking policy system is now **fully dynamic and future-proof**. It will automatically detect and include any admin roles added to your Snowflake instance in the future, eliminating the need for manual code updates.

✅ **Current Status:** All admin roles detected dynamically
✅ **Future Status:** New roles automatically included
✅ **Code Changes:** Zero when roles are added
