# Data Preview with Role-Based Views - Implementation Summary

## Overview
Implemented before/after data visualization showing how different Snowflake roles (HR_ROLE vs ANALYST_ROLE) see data after masking policies are applied.

## User Request
> "once user approvess and chnges made in snwilke immeditely user need to see data in fornetd with chnges in data for HR_Role and analyst role first 2 rows of data left and right side boxes"

## Changes Made

### Backend Changes

#### 1. New Endpoint: `/api/data-preview/<session_id>` (atlan_api_server.py)
- **Purpose**: Fetch and compare data with different role contexts
- **What it does**:
  - Retrieves table name from session data
  - Uses `USE ROLE` to switch between roles
  - Queries first 2 rows with ACCOUNTADMIN (before - unmasked)
  - Queries first 2 rows with HR_ROLE (after - may show some data)
  - Queries first 2 rows with ANALYST_ROLE (after - masked)
  - Returns JSON with all 3 views plus column names

- **Response structure**:
  ```json
  {
    "table": "CUSTOMERS",
    "columns": ["ID", "NAME", "EMAIL", "SSN"],
    "before": [
      {"ID": 1, "NAME": "John", "EMAIL": "john@email.com", "SSN": "123-45-6789"},
      {"ID": 2, "NAME": "Jane", "EMAIL": "jane@email.com", "SSN": "987-65-4321"}
    ],
    "after_hr": [
      {"ID": 1, "NAME": "John", "EMAIL": "john@email.com", "SSN": "123-45-6789"},
      {"ID": 2, "NAME": "Jane", "EMAIL": "jane@email.com", "SSN": "987-65-4321"}
    ],
    "after_analyst": [
      {"ID": 1, "NAME": "John", "EMAIL": "***MASKED***", "SSN": "***MASKED***"},
      {"ID": 2, "NAME": "Jane", "EMAIL": "***MASKED***", "SSN": "***MASKED***"}
    ]
  }
  ```

#### 2. Enhanced `/api/continue-execution/<session_id>` (atlan_api_server.py)
- **Added**: Automatic data preview generation after execution
- **What changed**:
  - After successful execution, automatically queries data with different roles
  - Includes `data_preview` in response JSON
  - Frontend receives preview data without additional API call

- **Implementation**:
  ```python
  # After execution completes
  cursor = actions_engine.engine.connector.connection.cursor()
  
  # Get BEFORE (ACCOUNTADMIN - unmasked)
  cursor.execute("USE ROLE ACCOUNTADMIN")
  cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
  
  # Get AFTER with HR_ROLE
  cursor.execute("USE ROLE HR_ROLE")
  cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
  
  # Get AFTER with ANALYST_ROLE
  cursor.execute("USE ROLE ANALYST_ROLE")
  cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
  
  results['data_preview'] = data_views
  ```

### Frontend Changes

#### 1. Updated Data Preview Function (atlan_dashboard.html)
- **File**: `src1/atlan_dashboard.html`
- **Function**: `updateDataPreview(result)`
- **Changes**:
  - Now displays 3 columns instead of 2
  - Shows BEFORE (unmasked), HR_ROLE view, ANALYST_ROLE view
  - Highlights masked fields with colored background
  - Formats data as "Column: Value" pairs

- **Visual Layout**:
  ```
  ┌─────────────────────┬─────────────────────┬─────────────────────┐
  │  🔓 BEFORE          │  🔒 HR_ROLE         │  🔒 ANALYST_ROLE    │
  │  (Unmasked)         │  (Some Access)      │  (Masked)           │
  ├─────────────────────┼─────────────────────┼─────────────────────┤
  │ Row 1:              │ Row 1:              │ Row 1:              │
  │ ID: 1               │ ID: 1               │ ID: 1               │
  │ EMAIL: john@...     │ EMAIL: john@...     │ EMAIL: ***MASKED*** │
  │ SSN: 123-45-6789    │ SSN: 123-45-6789    │ SSN: ***MASKED***   │
  └─────────────────────┴─────────────────────┴─────────────────────┘
  ```

#### 2. Updated CSS (atlan_dashboard.html)
- Changed `.before-after` from `grid` to `flex` layout
- Supports 3 columns with responsive wrapping
- Each column has `flex: 1; min-width: 250px`

- **Before**:
  ```css
  .before-after {
      display: grid;
      grid-template-columns: 1fr 1fr;  /* 2 columns */
  }
  ```

- **After**:
  ```css
  .before-after {
      display: flex;
      flex-wrap: wrap;  /* Supports 3 columns */
      gap: 20px;
  }
  ```

### Testing

#### Test Script: `test_data_preview.py`
- **Location**: `src/test_data_preview.py`
- **Tests**:
  1. `/api/data-preview/<session_id>` - standalone endpoint
  2. `/api/continue-execution/<session_id>` - with embedded preview

- **Usage**:
  ```powershell
  cd src
  python test_data_preview.py
  ```

## How It Works (User Flow)

1. **User submits governance command**:
   ```
   "mask pii in customers table"
   ```

2. **System processes** through 6 phases (OBSERVE → ANALYZE → PLAN → SIMULATE → EXECUTE → LEARN)

3. **User sees simulation** and approves via frontend

4. **System executes** masking policies in Snowflake

5. **Immediately after execution**:
   - Backend automatically queries the table with 3 different roles
   - Returns first 2 rows for each role view
   - Frontend displays side-by-side comparison

6. **User sees**:
   - **Left box**: Original unmasked data (ACCOUNTADMIN)
   - **Middle box**: HR_ROLE view (may see some sensitive data)
   - **Right box**: ANALYST_ROLE view (masked sensitive data)

## Key Features

### ✅ Role-Based Access Control
- Uses Snowflake's `USE ROLE` to switch contexts
- Shows actual masking policy effects per role

### ✅ Automatic Preview
- No separate API call needed
- Preview included in continue-execution response

### ✅ Visual Highlighting
- Masked fields highlighted in yellow/red
- Clear before/after comparison

### ✅ Error Handling
- Graceful fallback if role query fails
- Restores original role after queries
- Handles missing session data

### ✅ Limited Data
- Only first 2 rows (as requested)
- Prevents overwhelming display
- Fast query execution

## API Endpoints Summary

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/data-preview/<session_id>` | GET | Get role-based data comparison | `{table, columns, before, after_hr, after_analyst}` |
| `/api/continue-execution/<session_id>` | POST | Execute approved action + preview | Includes `data_preview` field |

## Files Modified

1. **src/atlan_api_server.py**:
   - Added `/api/data-preview/<session_id>` endpoint (lines ~336-408)
   - Enhanced `/api/continue-execution/<session_id>` with data preview (lines ~559-610)

2. **src1/atlan_dashboard.html**:
   - Updated `updateDataPreview()` function for 3-column display (lines ~844-905)
   - Changed CSS `.before-after` to flex layout (lines ~216-220)

3. **src/test_data_preview.py**: New test script

## Example Output

### Console Output (Backend):
```
✅ Added data preview for CUSTOMERS
📊 Table: CUSTOMERS
📋 Columns: ID, NAME, EMAIL, SSN

🔓 BEFORE (Unmasked - ACCOUNTADMIN):
  Row 1: {'ID': 1, 'NAME': 'John Doe', 'EMAIL': 'john@email.com', 'SSN': '123-45-6789'}
  Row 2: {'ID': 2, 'NAME': 'Jane Smith', 'EMAIL': 'jane@email.com', 'SSN': '987-65-4321'}

🔒 AFTER (HR_ROLE View):
  Row 1: {'ID': 1, 'NAME': 'John Doe', 'EMAIL': 'john@email.com', 'SSN': '123-45-6789'}
  Row 2: {'ID': 2, 'NAME': 'Jane Smith', 'EMAIL': 'jane@email.com', 'SSN': '987-65-4321'}

🔒 AFTER (ANALYST_ROLE View):
  Row 1: {'ID': 1, 'NAME': 'John Doe', 'EMAIL': '***MASKED***', 'SSN': '***MASKED***'}
  Row 2: {'ID': 2, 'NAME': 'Jane Smith', 'EMAIL': '***MASKED***', 'SSN': '***MASKED***'}
```

### Frontend Display:
```
┌─────────────────────────────────────────────────────────────────────┐
│                    🔍 Data Impact Preview                           │
├─────────────────────┬─────────────────────┬─────────────────────────┤
│ 🔓 BEFORE           │ 🔒 HR_ROLE         │ 🔒 ANALYST_ROLE         │
│ (Unmasked)          │                     │                          │
│                     │                     │                          │
│ Row 1:              │ Row 1:              │ Row 1:                   │
│ ID: 1               │ ID: 1               │ ID: 1                    │
│ NAME: John Doe      │ NAME: John Doe      │ NAME: John Doe           │
│ EMAIL: john@...com  │ EMAIL: john@...com  │ EMAIL: [***MASKED***]    │
│ SSN: 123-45-6789    │ SSN: 123-45-6789    │ SSN: [***MASKED***]      │
│                     │                     │                          │
│ Row 2:              │ Row 2:              │ Row 2:                   │
│ ID: 2               │ ID: 2               │ ID: 2                    │
│ NAME: Jane Smith    │ NAME: Jane Smith    │ NAME: Jane Smith         │
│ EMAIL: jane@...com  │ EMAIL: jane@...com  │ EMAIL: [***MASKED***]    │
│ SSN: 987-65-4321    │ SSN: 987-65-4321    │ SSN: [***MASKED***]      │
└─────────────────────┴─────────────────────┴─────────────────────────┘
```

## Technical Implementation Details

### Role Switching Logic
```python
# Save original role
cursor.execute("SELECT CURRENT_ROLE()")
original_role = cursor.fetchone()[0]

# Query with different roles
cursor.execute("USE ROLE ACCOUNTADMIN")
cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
# ... fetch data ...

cursor.execute("USE ROLE HR_ROLE")
cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
# ... fetch data ...

cursor.execute("USE ROLE ANALYST_ROLE")
cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
# ... fetch data ...

# Restore original role
cursor.execute(f"USE ROLE {original_role}")
```

### Data Comparison Logic
```javascript
// Check if value was masked
const isMasked = originalValue !== null && value !== originalValue;

// Highlight masked fields
const displayValue = isMasked ? 
  `<span style="background-color: #ffebee; padding: 2px 5px;">${value}</span>` : 
  value;
```

## Next Steps / Future Enhancements

1. **Add More Roles**: Support comparing more than 2 roles
2. **Row Filtering**: Allow users to select which rows to preview
3. **Column Filtering**: Show only masked columns
4. **Diff Highlighting**: More sophisticated visual diff
5. **Export Feature**: Download comparison as CSV/JSON
6. **Real-time Updates**: WebSocket for live data updates

## Troubleshooting

### Common Issues:

1. **"Session not found"**
   - Ensure you've executed a command first
   - Session ID must match an active session

2. **"No target tables found"**
   - Command must have completed OBSERVE phase
   - Check that observe phase identified target entities

3. **Role errors**
   - Ensure HR_ROLE and ANALYST_ROLE exist in Snowflake
   - Verify current user has permission to switch roles

4. **Empty data arrays**
   - Table might not have data yet
   - Check table exists and has rows

## Testing Checklist

- [x] Backend: `/api/data-preview/<session_id>` endpoint created
- [x] Backend: Data preview added to continue-execution response
- [x] Frontend: 3-column layout CSS updated
- [x] Frontend: updateDataPreview() function enhanced
- [x] Frontend: Masking highlighting added
- [x] Test script: Created test_data_preview.py
- [ ] Integration test: End-to-end workflow test
- [ ] Manual test: UI display verification

## Summary

Successfully implemented role-based data preview that shows users immediate visual feedback when masking policies are applied. Users can now see side-by-side how HR_ROLE and ANALYST_ROLE view the same data differently after governance actions execute.

**User benefit**: Immediate visual confirmation that policies work as intended, with clear before/after comparison for different roles.
