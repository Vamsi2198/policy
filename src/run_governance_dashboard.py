#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Governance Actions - Complete Startup Script
=============================================

Starts both the Flask API server and Streamlit frontend
in a single unified application.

Usage:
    python run_governance_dashboard.py
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

# Get script directory
SCRIPT_DIR = Path(__file__).parent.absolute()

# Use Python executable from current environment
PYTHON_EXE = sys.executable

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Print fancy header"""
    print(f"""{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ⚡ GOVERNANCE ACTIONS DASHBOARD                            ║
║      Natural Language Governance Automation                  ║
║                                                               ║
║   Atlan Actions Engine - Complete Solution                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.ENDC}""")

def print_status(message: str, status: str = "INFO"):
    """Print status message"""
    status_colors = {
        "INFO": Colors.CYAN,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "DEBUG": Colors.BLUE
    }
    color = status_colors.get(status, Colors.CYAN)
    print(f"{color}[{status:7s}]{Colors.ENDC} {message}")

def check_python_packages():
    """Check if required packages are installed"""
    print_status("Checking Python packages...", "INFO")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'streamlit': 'Streamlit',
        'requests': 'Requests',
        'pandas': 'Pandas',
        'plotly': 'Plotly'
    }
    
    missing = []
    for import_name, display_name in required_packages.items():
        try:
            __import__(import_name)
            print_status(f"✓ {display_name} installed", "SUCCESS")
        except ImportError:
            print_status(f"✗ {display_name} missing", "WARNING")
            missing.append(import_name)
    
    if missing:
        print_status(f"Install missing packages: pip install -r requirements_streamlit.txt", "ERROR")
        return False
    
    return True

def start_flask_server():
    """Start Flask API server in a separate thread"""
    print_status("Starting Flask API server...", "INFO")
    
    try:
        # Start Flask server
        cmd = [
            sys.executable,
            str(SCRIPT_DIR / "atlan_api_server.py")
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        print_status("Flask server process started (PID: {})".format(process.pid), "SUCCESS")
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if running
        if process.poll() is None:
            print_status("✓ Flask API running on http://0.0.0.0:5000", "SUCCESS")
            return process
        else:
            print_status("Flask server failed to start", "ERROR")
            return None
    
    except Exception as e:
        print_status(f"Failed to start Flask server: {e}", "ERROR")
        return None

def start_streamlit():
    """Start Streamlit frontend"""
    print_status("Starting Streamlit frontend...", "INFO")
    
    try:
        streamlit_script = SCRIPT_DIR / "streamlit_app.py"
        
        if not streamlit_script.exists():
            print_status(f"Streamlit app not found at {streamlit_script}", "ERROR")
            return False
        
        cmd = [
            sys.executable,
            "-m", "streamlit",
            "run",
            str(streamlit_script),
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--logger.level=info",
            "--theme.base=dark",
            "--theme.primaryColor=#667eea"
        ]
        
        print_status("Launching Streamlit...", "INFO")
        
        # Start Streamlit (blocks until closed)
        subprocess.run(cmd, cwd=SCRIPT_DIR)
        
    except Exception as e:
        print_status(f"Failed to start Streamlit: {e}", "ERROR")

def main():
    """Main startup logic"""
    
    print_header()
    
    print_status("Governance Actions Dashboard Startup", "INFO")
    print(f"{Colors.BOLD}Location: {SCRIPT_DIR}{Colors.ENDC}\n")
    
    # Check Python version
    print_status(f"Python {sys.version.split()[0]}", "DEBUG")
    
    # Check packages
    if not check_python_packages():
        print_status("\nInstalling required packages...", "WARNING")
        req_file = str(SCRIPT_DIR / "requirements_streamlit.txt")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=False)
    
    print()
    
    # Start Flask server
    flask_process = start_flask_server()
    
    if flask_process is None:
        print_status("Failed to start Flask server. Exiting.", "ERROR")
        sys.exit(1)
    
    print()
    
    try:
        print_status("=" * 60, "INFO")
        print_status("🎉 GOVERNANCE ACTIONS DASHBOARD IS READY!", "SUCCESS")
        print_status("=" * 60, "INFO")
        print()
        
        print_status("📊 SERVICES RUNNING:", "INFO")
        print_status("  • Flask API Server: http://localhost:5000", "SUCCESS")
        print_status("  • Streamlit Frontend: http://localhost:8501", "SUCCESS")
        print()
        
        print_status("📚 QUICK START:", "INFO")
        print_status("  1. Open browser to: http://localhost:8501", "DEBUG")
        print_status("  2. Enter a governance command, e.g.:", "DEBUG")
        print_status("     'mask salary in employee table for analyst role'", "DEBUG")
        print_status("  3. Click 'Execute Command'", "DEBUG")
        print_status("  4. Monitor the 6-phase workflow", "DEBUG")
        print()
        
        print_status("🛠️  AVAILABLE ENDPOINTS:", "INFO")
        print_status("  • GET  http://localhost:5000/api/health", "DEBUG")
        print_status("  • POST http://localhost:5000/api/process", "DEBUG")
        print_status("  • GET  http://localhost:5000/api/metadata", "DEBUG")
        print_status("  • GET  http://localhost:5000/api/audit-logs", "DEBUG")
        print()
        
        print_status("Press Ctrl+C to stop all services", "WARNING")
        print_status("=" * 60, "INFO")
        print()
        
        # Open browser
        time.sleep(2)
        try:
            print_status("Opening browser...", "INFO")
            webbrowser.open("http://localhost:8501")
        except:
            print_status("Could not open browser automatically", "WARNING")
        
        # Start Streamlit (blocks)
        start_streamlit()
        
    except KeyboardInterrupt:
        print()
        print_status("Shutting down services...", "WARNING")
        
        if flask_process and flask_process.poll() is None:
            print_status("Stopping Flask server...", "INFO")
            flask_process.terminate()
            try:
                flask_process.wait(timeout=5)
            except:
                flask_process.kill()
        
        print_status("All services stopped", "SUCCESS")
        sys.exit(0)
    
    except Exception as e:
        print_status(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
