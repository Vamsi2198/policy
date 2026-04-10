#!/usr/bin/env python3
"""
Snowflake Query Log Viewer
Displays recent Snowflake query execution logs with filtering options
"""

import os
import sys
from datetime import datetime, timedelta
import re
from collections import defaultdict

def parse_log_entry(lines):
    """Parse a log entry from multiple lines"""
    entry = {
        'timestamp': None,
        'query': None,
        'status': None,
        'execution_time': None,
        'rows_affected': None,
        'rows_returned': None,
        'error': None,
        'query_id': None
    }
    
    full_text = '\n'.join(lines)
    
    # Extract timestamp
    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})', full_text)
    if timestamp_match:
        entry['timestamp'] = timestamp_match.group(1)
    
    # Extract query
    query_match = re.search(r'Query: (.+?)(?:\n|$)', full_text, re.DOTALL)
    if query_match:
        entry['query'] = query_match.group(1).strip()
    
    # Check status
    if '✅' in full_text or 'SUCCESS' in full_text:
        entry['status'] = 'SUCCESS'
    elif '❌' in full_text or 'FAILED' in full_text:
        entry['status'] = 'FAILED'
    
    # Extract execution time
    time_match = re.search(r'Execution time: ([\d.]+)s', full_text)
    if time_match:
        entry['execution_time'] = float(time_match.group(1))
    
    # Extract rows affected/returned
    rows_affected_match = re.search(r'Rows affected: (\d+)', full_text)
    if rows_affected_match:
        entry['rows_affected'] = int(rows_affected_match.group(1))
    
    rows_returned_match = re.search(r'Rows returned: (\d+)', full_text)
    if rows_returned_match:
        entry['rows_returned'] = int(rows_returned_match.group(1))
    
    # Extract error
    error_match = re.search(r'Error: (.+?)(?:\n|$)', full_text)
    if error_match:
        entry['error'] = error_match.group(1).strip()
    
    # Extract query ID
    query_id_match = re.search(r'Query ID: (.+?)(?:\n|$)', full_text)
    if query_id_match:
        qid = query_id_match.group(1).strip()
        if qid != 'N/A':
            entry['query_id'] = qid
    
    return entry

def read_log_file(log_file='snowflake_queries.log'):
    """Read and parse the log file"""
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        return []
    
    entries = []
    current_entry_lines = []
    in_entry = False
    
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' * 40 in line:
                if in_entry and current_entry_lines:
                    # Parse the completed entry
                    entry = parse_log_entry(current_entry_lines)
                    if entry['query']:  # Only add if we found a query
                        entries.append(entry)
                    current_entry_lines = []
                in_entry = not in_entry
            elif in_entry:
                current_entry_lines.append(line.strip())
    
    # Parse last entry if exists
    if current_entry_lines:
        entry = parse_log_entry(current_entry_lines)
        if entry['query']:
            entries.append(entry)
    
    return entries

def display_summary(entries):
    """Display summary statistics"""
    if not entries:
        print("📊 No log entries found")
        return
    
    total = len(entries)
    success = sum(1 for e in entries if e['status'] == 'SUCCESS')
    failed = sum(1 for e in entries if e['status'] == 'FAILED')
    
    total_time = sum(e['execution_time'] for e in entries if e['execution_time'])
    avg_time = total_time / total if total > 0 else 0
    
    print("\n" + "="*80)
    print("📊 SNOWFLAKE QUERY LOG SUMMARY")
    print("="*80)
    print(f"Total Queries:     {total}")
    print(f"✅ Successful:     {success} ({success/total*100:.1f}%)")
    print(f"❌ Failed:         {failed} ({failed/total*100:.1f}%)")
    print(f"⏱️  Total Time:     {total_time:.2f}s")
    print(f"⏱️  Average Time:   {avg_time:.3f}s")
    
    # Query type breakdown
    query_types = defaultdict(int)
    for entry in entries:
        if entry['query']:
            query_upper = entry['query'].upper().strip()
            for qtype in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'SHOW', 'DESCRIBE']:
                if query_upper.startswith(qtype):
                    query_types[qtype] += 1
                    break
    
    if query_types:
        print("\n📝 Query Types:")
        for qtype, count in sorted(query_types.items(), key=lambda x: -x[1]):
            print(f"   {qtype:12} {count:3} queries")
    
    print("="*80 + "\n")

def display_entries(entries, filter_status=None, filter_type=None, limit=None, show_errors=False):
    """Display log entries with optional filtering"""
    if not entries:
        print("No entries to display")
        return
    
    # Apply filters
    filtered = entries
    
    if filter_status:
        filtered = [e for e in filtered if e['status'] == filter_status]
    
    if filter_type:
        filtered = [e for e in filtered if e['query'] and e['query'].upper().startswith(filter_type.upper())]
    
    if limit:
        filtered = filtered[-limit:]  # Show most recent
    
    print(f"\n📋 Displaying {len(filtered)} entries:\n")
    
    for i, entry in enumerate(filtered, 1):
        status_icon = "✅" if entry['status'] == 'SUCCESS' else "❌"
        print(f"{'-'*80}")
        print(f"Entry #{i} | {status_icon} {entry['status']} | {entry['timestamp'] or 'No timestamp'}")
        print(f"{'-'*80}")
        
        if entry['query']:
            query_preview = entry['query'][:200] + ('...' if len(entry['query']) > 200 else '')
            print(f"Query: {query_preview}")
        
        if entry['execution_time']:
            print(f"⏱️  Execution Time: {entry['execution_time']:.3f}s")
        
        if entry['rows_affected']:
            print(f"📝 Rows Affected: {entry['rows_affected']}")
        
        if entry['rows_returned']:
            print(f"📊 Rows Returned: {entry['rows_returned']}")
        
        if entry['query_id']:
            print(f"🔍 Query ID: {entry['query_id']}")
        
        if entry['error'] and (show_errors or filter_status == 'FAILED'):
            print(f"❌ Error: {entry['error']}")
        
        print()

def main():
    """Main function to display logs"""
    import argparse
    
    parser = argparse.ArgumentParser(description='View Snowflake query logs')
    parser.add_argument('--file', default='snowflake_queries.log', help='Log file path')
    parser.add_argument('--status', choices=['SUCCESS', 'FAILED'], help='Filter by status')
    parser.add_argument('--type', help='Filter by query type (SELECT, INSERT, etc.)')
    parser.add_argument('--limit', type=int, help='Limit number of entries to show (most recent)')
    parser.add_argument('--errors', action='store_true', help='Show error details for failed queries')
    parser.add_argument('--summary-only', action='store_true', help='Show only summary statistics')
    
    args = parser.parse_args()
    
    print("\n🔍 Snowflake Query Log Viewer")
    print(f"📁 Reading from: {args.file}\n")
    
    entries = read_log_file(args.file)
    
    if not entries:
        print("❌ No log entries found")
        return
    
    display_summary(entries)
    
    if not args.summary_only:
        display_entries(
            entries, 
            filter_status=args.status,
            filter_type=args.type,
            limit=args.limit,
            show_errors=args.errors
        )

if __name__ == '__main__':
    main()
