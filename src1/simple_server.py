#!/usr/bin/env python3
"""
Simple Flask Server for Atlan Actions Dashboard
Fixed version with proper CORS and localhost binding
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Atlan Actions API - Working!</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; }
            .status { color: green; font-size: 20px; }
        </style>
    </head>
    <body>
        <h1>🎯 Atlan Actions API Server</h1>
        <div class="status">✅ Server is running successfully!</div>
        <p>API endpoints available at:</p>
        <ul style="list-style: none;">
            <li>GET /api/health</li>
            <li>POST /api/process</li>
            <li>GET /api/policies</li>
        </ul>
        <br>
        <p><strong>📱 Use the HTML dashboard:</strong></p>
        <p>Open: <code>atlan_dashboard.html</code></p>
    </body>
    </html>
    """

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Atlan Actions API is running',
        'version': '1.0.0',
        'timestamp': '2025-10-31T21:20:00Z'
    })

@app.route('/api/process', methods=['POST'])
def process_command():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Mock response for demonstration
        response = {
            'query': query,
            'execution_time': 2.5,
            'confidence': 0.95,
            'policies_created': 3,
            'tables_affected': 1,
            'columns_protected': 4,
            'atlan_synced_items': 3,
            'phases': {
                'observe': {
                    'status': 'completed',
                    'intent': 'MASK',
                    'confidence': 0.95,
                    'entities_count': 1,
                    'duration': 0.5
                },
                'analyze': {
                    'status': 'completed',
                    'pii_findings_count': 4,
                    'risk_level': 'MEDIUM',
                    'duration': 0.8
                },
                'plan': {
                    'status': 'completed',
                    'sql_commands_count': 8,
                    'strategy': 'Masking',
                    'duration': 0.3
                },
                'simulate': {
                    'status': 'completed',
                    'rows_affected': 100000,
                    'risk_assessment': 'LOW',
                    'duration': 0.2
                },
                'execute': {
                    'status': 'completed',
                    'commands_executed': 8,
                    'atlan_sync_status': 'Completed',
                    'duration': 0.6
                },
                'learn': {
                    'status': 'completed',
                    'patterns_discovered': 2,
                    'recommendations_count': 3,
                    'duration': 0.1
                }
            },
            'policies': [
                {
                    'name': 'customers_email_masking_policy',
                    'table': 'PUBLIC.CUSTOMERS',
                    'column': 'EMAIL',
                    'pii_types': ['EMAIL_ADDRESS'],
                    'confidence': 0.95,
                    'atlan_synced': True
                },
                {
                    'name': 'customers_ssn_masking_policy',
                    'table': 'PUBLIC.CUSTOMERS',
                    'column': 'SSN',
                    'pii_types': ['SSN'],
                    'confidence': 0.98,
                    'atlan_synced': True
                },
                {
                    'name': 'customers_phone_masking_policy',
                    'table': 'PUBLIC.CUSTOMERS',
                    'column': 'PHONE',
                    'pii_types': ['PHONE_NUMBER'],
                    'confidence': 0.92,
                    'atlan_synced': True
                }
            ],
            'recommendations': [
                {
                    'title': '🔍 Similar Pattern Detected',
                    'description': 'Apply similar masking policies to EMPLOYEES table which has EMAIL, PHONE, SSN columns'
                },
                {
                    'title': '⚡ Continuous Monitoring',
                    'description': 'Set up automated PII scanning for new tables and columns'
                },
                {
                    'title': '📊 Compliance Enhancement',
                    'description': 'Consider implementing column-level lineage tracking for complete audit trail'
                }
            ],
            'data_preview': {
                'before': [
                    'ID: 1, EMAIL: john.doe@company.com, SSN: 123-45-6789',
                    'ID: 2, EMAIL: jane.smith@corp.org, PHONE: 555-123-4567',
                    'ID: 3, EMAIL: bob.wilson@business.net, SSN: 987-65-4321'
                ],
                'after': [
                    'ID: 1, EMAIL: joh***@***.com, SSN: ***MASKED***',
                    'ID: 2, EMAIL: jan***@***.org, PHONE: ***MASKED***',
                    'ID: 3, EMAIL: bob***@***.net, SSN: ***MASKED***'
                ]
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to process command'
        }), 500

@app.route('/api/policies', methods=['GET'])
def get_policies():
    return jsonify({
        'policies': [
            {
                'name': 'customers_email_masking_policy',
                'table': 'PUBLIC.CUSTOMERS',
                'column': 'EMAIL',
                'status': 'ACTIVE',
                'created': '2025-10-31T21:15:00Z'
            }
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Simple Atlan Actions API Server...")
    print("📱 Dashboard will be available at: http://localhost:3000")
    print("🔗 API Health: http://localhost:3000/api/health")
    
    # Run on a different port to avoid conflicts
    app.run(
        host='127.0.0.1',  # Explicit localhost binding
        port=3000,         # Different port
        debug=True,
        use_reloader=False  # Prevent file watching issues
    )