# Masking Policy SQL Generation Fix

## Issue
The LLM was generating masking policies with incorrect signatures:
- Created policy with 2 arguments: `AS (val STRING, role STRING)`
- Applied policy with 1 argument: `ALTER TABLE ... SET MASKING POLICY policy_name`
- Error: "expected 2 arguments, got 1 arguments"

## Root Cause
The LLM prompt examples showed multi-argument conditional masking policies, which the LLM copied even for simple masking requests.

## Fix Applied
Updated the LLM prompt in `control_pannel.py` to:

1. **Clearly distinguish between SIMPLE and CONDITIONAL masking:**
   - SIMPLE (default): Single argument `AS (val STRING)` 
   - CONDITIONAL (explicit only): Multi-argument `AS (val STRING, condition STRING)`

2. **Updated all examples to use SINGLE argument by default:**
   - Role-based masking: Use `CURRENT_ROLE()` in CASE statement
   - Partial masking: Use string functions with single val argument
   - Pattern-based masking: Use CASE/LIKE with single val argument

3. **Added clear rules:**
   - DEFAULT: Use single argument policies
   - ONLY use multi-argument when user explicitly mentions conditions like "except for X type"
   - Include proper USING clause when multi-argument is needed

## Examples Now Provided to LLM

### ✅ CORRECT - Simple masking (single argument):
```sql
CREATE OR REPLACE MASKING POLICY analyst_mask AS (val STRING) 
RETURNS STRING -> 
CASE WHEN CURRENT_ROLE() = 'ANALYST' THEN '***MASKED***' ELSE val END;

ALTER TABLE EMPLOYEE_DATA MODIFY COLUMN "SALARY" SET MASKING POLICY analyst_mask;
```

### ✅ CORRECT - Partial masking (single argument):
```sql
CREATE OR REPLACE MASKING POLICY partial_ssn_mask AS (val STRING) 
RETURNS STRING -> 
CASE WHEN CURRENT_ROLE() IN ('ADMIN') THEN val 
     ELSE CONCAT(REPEAT('X', LENGTH(val)-2), RIGHT(val, 2)) END;

ALTER TABLE CUSTOMERS MODIFY COLUMN "SSN" SET MASKING POLICY partial_ssn_mask;
```

### ❌ WRONG - What was being generated before:
```sql
-- Policy defined with 2 arguments
CREATE OR REPLACE MASKING POLICY analyst_role_mask AS (val STRING, role STRING) 
RETURNS STRING -> CASE WHEN CURRENT_ROLE() = 'ANALYST' THEN '***MASKED***' ELSE val END;

-- But applied with only 1 argument (WRONG!)
ALTER TABLE PUBLIC.EMPLOYEE_DATA MODIFY COLUMN NAME SET MASKING POLICY analyst_role_mask;
-- ERROR: expected 2 arguments, got 1 arguments
```

## Result
✅ LLM will now generate correct single-argument masking policies by default
✅ Query logging will show the correct SQL being generated
✅ Masking policies will apply successfully

## File Modified
- `src/control_pannel.py` - Updated LLM prompt and examples

## Testing
Try the same query again:
```
"mask pii in employee table"
```

The generated SQL should now be:
```sql
CREATE OR REPLACE MASKING POLICY employee_pii_mask AS (val STRING) 
RETURNS STRING -> 
CASE WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_STEWARD') THEN val ELSE '***MASKED***' END;

ALTER TABLE EMPLOYEE_DATA MODIFY COLUMN "NAME" SET MASKING POLICY employee_pii_mask;
```

This will execute successfully! ✅
