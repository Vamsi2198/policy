# S3 Data Processing Workflow

## Overview

This enhancement changes the data flow to use **S3 JSON data as the source** instead of fetching from Snowflake. The system now:

1. **Loads data from `s3.json`** (instead of querying Snowflake)
2. **Applies runtime masking policies** based on user queries
3. **Inserts masked data into Snowflake `MY_TABLE`**

## Architecture

```
┌─────────────┐
│  s3.json    │  Source: Employee data with PII
│  (Source)   │
└──────┬──────┘
       │
       │ Load
       ▼
┌─────────────────────────┐
│  S3DataHandler          │  Reads JSON, detects schema
│  - load_s3_data()       │
│  - get_schema()         │
└──────┬──────────────────┘
       │
       │ Apply Policies
       ▼
┌─────────────────────────┐
│  Policy Engine          │  Masks PII based on user query
│  - detect_pii()         │  - Email: a***@example.com
│  - apply_masking()      │  - SSN: ***-**-6789
│  - mask_email()         │  - Salary: $70,000 - $80,000
│  - mask_ssn()           │
└──────┬──────────────────┘
       │
       │ Prepare for Snowflake
       ▼
┌─────────────────────────┐
│  Transform to Table     │  Converts to: (id INT, data STRING)
│  - prepare_records()    │  id=1, data='{"name":"Alice",...}'
└──────┬──────────────────┘
       │
       │ Insert
       ▼
┌─────────────────────────┐
│  Snowflake MY_TABLE     │  Final destination
│  CREATE TABLE MY_TABLE  │
│  (id INT, data STRING)  │
└─────────────────────────┘
```

## Files Modified

### 1. **s3_data_handler.py** (NEW)
Main module for S3 data processing:
- `S3DataHandler`: Loads and processes S3 data
- `SnowflakeInserter`: Handles insertion to MY_TABLE
- `apply_policies_and_insert()`: Complete workflow function

### 2. **control_pannel.py** (MODIFIED)
Added S3 chatbot functionality:
- `run_s3_data_chatbot()`: Interactive chatbot for S3 data
- `--s3-chatbot` CLI option
- Integrated S3 handler imports

### 3. **ai_control_plane.py** (MODIFIED)
Added S3 processing method:
- `process_s3_data()`: 5-phase S3 workflow
- Phases: LOAD → ANALYZE → MASK → PREPARE → INSERT

### 4. **atlan_ai_control_plane.py** (MODIFIED)
- Added S3 handler imports
- Compatible with S3 workflow

### 5. **atlan_api_server.py** (MODIFIED)
Added S3 API endpoints:
- `POST /api/s3/process`: Process S3 data with policies
- `GET /api/s3/info`: Get S3 data schema and sample

## Usage

### Method 1: Interactive S3 Chatbot (Recommended)

```bash
# From the src directory
python control_pannel.py --s3-chatbot
```

Example queries:
- `"Mask all email addresses"`
- `"Hide SSN and salary information"`
- `"Protect all PII data and insert to Snowflake"`
- `"Show me all data"` (no masking)

### Method 2: Command Line

```bash
# Using control panel
python control_pannel.py --s3-chatbot
```

### Method 3: Python API

```python
from s3_data_handler import S3DataHandler, SnowflakeInserter, apply_policies_and_insert
from control_pannel import ControlPlaneEngine

# Complete workflow
engine = ControlPlaneEngine()
engine.connect_platform()

result = apply_policies_and_insert(
    user_query="Mask all email and SSN",
    snowflake_connector=engine.connector
)

print(f"Inserted {result['snowflake_insertion']['rows_inserted']} rows")
```

### Method 4: AI Control Plane

```python
from ai_control_plane import AIControlPlane

ai_control = AIControlPlane()
results = ai_control.process_s3_data("Mask all PII and insert to Snowflake")

print(f"Status: {results['status']}")
```

### Method 5: API Server

```bash
# Start the API server
python atlan_api_server.py

# Then use the API
curl -X POST http://localhost:5000/api/s3/process \
  -H "Content-Type: application/json" \
  -d '{"command": "Mask all email and SSN data"}'
```

## S3 Data Format

The `s3.json` file contains employee records:

```json
[
  {
    "name": "Alice Johnson",
    "salary": 72000,
    "email": "alice.johnson@example.com",
    "ssn": "123-45-6789",
    "address": "245 Maple Street, Denver, CO 80203"
  },
  ...
]
```

## Masking Policies

### Automatic PII Detection

The system automatically detects and masks:

| Field Type | Detection | Masking Example |
|-----------|-----------|-----------------|
| Email | Pattern + field name | `a***@example.com` |
| SSN | Pattern + field name | `***-**-6789` |
| Salary | Field name | `$70,000 - $80,000` |
| Address | Field name | `*** Denver, CO 80203` |
| Phone | Pattern | `***-***-1234` |

### Query-Based Masking

You can specify masking in natural language:
- "Mask email" → Masks only email fields
- "Hide salary and SSN" → Masks both fields
- "Protect all PII" → Masks all detected PII

## Snowflake Table Structure

Data is inserted into:

```sql
CREATE TABLE MY_TABLE (
    id INT,
    data STRING
);
```

Each row contains:
- `id`: Sequential number (1, 2, 3, ...)
- `data`: JSON string of the entire record (masked)

Example:
```
ID | DATA
---+--------------------------------------------------------
1  | {"name":"Alice Johnson","email":"a***@example.com",...}
2  | {"name":"Brian Smith","email":"b***@example.com",...}
```

## Testing

### Quick Test

```bash
# Run all tests (non-interactive)
python test_s3_workflow.py --all
```

### Individual Tests

```bash
# Direct processing test
python test_s3_workflow.py --direct

# AI Control Plane test
python test_s3_workflow.py --ai

# Interactive chatbot
python test_s3_workflow.py --chatbot
```

## Workflow Phases (AI Control Plane)

When using the AI Control Plane, the S3 workflow has 5 phases:

1. **LOAD** (Phase 1)
   - Load data from s3.json
   - Parse JSON records
   - Extract schema

2. **ANALYZE** (Phase 2)
   - Detect PII using presidio analyzer
   - Identify sensitive fields
   - Calculate confidence scores

3. **MASK** (Phase 3)
   - Apply masking policies
   - Transform sensitive data
   - Preserve data structure

4. **PREPARE** (Phase 4)
   - Convert to Snowflake format
   - Create (id, data) pairs
   - Serialize to JSON strings

5. **INSERT** (Phase 5)
   - Insert into MY_TABLE
   - Verify insertion
   - Return results

## Configuration

### Snowflake Connection

Ensure your `config.yaml` has Snowflake credentials:

```yaml
platform:
  type: snowflake
  snowflake:
    account: your_account
    user: your_user
    password: your_password
    warehouse: your_warehouse
    database: your_database
    schema: PUBLIC
```

### S3 Data Location

The handler searches for `s3.json` in:
1. Current directory
2. `src/s3.json`
3. `../s3.json`

Or specify explicitly:
```python
s3_handler = S3DataHandler(s3_json_path="/path/to/s3.json")
```

## Benefits

### Before (Snowflake Query)
```
User Query → Snowflake → Apply Policies → Snowflake
```
- Required existing Snowflake data
- Limited to Snowflake schema
- Policies applied in-database

### After (S3 Source)
```
User Query → S3 JSON → Apply Policies → Snowflake
```
- ✅ Works with any JSON data source
- ✅ Runtime policy application
- ✅ No database dependencies for source
- ✅ Flexible schema detection
- ✅ Can process data before storage

## API Endpoints

### Process S3 Data
```http
POST /api/s3/process
Content-Type: application/json

{
  "command": "Mask all email addresses",
  "session_id": "optional_session_id"
}
```

Response:
```json
{
  "status": "success",
  "source": "S3",
  "target": "Snowflake MY_TABLE",
  "phases": {
    "load": {"status": "success", "records": 9},
    "analyze": {"pii_findings": [...]},
    "mask": {"policies_applied": [...]},
    "prepare": {"records_prepared": 9},
    "insert": {"rows_inserted": 9}
  }
}
```

### Get S3 Info
```http
GET /api/s3/info
```

Response:
```json
{
  "status": "success",
  "total_records": 9,
  "schema": {...},
  "sample_data": [...]
}
```

## Troubleshooting

### S3 file not found
- Ensure `s3.json` is in the src directory
- Or specify path explicitly in code

### Snowflake connection failed
- Check `config.yaml` credentials
- Ensure Snowflake warehouse is running
- Test with `--test-connection`

### Masking not applied
- Check if PII fields are detected
- Use explicit field names in query
- View PII findings in analyze phase

### Import errors
- Ensure all files are in src directory
- Run from src directory: `cd src`
- Check Python path

## Examples

### Example 1: Mask Email Only
```bash
python control_pannel.py --s3-chatbot
> Mask all email addresses
```

Result:
- Emails: `a***@example.com`
- Other fields: Unchanged

### Example 2: Mask Multiple Fields
```bash
> Hide SSN and salary information
```

Result:
- SSN: `***-**-6789`
- Salary: `$70,000 - $80,000`
- Other fields: Unchanged

### Example 3: Full Workflow
```bash
> Protect all PII and insert to Snowflake
```

Result:
- All PII fields masked
- Data inserted to MY_TABLE
- Verification shown

## Summary

This implementation provides a complete **S3 → Policy Application → Snowflake** workflow that:

✅ Loads data from JSON source (s3.json)  
✅ Applies runtime masking policies based on user queries  
✅ Inserts masked data into Snowflake MY_TABLE  
✅ Provides multiple interfaces (CLI, API, chatbot)  
✅ Integrates with existing AI Control Plane  
✅ Maintains audit trail and metadata  

The system is now **source-agnostic** and can process any JSON data with flexible policy application before storage.
