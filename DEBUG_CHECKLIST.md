# Debug Checklist - Data Tables Not Showing

## How to Debug This Issue

### Step 1: Restart Flask Server
```powershell
# Stop the current server (Ctrl+C)
# Then restart it
python src/atlan_api_server.py
```

### Step 2: Open Browser Console
1. Open your browser
2. Press **F12** to open Developer Tools
3. Click on the **Console** tab
4. Keep this open while testing

### Step 3: Run a Test Command
1. Go to the Atlan Actions Dashboard
2. Enter command: `mask email in PUBLIC.EMPLOYEES_DATA`
3. Click **Execute**
4. Wait for approval prompt
5. Click **"Approve & Execute"**

### Step 4: Check Server Console (Python Terminal)

Look for these messages in sequence:

#### Before Approval:
```
📊 [PREVIEW] Switched to role: HR_ROLE
✅ [PREVIEW] Fetched 2 rows as HR_ROLE
```

#### After Approval:
```
🔍 DATA PREVIEW PREPARATION:
   - Target entities: ['PUBLIC.EMPLOYEES_DATA']
   
🔍 Starting data preview fetch for table: PUBLIC.EMPLOYEES_DATA
📊 Switched to role: HR_ROLE
✅ Fetched 2 rows as HR_ROLE
📊 Switched to role: ANALYST_ROLE
✅ Fetched 2 rows as ANALYST_ROLE
✅ Added POST-EXECUTION data preview for PUBLIC.EMPLOYEES_DATA
   - BEFORE rows: 2
   - HR_ROLE rows: 2
   - Analyst rows: 2

============================================================
📤 FINAL RESPONSE CHECK:
   - Has data_preview: True
   - Columns: X
============================================================
```

**❌ If you see**: "Cannot add data preview" - Check which component is missing

### Step 5: Check Browser Console (F12)

Look for these messages:

#### After Approval:
```
✅ Continue execution response: {Object}
📊 Data preview available: true
   - Table: PUBLIC.EMPLOYEES_DATA
   - Columns: 6
   - Before rows: 2
   - HR rows: 2
   - Analyst rows: 2
```

#### During Rendering:
```
📺 displayResult called with: {Object}
📺 result.data_preview exists: true
🔍 Checking for data_preview: {Object}
✅ RENDERING DATA PREVIEW NOW!
   Columns: 6
   Before rows: 2
   HR rows: 2
   Analyst rows: 2
✅ DATA PREVIEW HTML ADDED TO RESULT!
📺 HTML length from formatResultDetails: XXXXX
📺 Result appended to container
```

**❌ If you see**: "Data preview NOT added - missing data_preview or columns"

### Common Issues and Solutions

#### Issue 1: "No target entities found"
**Cause**: The observe phase didn't capture the table name
**Solution**: Check if the command mentions a specific table

#### Issue 2: "Actions engine not available"
**Cause**: Engine didn't initialize properly
**Solution**: Restart the Flask server

#### Issue 3: "Connector not available"
**Cause**: Database connection lost
**Solution**: Check Snowflake credentials in config.yaml

#### Issue 4: Data preview exists but not rendering
**Cause**: JavaScript condition failing
**Check**: Browser console for "Data preview NOT added" message
**Solution**: Verify `result.data_preview.columns` is an array

#### Issue 5: SQL errors when switching roles
**Cause**: Roles don't exist or no permission
**Solution**: 
```sql
-- Run in Snowflake to create roles if missing:
CREATE ROLE IF NOT EXISTS HR_ROLE;
CREATE ROLE IF NOT EXISTS ANALYST_ROLE;
GRANT USAGE ON DATABASE PUBLIC TO ROLE HR_ROLE;
GRANT USAGE ON DATABASE PUBLIC TO ROLE ANALYST_ROLE;
```

### Expected Final Result

You should see **three side-by-side panels**:

1. **🔓 BEFORE (Unmasked - ACCOUNTADMIN)**
   - Shows raw data without masking
   
2. **🔒 AFTER (HR_ROLE View)**
   - Shows: "Current Role: HR_ROLE"
   - Shows masked data as HR sees it
   
3. **🔒 AFTER (ANALYST_ROLE View)**
   - Shows: "Current Role: ANALYST_ROLE"
   - Shows masked data as ANALYST sees it

### Send Me This Info If Still Not Working

If tables still don't show, send me:

1. **Last 50 lines from Python console** (after clicking Approve)
2. **All console logs from Browser Console** (F12)
3. **Screenshot of the page** after approval
4. **Network tab** - look for `/api/continue-execution/{session_id}` response

I can then pinpoint exactly where the issue is!
