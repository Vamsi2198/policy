# Snowflake Query Logging

## Overview

Comprehensive logging system for tracking all Snowflake query executions, including successful queries, failures, execution times, and detailed error information.

## Features

✅ **Detailed Query Logging**
- Every query execution is logged with timestamp
- Execution time tracking (millisecond precision)
- Rows affected/returned counts
- Snowflake Query IDs for tracking in Snowflake console
- Query type detection (SELECT, INSERT, UPDATE, etc.)

✅ **Error Tracking**
- Detailed error messages
- Error type identification
- Failed query preservation for debugging
- Execution time even for failed queries

✅ **Dual Logging**
- Console output for real-time monitoring
- Persistent file logging (`snowflake_queries.log`)
- Separate logger to avoid interference with application logs

## Log File Location

```
snowflake_queries.log
```

The log file is created automatically in the current working directory when the first query is executed.

## Log Format

Each log entry contains:

```
================================================================================
📤 EXECUTING SNOWFLAKE QUERY:
Query: SELECT * FROM EMPLOYEE_DATA LIMIT 10
Timestamp: 2025-12-08T10:30:45.123456

✅ SNOWFLAKE QUERY SUCCESS (SELECT)
Rows returned: 10
Execution time: 0.234s
Sample results: [(1, 'John', 'Doe'), ...]
================================================================================
```

For failed queries:

```
================================================================================
📤 EXECUTING SNOWFLAKE QUERY:
Query: CREATE MASKING POLICY invalid_policy...
Timestamp: 2025-12-08T10:31:12.456789

❌ SNOWFLAKE QUERY FAILED
Error: SQL compilation error: syntax error line 1 at position 45
Error Type: ProgrammingError
Execution time: 0.156s
Failed Query: CREATE MASKING POLICY invalid_policy...
================================================================================
```

## Viewing Logs

### Using the Log Viewer Script

```bash
# View all logs with summary
python src/view_snowflake_logs.py

# View only failed queries
python src/view_snowflake_logs.py --status FAILED --errors

# View last 10 queries
python src/view_snowflake_logs.py --limit 10

# Filter by query type
python src/view_snowflake_logs.py --type SELECT

# Show only summary statistics
python src/view_snowflake_logs.py --summary-only
```

### Manual Log Viewing

You can also view the log file directly:

```bash
# View entire log
cat snowflake_queries.log

# View last 50 lines
tail -n 50 snowflake_queries.log

# Search for failed queries
grep -A 10 "FAILED" snowflake_queries.log

# Search for specific query type
grep -A 5 "CREATE MASKING POLICY" snowflake_queries.log
```

## Log Viewer Options

```
usage: view_snowflake_logs.py [-h] [--file FILE] [--status {SUCCESS,FAILED}]
                              [--type TYPE] [--limit LIMIT] [--errors]
                              [--summary-only]

View Snowflake query logs

optional arguments:
  --file FILE              Log file path (default: snowflake_queries.log)
  --status {SUCCESS,FAILED}
                          Filter by status
  --type TYPE             Filter by query type (SELECT, INSERT, etc.)
  --limit LIMIT           Limit number of entries to show (most recent)
  --errors                Show error details for failed queries
  --summary-only          Show only summary statistics
```

## Example Output

### Summary Statistics

```
================================================================================
📊 SNOWFLAKE QUERY LOG SUMMARY
================================================================================
Total Queries:     45
✅ Successful:     42 (93.3%)
❌ Failed:         3 (6.7%)
⏱️  Total Time:     12.45s
⏱️  Average Time:   0.277s

📝 Query Types:
   CREATE          15 queries
   ALTER           12 queries
   SELECT          10 queries
   SHOW             5 queries
   DROP             3 queries
================================================================================
```

### Individual Entries

```
📋 Displaying 3 entries:

--------------------------------------------------------------------------------
Entry #1 | ✅ SUCCESS | 2025-12-08 10:30:45,123
--------------------------------------------------------------------------------
Query: CREATE OR REPLACE MASKING POLICY analyst_role_mask AS (val STRING) 
       RETURNS STRING -> CASE WHEN CURRENT_ROLE() IN ('ADMIN') 
       THEN val ELSE '***MASKED***' END
⏱️  Execution Time: 0.145s
📝 Rows Affected: 0
🔍 Query ID: 01b2c3d4-e5f6-7890-abcd-ef1234567890

--------------------------------------------------------------------------------
Entry #2 | ✅ SUCCESS | 2025-12-08 10:30:45,345
--------------------------------------------------------------------------------
Query: ALTER TABLE PUBLIC.EMPLOYEE_DATA MODIFY COLUMN SALARY 
       SET MASKING POLICY analyst_role_mask
⏱️  Execution Time: 0.234s
📝 Rows Affected: 0
🔍 Query ID: 02c3d4e5-f6a7-8901-bcde-f12345678901

--------------------------------------------------------------------------------
Entry #3 | ❌ FAILED | 2025-12-08 10:30:46,567
--------------------------------------------------------------------------------
Query: ALTER TABLE PUBLIC.EMPLOYEE_DATA MODIFY COLUMN INVALID_COLUMN 
       SET MASKING POLICY test_mask
⏱️  Execution Time: 0.089s
❌ Error: SQL compilation error: invalid identifier 'INVALID_COLUMN'
```

## Integration with Governance Flow

The logging is integrated at multiple levels:

1. **Low-level connector** (`control_pannel.py`):
   - All Snowflake queries executed through `SnowflakeConnector.execute()`
   - Captures raw query execution details

2. **Governance engine** (`atlan_ai_control_plane.py`):
   - Additional logging for governance workflow context
   - Tracks which phase is executing queries
   - Links queries to natural language commands

## Troubleshooting

### Query Failed - How to Debug?

1. Check the log file for the full error message:
   ```bash
   python src/view_snowflake_logs.py --status FAILED --errors
   ```

2. Look for the Snowflake Query ID and check in Snowflake console:
   ```sql
   SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
   WHERE QUERY_ID = 'your-query-id-here';
   ```

3. Review the exact SQL that was attempted

### Performance Issues?

1. Check average execution times:
   ```bash
   python src/view_snowflake_logs.py --summary-only
   ```

2. Identify slow queries:
   ```bash
   grep "Execution time" snowflake_queries.log | sort -t':' -k2 -n
   ```

### Log File Getting Too Large?

The log file will grow over time. You can:

1. Archive old logs:
   ```bash
   mv snowflake_queries.log snowflake_queries_$(date +%Y%m%d).log
   ```

2. Truncate the log:
   ```bash
   > snowflake_queries.log
   ```

3. Keep only recent entries:
   ```bash
   tail -n 1000 snowflake_queries.log > snowflake_queries_temp.log
   mv snowflake_queries_temp.log snowflake_queries.log
   ```

## Benefits

✅ **Debugging**: Quick identification of failed queries and root causes
✅ **Performance**: Track slow queries and optimize
✅ **Audit**: Complete trail of all database operations
✅ **Monitoring**: Real-time and historical query analysis
✅ **Compliance**: Evidence of what queries were executed and when

## Next Steps

- Set up log rotation for production environments
- Integrate with monitoring systems (Datadog, Splunk, etc.)
- Create alerts for high failure rates
- Export logs to centralized logging platform
