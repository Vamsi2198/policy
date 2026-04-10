# S3 Workflow - Quick Reference

## 🚀 Quick Start

```bash
cd src
python control_pannel.py --s3-chatbot
```

## 📝 Example Queries

| Query | Result |
|-------|--------|
| `"Mask all email addresses"` | Email → `a***@example.com` |
| `"Hide SSN and salary"` | SSN → `***-**-6789`, Salary → `$70K-$80K` |
| `"Protect all PII"` | All sensitive fields masked |
| `"Show me all data"` | Display without masking |

## 🔧 All Commands

```bash
# Interactive chatbot (recommended)
python control_pannel.py --s3-chatbot

# Run tests
python test_s3_workflow.py --direct    # Direct test
python test_s3_workflow.py --ai        # AI test
python test_s3_workflow.py --all       # All tests

# Start API server
python atlan_api_server.py
# Then: POST to http://localhost:5000/api/s3/process
```

## 📊 Data Format

**S3 Input (s3.json)**:
```json
{"name": "Alice", "email": "alice@example.com", "ssn": "123-45-6789"}
```

**Snowflake Output (MY_TABLE)**:
```
ID | DATA
1  | {"name":"Alice","email":"a***@example.com","ssn":"***-**-6789"}
```

## 🛡️ Masking Rules

- **Email**: `alice@example.com` → `a***@example.com`
- **SSN**: `123-45-6789` → `***-**-6789`  
- **Salary**: `72000` → `$70,000 - $80,000`
- **Address**: `123 Main St, Denver, CO` → `*** Denver, CO`
- **Phone**: `555-123-4567` → `***-***-4567`

## 🔍 Files

| File | Purpose |
|------|---------|
| `s3_data_handler.py` | Core S3 processing |
| `s3.json` | Source data (9 records) |
| `test_s3_workflow.py` | Test suite |
| `S3_WORKFLOW_README.md` | Full documentation |

## ⚡ Workflow

```
Load s3.json → Detect PII → Mask Data → Insert to MY_TABLE
```

## ✅ That's it!

Start chatbot: `python control_pannel.py --s3-chatbot`
