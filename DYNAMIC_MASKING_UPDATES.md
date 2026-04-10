# Dynamic Masking Updates - Column-Specific & Role-Based Support

## Problem Addressed

When executing query: `"mask salary in employee table for analyst role"`

- **Old behavior**: Masked ALL PII columns in the table
- **New behavior**: Only masks the SALARY column with role-specific rules

## Key Changes

### 1. **Dynamic Column Detection**

Added `_extract_target_columns()` method that identifies specific columns mentioned in user queries:

- **Common columns tracked**: salary, wage, income, ssn, email, phone, address, name, etc.
- **Intelligent matching**: Detects exact column names in natural language queries
- **Logging**: Shows detected columns at OBSERVE phase

Example:

```
Query: "mask salary in employee table"
✓ Specific columns detected: ['salary']
```

### 2. **Role-Based Masking Detection**

Added `_extract_target_roles()` method that identifies roles in queries:

- **Common roles tracked**: admin, analyst, manager, employee, viewer, auditor, data_engineer
- **Pattern matching**: Finds "for analyst role", "for admin", etc.
- **Supports different masking per role**

Example:

```
Query: "mask salary in employee table for analyst role"
✓ Target roles detected: ['analyst']
```

### 3. **Enhanced Intent Extraction**

Modified `_extract_intent()` to return dict with:

```python
{
    'type': 'MASK',                    # Original intent
    'target_columns': ['salary'],      # NEW: Specific columns
    'target_roles': ['analyst'],       # NEW: Specific roles
    'is_column_specific': True,        # NEW: Flag
    'is_role_based': True              # NEW: Flag
}
```

### 4. **Column-Specific Analysis**

Updated `_phase_analyze()` to:

- **Check intent_info** from OBSERVE phase
- **Skip non-target columns** when user specified columns
- **Only analyze specified columns** instead of full PII scan
- **Faster execution** for targeted queries

Before:

```
🧠 ANALYZE: Scanning 50 columns for PII...
```

After:

```
📊 Analysis Mode: COLUMN-SPECIFIC
   Target columns: ['salary']
   PII detected in EMPLOYEES.SALARY: Final: 0.95
```

### 5. **Role-Based SQL Generation**

Added `_generate_role_based_masking_sql()` method:

- **Different masking per role**:
  - **ADMIN**: Sees unmasked data
  - **ANALYST**: Sees rounded values (SALARY → rounded to nearest 1000)
  - **Others**: Sees masked values
- **Dynamic SQL generation**:

```sql
CREATE MASKING POLICY EMPLOYEES_SALARY_MASK_POLICY AS
  (val STRING) RETURNS STRING -> CASE
    WHEN CURRENT_ROLE() IN ('ADMIN') THEN val
    WHEN CURRENT_ROLE() IN ('ANALYST') THEN ROUND(val / 1000) * 1000
    ELSE '***SALARY_MASKED***'
  END;
```

### 6. **SALARY-Specific Masking**

Added dedicated handling for salary columns:

- **Detection**: 95% confidence for columns with 'salary', 'wage', 'income'
- **Masking function**: `'***SALARY_MASKED***'` (clear PII indicator)
- **Role masking**: Can show rounded values to analysts instead of full mask

## Execution Flow Example

### Query: `"mask salary in employee table for analyst role"`

1. **OBSERVE Phase**:

   ```
   ✓ Intent: MASK
   ✓ Target columns: ['salary']
   ✓ Target roles: ['analyst']
   ✓ Confidence: 0.95
   ✓ Target entities: ['employees']
   ```

2. **ANALYZE Phase**:

   ```
   📊 Analysis Mode: COLUMN-SPECIFIC
      Target columns: ['salary']
   PII detected in EMPLOYEES.SALARY: Heuristic: 0.95, ML: 0.90, Final: 0.95
   ```

   _Note: Other PII columns are SKIPPED_

3. **PLAN Phase**:

   ```
   ✓ Generating role-based masking for EMPLOYEES.SALARY: roles ['analyst']
   ✓ Generated 4 SQL commands
   ```

4. **Generated SQL**:

   ```sql
   CREATE MASKING POLICY EMPLOYEES_SALARY_MASK_POLICY AS
     (val STRING) RETURNS STRING -> CASE
       WHEN CURRENT_ROLE() IN ('ADMIN') THEN val
       WHEN CURRENT_ROLE() IN ('ANALYST') THEN ROUND(val / 1000) * 1000
       ELSE '***SALARY_MASKED***'
     END;

   ALTER TABLE EMPLOYEES MODIFY COLUMN SALARY
     SET MASKING POLICY EMPLOYEES_SALARY_MASK_POLICY;
   ```

## Backward Compatibility

✓ **Fully backward compatible**:

- Queries WITHOUT specific columns → Full PII scan (original behavior)
- Queries WITHOUT specific roles → Standard masking (mask all non-admin)
- Queries with columns/roles → NEW dynamic behavior

### Example: `"automatically discover and mask all PII"`

- **Result**: Full scan, all PII columns masked (original behavior)

## Benefits

| Feature              | Before                 | After                |
| -------------------- | ---------------------- | -------------------- |
| **Column targeting** | ❌ All columns         | ✅ Only specified    |
| **Role support**     | ❌ None                | ✅ Full support      |
| **Analyst access**   | ❌ Fully masked        | ✅ Rounded/partial   |
| **Performance**      | ❌ Scan all            | ✅ Scan only targets |
| **Control**          | ❌ Binary mask/no-mask | ✅ Granular rules    |

## Usage Examples

### 1. Mask only salary for analysts (NEW)

```
"mask salary in employee table for analyst role"
```

### 2. Mask salary and phone (NEW)

```
"mask salary and phone in employee table"
```

### 3. Mask salary for specific roles (NEW)

```
"protect salary for analyst and manager roles"
```

### 4. Auto-discover all PII (Original - still works)

```
"automatically discover and mask all pii"
```

### 5. Mask email only (NEW)

```
"mask email addresses in customers"
```

## Code Location

File: `src/atlan_ai_control_plane.py`

### Modified Methods:

- `_extract_intent()` - Now returns dict with column/role info
- `_extract_target_columns()` - NEW
- `_extract_target_roles()` - NEW
- `_phase_observe()` - Attaches intent_info to result
- `_phase_analyze()` - Uses intent_info for selective analysis
- `_phase_plan()` - Uses intent_info for role-based SQL
- `_generate_masking_sql()` - Enhanced with SALARY support
- `_generate_role_based_masking_sql()` - NEW

## Testing Recommendations

1. **Test column targeting**:

   ```bash
   python atlan_ai_control_plane.py --query "mask salary in employee table"
   ```

2. **Test role-based masking**:

   ```bash
   python atlan_ai_control_plane.py --query "mask salary for analyst role"
   ```

3. **Test combined**:

   ```bash
   python atlan_ai_control_plane.py --query "mask salary and email for analyst and manager"
   ```

4. **Test backward compatibility**:
   ```bash
   python atlan_ai_control_plane.py --query "automatically discover and mask pii"
   ```
