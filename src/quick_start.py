#!/usr/bin/env python3
"""
Quick Start Script - Governance Actions Dashboard
Starts Flask API and Streamlit in a single command
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PYTHON_EXE = sys.executable

print("\n" + "="*70)
print("⚡ GOVERNANCE ACTIONS DASHBOARD")
print("   Starting Atlan Actions Engine...\n")

# Start Flask API
print("[1/2] Starting Flask API Server...")
flask_cmd = [PYTHON_EXE, str(SCRIPT_DIR / "atlan_api_server.py")]
flask_process = subprocess.Popen(
    flask_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=str(SCRIPT_DIR)
)
time.sleep(2)
print("      ✓ Flask API running on http://localhost:5000")

# Start Streamlit
print("\n[2/2] Starting Streamlit Dashboard...")
streamlit_cmd = [
    PYTHON_EXE, "-m", "streamlit", "run",
    str(SCRIPT_DIR / "streamlit_app.py"),
    "--server.port=8501",
    "--server.address=0.0.0.0"
]
print("      ✓ Streamlit will start momentarily...")
print("="*70)
print("\n📊 DASHBOARD READY: http://localhost:8501\n")

try:
    # This blocks until Streamlit exits
    subprocess.run(streamlit_cmd, cwd=str(SCRIPT_DIR))
except KeyboardInterrupt:
    print("\n\n🛑 Shutting down...")
    flask_process.terminate()
    print("✓ Services stopped")
