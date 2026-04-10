# 🚀 Quick Start Guide - Governance Actions Dashboard

## 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)

```bash
cd src
pip install -r requirements_streamlit.txt
```

### Step 2: Start Dashboard (1 minute)

**Windows:**

```bash
run_dashboard.bat
```

**Linux/Mac:**

```bash
bash run_dashboard.sh
```

**Manual:**

```bash
python run_governance_dashboard.py
```

### Step 3: Open Browser (instantly)

- Opens automatically to http://localhost:8501
- If not, open manually in your browser

### Step 4: You're Ready! 🎉

## Example Commands to Try

### 1. Basic Masking

```
"mask pii in employees"
```

✅ Masks all PII columns in the employees table

### 2. Column-Specific

```
"mask salary in employee table"
```

✅ Masks ONLY the salary column

### 3. Role-Based Masking

```
"mask salary for analyst role"
```

✅ Applies role-specific rules (analyst sees rounded value)

### 4. Multiple Columns & Roles

```
"mask salary and phone for analyst and manager"
```

✅ Advanced masking with multiple rules

### 5. Auto-Discovery

```
"automatically discover and mask all pii"
```

✅ Full PII scan and masking

### 6. Show Policies

```
"show current governance policies"
```

✅ Display all active policies

## What You'll See

### 📊 Phase Workflow

```
1. OBSERVE → 2. ANALYZE → 3. PLAN → 4. SIMULATE → 5. EXECUTE → 6. LEARN
  ✓        ✓        ✓         ✓        ◆        ○
```

### 📈 Results

- Execution time
- SQL commands generated
- Affected rows/columns
- Success status

### 📚 Additional Tabs

- **Metadata** - Classifications and policies
- **Audit Logs** - Execution history
- **Analytics** - Performance metrics

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

```bash
pip install streamlit
```

### "Address already in use" (Port 8501)

```bash
streamlit run streamlit_app.py --server.port=8502
```

### "Failed to connect to API"

Ensure Flask server is running. Check terminal for errors.

### "Column not detected"

Use supported column names: salary, email, phone, ssn, etc.

## Next Steps

1. ✅ Run example commands above
2. 📊 Check Metadata tab for policies
3. 📋 Review Audit Logs tab
4. 📈 Analyze results in Analytics tab
5. 📚 Read STREAMLIT_DASHBOARD_README.md for full guide

## System Requirements

- **Python**: 3.8+
- **RAM**: 2GB minimum
- **Disk Space**: 500MB
- **Ports**: 5000 (Flask), 8501 (Streamlit)
- **Network**: Works on local network (0.0.0.0)

## Architecture

```
Browser (http://localhost:8501)
    ↓
Streamlit Frontend
    ↓
Flask API (http://localhost:5000)
    ↓
Governance Engine
    ↓
Snowflake / Database
```

## Features Enabled

✅ Natural language commands
✅ 6-phase workflow
✅ Column detection
✅ Role-based masking
✅ Real-time monitoring
✅ Audit logging
✅ SQL generation
✅ Policy management

## Getting Help

- Check **STREAMLIT_DASHBOARD_README.md** for full documentation
- Review **DYNAMIC_MASKING_QUICK_REFERENCE.md** for feature details
- Check **CODE_EXAMPLES_DYNAMIC_MASKING.md** for API examples

## Running on Network

To access from other computers:

```
http://<your-computer-ip>:8501
```

Replace `<your-computer-ip>` with actual IP (e.g., 192.168.1.100)

## API Direct Access

You can also use the API directly without Streamlit:

```bash
# Health check
curl http://localhost:5000/api/health

# Process command
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{"query":"mask salary"}'

# Get metadata
curl http://localhost:5000/api/metadata

# Get audit logs
curl http://localhost:5000/api/audit-logs
```

## Stop the Dashboard

Press `Ctrl+C` in the terminal to stop all services.

---

**You're all set!** 🎉

Start using the Governance Actions Dashboard now!
