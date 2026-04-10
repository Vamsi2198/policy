# Fix Summary: Rows Affected and Columns Affected Display

## Problem
The web UI was showing:
- **Rows Affected: 0** ❌
- **Columns Affected: 0** ❌

Even though the workflow was working correctly and data was being masked/unmasked.

## Root Cause

In `ai_control_plane.py`, the `_phase_simulate()` method was calculating affected rows incorrectly:

```python
# OLD CODE (WRONG):
affected_rows = plan_result.estimated_impact.get('estimated_rows', 0)
# This was always 0 because estimated_impact wasn't properly populated
```

The method wasn't using the actual **PII findings** from the ANALYZE phase to count:
1. How many columns have PII
2. How many rows are in those tables

## Fix Applied

### 1. Pass `analyze_result` to `_phase_simulate()`

**File:** `ai_control_plane.py` line ~594
```python
# OLD:
simulate_result = self._phase_simulate(plan_result, observe_result)

# NEW:
simulate_result = self._phase_simulate(plan_result, observe_result, analyze_result)
```

### 2. Updated `_phase_simulate()` Method

**File:** `ai_control_plane.py` line ~1100

**Changes:**
- Added `analyze_result` parameter
- Uses `analyze_result.pii_findings` to count affected columns
- Sums row counts from schema_context for affected tables
- Returns **actual counts** instead of 0

**New Logic:**
```python
def _phase_simulate(self, plan_result, observe_result, analyze_result=None):
    affected_columns_list = []
    total_rows_in_affected_tables = 0
    
    if analyze_result and analyze_result.pii_findings:
        # Get unique tables from PII findings
        affected_tables = set()
        for finding in analyze_result.pii_findings:
            table = finding['table']
            column = finding['column']
            affected_tables.add(table)
            affected_columns_list.append(f"{table}.{column}")
        
        # Get row counts from affected tables
        for table_name in affected_tables:
            if table_name in observe_result.schema_context:
                row_count = observe_result.schema_context[table_name].get('row_count', 0)
                total_rows_in_affected_tables += row_count
    
    return SimulationResult(
        affected_rows=total_rows_in_affected_tables,  # Real count!
        affected_columns=affected_columns_list,       # Real columns!
        ...
    )
```

## What Now Shows Correctly

For the CUSTOMERS table with 3 rows and 5 PII columns:

**Before Fix:**
```
Rows Affected: 0        ❌
Columns Affected: 0     ❌
```

**After Fix:**
```
Rows Affected: 3        ✅ (total rows in CUSTOMERS table)
Columns Affected: 5     ✅ (SSN, EMAIL, PHONE, FULL_NAME, ADDRESS)
```

## Why DDL Commands Still Show "0 rows affected" in Logs

This is **separate** and **CORRECT**:
- DDL commands (CREATE/ALTER/DROP) don't modify data rows
- They modify metadata (policies, schemas)
- So `cursor.rowcount = 0` is expected
- The **display counts** show table-level impact, not execution rowcount

## How to Verify

1. **Start the server:**
   ```powershell
   cd c:\Users\mula.krishna\Documents\policy2\src
   python atlan_api_server.py
   ```

2. **Open web UI:**
   ```
   http://localhost:5000
   ```

3. **Type a masking command:**
   ```
   "mask pii in customers table"
   ```

4. **Check the "Awaiting Your Approval" section:**
   - Should show: **Rows Affected: 3**
   - Should show: **Columns Affected: 5** (or however many PII columns detected)

## Files Modified

1. **`ai_control_plane.py`** (2 changes)
   - Line ~594: Pass `analyze_result` to `_phase_simulate()`
   - Line ~1100: Updated `_phase_simulate()` to use PII findings for counts

## Test It Now

Run this command and check the web UI:
```powershell
python atlan_api_server.py
```

Then navigate to http://localhost:5000 and try:
- "mask pii in customers"
- "unmask customers data"

Both should now show **correct counts** in the approval dialog! ✅
