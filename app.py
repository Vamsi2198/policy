#!/usr/bin/env python3
"""
Flask Web Application for Atlan AI Control Plane
Runs on localhost:5000
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from atlan_ai_control_plane import AtlanActionsEngine
    ENGINE_AVAILABLE = True
except ImportError:
    print("⚠️  AtlanActionsEngine not available")
    ENGINE_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Initialize engine
if ENGINE_AVAILABLE:
    try:
        engine = AtlanActionsEngine(
            config_path=os.path.join(os.path.dirname(__file__), 'src', 'config.yaml'),
            use_llm=True,
            execution_mode='direct'
        )
        print("✅ Atlan Actions Engine initialized successfully")
    except Exception as e:
        print(f"⚠️  Error initializing engine: {e}")
        engine = None
else:
    engine = None

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Atlan AI Control Plane</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .content { padding: 40px; }
        .query-section {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        .query-box {
            width: 100%;
            padding: 15px 20px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            margin-bottom: 15px;
            transition: border-color 0.3s;
        }
        .query-box:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            font-size: 16px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            font-weight: 600;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn:active { transform: translateY(0); }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .results {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            display: none;
        }
        .results.show { display: block; }
        .phase {
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .phase h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.pending { background: #fff3cd; color: #856404; }
        .status.error { background: #f8d7da; color: #721c24; }
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
            font-size: 1.2em;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .examples {
            background: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .examples h3 { color: #333; margin-bottom: 15px; }
        .example-item {
            background: white;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .example-item:hover { background: #f0f0f0; }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Atlan AI Control Plane</h1>
            <p>Autonomous Data Governance System</p>
            <p style="font-size: 0.9em; margin-top: 10px;">6-Phase Loop: OBSERVE → ANALYZE → PLAN → SIMULATE → EXECUTE → LEARN</p>
        </div>
        
        <div class="content">
            <div class="query-section">
                <h2 style="margin-bottom: 20px;">Enter Governance Command</h2>
                <input 
                    type="text" 
                    id="query" 
                    class="query-box" 
                    placeholder="e.g., 'mask PII in customers table' or 'show me all sensitive data'"
                    autofocus
                >
                <button onclick="processQuery()" class="btn" id="executeBtn">Execute Governance Action</button>
            </div>

            <div class="examples">
                <h3>💡 Example Commands</h3>
                <div class="example-item" onclick="setQuery('mask PII in customers table')">
                    🔒 mask PII in customers table
                </div>
                <div class="example-item" onclick="setQuery('show me all sensitive data')">
                    🔍 show me all sensitive data
                </div>
                <div class="example-item" onclick="setQuery('apply GDPR compliance to user_data')">
                    ⚖️ apply GDPR compliance to user_data
                </div>
                <div class="example-item" onclick="setQuery('detect PII in all tables')">
                    🎯 detect PII in all tables
                </div>
            </div>

            <div id="results" class="results"></div>
        </div>
    </div>

    <script>
        function setQuery(text) {
            document.getElementById('query').value = text;
            document.getElementById('query').focus();
        }

        async function processQuery() {
            const query = document.getElementById('query').value.trim();
            const resultsDiv = document.getElementById('results');
            const executeBtn = document.getElementById('executeBtn');
            
            if (!query) {
                alert('Please enter a governance command');
                return;
            }
            
            // Show loading state
            resultsDiv.className = 'results show';
            resultsDiv.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Processing your governance request...</p>
                    <p style="font-size: 0.9em; opacity: 0.7; margin-top: 10px;">Running 6-phase AI control loop</p>
                </div>
            `;
            executeBtn.disabled = true;
            
            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayResults(data);
                } else {
                    resultsDiv.innerHTML = `
                        <div class="phase">
                            <span class="status error">Error</span>
                            <h3>❌ Request Failed</h3>
                            <p>${data.error || 'Unknown error occurred'}</p>
                        </div>
                    `;
                }
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="phase">
                        <span class="status error">Error</span>
                        <h3>❌ Connection Error</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            } finally {
                executeBtn.disabled = false;
            }
        }

        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            
            let html = `
                <div class="phase">
                    <span class="status ${data.status === 'success' ? 'success' : 'pending'}">
                        ${data.status.toUpperCase()}
                    </span>
                    <h3>📊 Execution Summary</h3>
                    <p><strong>Query:</strong> ${data.original_query || 'N/A'}</p>
                </div>
            `;
            
            // Show phase results
            const phases = ['observe', 'analyze', 'plan', 'simulate', 'execute', 'learn'];
            phases.forEach(phase => {
                if (data[phase]) {
                    html += `
                        <div class="phase">
                            <h3>🔄 ${phase.toUpperCase()} Phase</h3>
                            <pre>${JSON.stringify(data[phase], null, 2)}</pre>
                        </div>
                    `;
                }
            });
            
            // Show full response
            html += `
                <div class="phase">
                    <h3>📄 Complete Response</h3>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                </div>
            `;
            
            resultsDiv.innerHTML = html;
        }

        // Allow Enter key to submit
        document.getElementById('query').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                processQuery();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/process', methods=['POST'])
def process_query():
    """Process natural language governance query"""
    data = request.json
    query = data.get('query', '').strip()
    session_id = data.get('session_id')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    if not engine:
        return jsonify({
            'error': 'Engine not available',
            'status': 'error',
            'message': 'Atlan Actions Engine is not initialized. Please check server logs.'
        }), 500
    
    try:
        results = engine.process_natural_language(
            query, 
            session_id=session_id
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error',
            'original_query': query
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'engine_available': engine is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'engine_initialized': engine is not None,
        'llm_enabled': engine.use_llm if engine else False,
        'execution_mode': engine.execution_mode.value if engine else 'unknown',
        'atlan_connected': engine.atlan_client is not None if engine else False
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Atlan AI Control Plane Web Server")
    print("="*60)
    print(f"✅ Server running at: http://localhost:5000")
    print(f"✅ Engine status: {'Initialized' if engine else 'Not Available'}")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
