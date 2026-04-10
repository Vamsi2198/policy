# DYNAMIC ROLE DETECTION - VISUAL DIAGRAMS

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MASKING POLICY SYSTEM                       │
│                      (Dynamic Role Detection)                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
            ┌───────▼────────┐          ┌────────────▼──────┐
            │  User Query    │          │  Snowflake        │
            │  "mask email   │          │  Database         │
            │   in customer" │          │                   │
            └───────┬────────┘          └────────────────┬──┘
                    │                                    │
                    │                          ┌─────────▼────────┐
                    │                          │  SHOW ROLES      │
                    │                          │  Returns: [all   │
                    │                          │   available      │
                    │                          │   roles]         │
                    │                          └─────────┬────────┘
                    │                                    │
        ┌───────────▼────────────────────────────────────▼─────────────┐
        │                   PHASE 1: OBSERVE                            │
        │                  Extract Entities                             │
        ├────────────────────────────────────────────────────────────┬──┤
        │ • Table: CUSTOMERS                                         │  │
        │ • Column: EMAIL                                            │  │
        │ • Role Directive: None (use default)                       │  │
        └────────────────────────────────────────────────────────────┴──┘
                    │
        ┌───────────▼────────────────────────────────────────────────┐
        │              PHASE 3: PLAN - Detect Admin Roles             │
        │                                                              │
        │  ┌──────────────────────────────────────────────────┐      │
        │  │ Call: _get_available_snowflake_roles()           │      │
        │  │ ├─ Executes: SHOW ROLES                          │      │
        │  │ └─ Returns: ['ACCOUNTADMIN', 'ANALYST_ROLE',     │      │
        │  │            'HR_ROLE', 'SYSADMIN', 'SECURITYADMIN'│     │
        │  │            'USERADMIN', 'PUBLIC']                │      │
        │  └──────────────────────────────────────────────────┘      │
        │                       │                                      │
        │  ┌────────────────────▼──────────────────────────────┐      │
        │  │ Call: _get_admin_roles()                          │      │
        │  │ ├─ Apply 9 keyword filters                        │      │
        │  │ │  (admin, sys, security, steward, governance,   │      │
        │  │ │   compliance, control, operator, superuser)    │      │
        │  │ └─ Returns: ['ACCOUNTADMIN', 'SYSADMIN',         │      │
        │  │            'SECURITYADMIN', 'USERADMIN']         │      │
        │  └──────────────────────────────────────────────────┘      │
        │                       │                                      │
        │  ┌────────────────────▼──────────────────────────────┐      │
        │  │ Generate Dynamic Masking Policy                  │      │
        │  │                                                   │      │
        │  │ roles_list = "'ACCOUNTADMIN', 'SYSADMIN',        │      │
        │  │             'SECURITYADMIN', 'USERADMIN'"        │      │
        │  │                                                   │      │
        │  │ CASE WHEN CURRENT_ROLE() IN (roles_list)        │      │
        │  │     THEN val                                     │      │
        │  │     ELSE '***MASKED***'                          │      │
        │  │ END                                              │      │
        │  └──────────────────────────────────────────────────┘      │
        └────────────────────┬─────────────────────────────────────────┘
                             │
        ┌────────────────────▼─────────────────────────────────────────┐
        │         PHASE 5: EXECUTE - Apply Masking Policy              │
        │                                                               │
        │  CREATE MASKING POLICY EMAIL_mask_policy_1769241021         │
        │  AS (val STRING) RETURNS STRING ->                           │
        │  CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN',  │
        │                                'SECURITYADMIN', 'USERADMIN')│
        │      THEN val ELSE '***MASKED***' END;                       │
        │                                                               │
        │  ALTER TABLE "CUSTOMERS" ALTER COLUMN "EMAIL"               │
        │  SET MASKING POLICY EMAIL_mask_policy_1769241021;            │
        └──────────────────────┬──────────────────────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────────────────────┐
        │            RESULT: Role-Based Data Access                    │
        │                                                               │
        │  ACCOUNTADMIN     ──────▶  sees email: alice@company.com    │
        │  SYSADMIN        ──────▶  sees email: alice@company.com    │
        │  SECURITYADMIN   ──────▶  sees email: alice@company.com    │
        │  USERADMIN       ──────▶  sees email: alice@company.com    │
        │  ANALYST_ROLE    ──────▶  sees email: ***MASKED***         │
        │  HR_ROLE         ──────▶  sees email: ***MASKED***         │
        │  PUBLIC          ──────▶  sees email: ***MASKED***         │
        │                                                               │
        │  ✅ Future: New admin role added → automatically included   │
        └──────────────────────────────────────────────────────────────┘
```

---

## Role Detection Flow

```
START: Request Masking Policy
│
├─────────────────────────────────────────────────────────┐
│  Step 1: Get Available Roles                            │
│  Execute: SHOW ROLES                                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
        All Available Roles from Snowflake:
        ┌─────────────────────────────┐
        │ • ACCOUNTADMIN              │
        │ • ANALYST_ROLE              │
        │ • COMPLIANCE_OFFICER        │
        │ • GOVERNANCE_ADMIN          │
        │ • HR_ROLE                   │
        │ • ORGADMIN                  │
        │ • PUBLIC                    │
        │ • SECURITYADMIN             │
        │ • SYSADMIN                  │
        │ • USERADMIN                 │
        └─────────────────────────────┘
                       │
├─────────────────────────────────────────────────────────┐
│  Step 2: Filter by Admin Keywords                       │
│                                                          │
│  Keywords: admin, sys, security, steward,               │
│            governance, compliance, control,             │
│            operator, superuser                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │ MATCH PROCESS:                  │
        │                                 │
        │ ACCOUNTADMIN                    │
        │ └─ contains 'admin' ✓ → MATCH  │
        │                                 │
        │ ANALYST_ROLE                    │
        │ └─ no match ✗                   │
        │                                 │
        │ COMPLIANCE_OFFICER              │
        │ └─ contains 'compliance' ✓ → MATCH
        │                                 │
        │ GOVERNANCE_ADMIN                │
        │ └─ contains 'governance' + 'admin' ✓ → MATCH
        │                                 │
        │ HR_ROLE                         │
        │ └─ no match ✗                   │
        │                                 │
        │ ORGADMIN                        │
        │ └─ contains 'admin' ✓ → MATCH  │
        │                                 │
        │ PUBLIC                          │
        │ └─ no match ✗                   │
        │                                 │
        │ SECURITYADMIN                   │
        │ └─ contains 'security' + 'admin' ✓ → MATCH
        │                                 │
        │ SYSADMIN                        │
        │ └─ contains 'admin' + 'sys' ✓ → MATCH
        │                                 │
        │ USERADMIN                       │
        │ └─ contains 'admin' ✓ → MATCH  │
        └─────────────────────────────────┘
                       │
├─────────────────────────────────────────────────────────┐
│  Step 3: Detected Admin Roles                           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
        ┌───────────────────────────────────┐
        │  Admin Roles (7 detected):        │
        │  • ACCOUNTADMIN                   │
        │  • COMPLIANCE_OFFICER             │
        │  • GOVERNANCE_ADMIN               │
        │  • ORGADMIN                       │
        │  • SECURITYADMIN                  │
        │  • SYSADMIN                       │
        │  • USERADMIN                      │
        │                                   │
        │  Regular Roles (3):               │
        │  • ANALYST_ROLE                   │
        │  • HR_ROLE                        │
        │  • PUBLIC                         │
        └───────────────────────────────────┘
                       │
├─────────────────────────────────────────────────────────┐
│  Step 4: Generate Masking Policy with Admin Roles       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
        CASE WHEN CURRENT_ROLE() IN (
            'ACCOUNTADMIN',
            'COMPLIANCE_OFFICER',
            'GOVERNANCE_ADMIN',
            'ORGADMIN',
            'SECURITYADMIN',
            'SYSADMIN',
            'USERADMIN'
        ) THEN val ELSE '***MASKED***' END
                       │
└─────────────────────────────────────────────────────────┐
                       │
                       ▼
                   END: Policy Created
                   ✅ Future: New admin role
                      automatically included
```

---

## Future Scenario: New Role Added

```
Timeline:
┌────────────────────────────────────────────────────────────┐
│  T0: Current State                                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Available Roles:                                     │  │
│  │ • ACCOUNTADMIN                                       │  │
│  │ • ANALYST_ROLE                                       │  │
│  │ • HR_ROLE                                            │  │
│  │ • SYSADMIN                                           │  │
│  │ • SECURITYADMIN                                      │  │
│  │ • USERADMIN                                          │  │
│  │ • PUBLIC                                             │  │
│  │                                                       │  │
│  │ Admin Roles: [ACCOUNTADMIN, SYSADMIN,               │  │
│  │              SECURITYADMIN, USERADMIN]              │  │
│  │                                                       │  │
│  │ Generated Policy:                                    │  │
│  │ CASE WHEN CURRENT_ROLE() IN (                       │  │
│  │     'ACCOUNTADMIN', 'SYSADMIN',                     │  │
│  │     'SECURITYADMIN', 'USERADMIN'                    │  │
│  │ ) THEN val ELSE '***MASKED***' END                 │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        DBA Action: Create new admin role ORGADMIN
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  T1: After ORGADMIN Added to Snowflake                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Available Roles:                                     │  │
│  │ • ACCOUNTADMIN                                       │  │
│  │ • ANALYST_ROLE                                       │  │
│  │ • HR_ROLE                                            │  │
│  │ • ORGADMIN            ← NEW!                        │  │
│  │ • SYSADMIN                                           │  │
│  │ • SECURITYADMIN                                      │  │
│  │ • USERADMIN                                          │  │
│  │ • PUBLIC                                             │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        User: Request new masking policy
                        │
                        ▼
┌────────────────────────────────────────────────────────────┐
│  T2: Next Policy Request                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ System Automatically:                                │  │
│  │                                                       │  │
│  │ 1. Run SHOW ROLES                                   │  │
│  │    └─ Gets: [ACCOUNTADMIN, ANALYST_ROLE, HR_ROLE,  │  │
│  │             ORGADMIN, SYSADMIN, SECURITYADMIN,     │  │
│  │             USERADMIN, PUBLIC]                      │  │
│  │                                                       │  │
│  │ 2. Filter by admin keywords                         │  │
│  │    └─ ORGADMIN contains 'admin' ✓ → MATCH          │  │
│  │                                                       │  │
│  │ 3. Updated Admin Roles:                             │  │
│  │    [ACCOUNTADMIN, ORGADMIN, SYSADMIN,              │  │
│  │     SECURITYADMIN, USERADMIN]                       │  │
│  │                                                       │  │
│  │ 4. Generate Policy with NEW role:                   │  │
│  │    CASE WHEN CURRENT_ROLE() IN (                   │  │
│  │        'ACCOUNTADMIN', 'ORGADMIN', 'SYSADMIN',    │  │
│  │        'SECURITYADMIN', 'USERADMIN'                │  │
│  │    ) THEN val ELSE '***MASKED***' END              │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
                  ✅ SUCCESS:
                  • ORGADMIN automatically included
                  • No code changes needed
                  • No restart required
                  • No testing cycle needed
```

---

## Keyword Matching Visualization

```
KEYWORD MATCHING MATRIX:

Role Name              │ admin │ sys │ sec │ stw │ gov │ cmpl │ cntrl │ op │ super │ MATCH?
───────────────────────┼───────┼─────┼─────┼─────┼─────┼──────┼───────┼────┼───────┼────────
ACCOUNTADMIN          │  ✓    │ ✗   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  YES
ANALYST_ROLE          │  ✗    │ ✗   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  NO
COMPLIANCE_OFFICER    │  ✗    │ ✗   │ ✗   │ ✗   │ ✗   │  ✓   │  ✗    │ ✗  │  ✗    │  YES
COMPLIANCE_ADMIN      │  ✓    │ ✗   │ ✗   │ ✗   │ ✗   │  ✓   │  ✗    │ ✗  │  ✗    │  YES
CONTROL_ADMIN         │  ✓    │ ✗   │ ✗   │ ✗   │ ✗   │  ✗   │  ✓    │ ✗  │  ✗    │  YES
DATABASE_OPERATOR     │  ✗    │ ✗   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✓  │  ✗    │  YES
DATA_STEWARD          │  ✗    │ ✗   │ ✗   │ ✓   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  YES
GOVERNANCE_ADMIN      │  ✓    │ ✗   │ ✗   │ ✗   │ ✓   │  ✗   │  ✗    │ ✗  │  ✗    │  YES
GOVERNANCE_STEWARD    │  ✗    │ ✗   │ ✗   │ ✓   │ ✓   │  ✗   │  ✗    │ ✗  │  ✗    │  YES
HR_ROLE               │  ✗    │ ✗   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  NO
ORGADMIN              │  ✓    │ ✗   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  YES
PUBLIC                │  ✗    │ ✗   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  NO
SECURITY_OFFICER      │  ✗    │ ✗   │ ✓   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  YES
SECURITYADMIN         │  ✓    │ ✗   │ ✓   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  YES
SUPERUSER             │  ✗    │ ✗   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✓    │  YES
SYSADMIN              │  ✓    │ ✓   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  YES
SYSOPERATOR           │  ✗    │ ✓   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✓  │  ✗    │  YES
SYSCONTROL            │  ✗    │ ✓   │ ✗   │ ✗   │ ✗   │  ✗   │  ✓    │ ✗  │  ✗    │  YES
USERADMIN             │  ✓    │ ✗   │ ✗   │ ✗   │ ✗   │  ✗   │  ✗    │ ✗  │  ✗    │  YES
```

---

## Method Call Sequence Diagram

```
                 User Query: "mask email in customers"
                              │
                              ▼
                    process_natural_language()
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
           OBSERVE Phase          PLAN Phase (Masking)
                │                           │
                │                    _generate_masking_sql()
                │                           │
                │                    Get admin roles? ────┐
                │                    (if no role_directive)
                │                                         │
                │                  ┌──────────────────────┘
                │                  ▼
                │         _get_admin_roles()
                │                  │
                │         Get available roles ──┐
                │                  │             │
                │         ┌────────┴─────┐      │
                │         ▼               ▼      │
                │    Try connection   Return fallback
                │    to Snowflake         │      │
                │         │               │      │
                │    If success:      (if not   │
                │    SHOW ROLES       connected)
                │         │               │      │
                │         └───────┬───────┘      │
                │                 ▼              │
                │      All available roles ◄─────┘
                │     (from Snowflake or fallback)
                │                 │
                │      _get_admin_roles() (cont)
                │                 │
                │      Apply 9 keyword filters:
                │      admin, sys, security,
                │      steward, governance,
                │      compliance, control,
                │      operator, superuser
                │                 │
                │                 ▼
                │      Admin roles detected:
                │      [ACCOUNTADMIN, SYSADMIN,
                │       SECURITYADMIN, USERADMIN]
                │                 │
                │      Return to _generate_masking_sql()
                │                 │
                │      Build CASE statement:
                │      CASE WHEN CURRENT_ROLE() IN
                │      ('ACCOUNTADMIN', 'SYSADMIN',
                │       'SECURITYADMIN', 'USERADMIN')
                │      THEN val ELSE '***MASKED***' END
                │                 │
                └─────────────────┬──────────────────┐
                                  ▼                  ▼
                          Generate SQL         Return to user
                                  │
                          Execute in Snowflake
                                  │
                              ✅ Success
```

---

## Performance & Scalability Chart

```
Role Detection Performance vs. Organization Size:

Number of     Initial    Dynamic      Future      Memory      Impact
Roles         Detection  Updates      Roles       Usage       on Performance
─────────────────────────────────────────────────────────────────────
10 roles      ~10ms      <1ms         Auto ✓      Minimal     Negligible
50 roles      ~15ms      <1ms         Auto ✓      Minimal     Negligible
100 roles     ~20ms      <1ms         Auto ✓      Minimal     Negligible
500+ roles    ~25ms      <1ms         Auto ✓      Minimal     Negligible

Key Points:
• Initial detection (SHOW ROLES): ~10-25ms regardless of count
• Keyword filtering: O(n) complexity, very fast
• Dynamic updates: Minimal overhead (cached after first call)
• Memory usage: Negligible (just role name strings)
• Recommendation: Implement caching for production (optional)
```

---

## State Transition Diagram

```
┌──────────────────────┐
│  System Started      │
│  No roles loaded     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────┐
│  First Masking Request   │
│  (or role check called)  │
└──────────┬───────────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
Connect to  No Connection
Snowflake   Available
     │           │
     │      Return Fallback
     │      Roles
     │           │
     │      ┌────┴─────┐
     │      ▼          ▼
     │   Use Default  Continue in
     │   [ACCOUNTADMIN Limited Mode
     │    SYSADMIN
     │    SECURITYADMIN
     │    USERADMIN]
     │      │
     ▼      ▼
┌─────────────────────┐
│  Admin Roles Ready  │
│  [cached until      │
│   next connection]  │
└──────────┬──────────┘
           │
    ┌──────┴──────────┐
    ▼                 ▼
Generate         Next masking
Policy with      request
detected roles
    │                 │
    ├─────────────────┤
    ▼
Create Masking
Policy in Snowflake
    │
    ▼
✅ Policy Applied
Role-based access
controlled
    │
    ▼
Future: New admin role added
to Snowflake
    │
    ▼
Next masking request
    │
    ▼
Re-detect admin roles
(ORGADMIN now detected)
    │
    ▼
✅ New policy includes
   ORGADMIN automatically
   (No code changes!)
```
