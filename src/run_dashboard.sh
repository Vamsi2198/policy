#!/bin/bash

# Governance Actions Dashboard - Linux/Mac Launcher
# This script starts the complete Governance Actions Dashboard
# (Flask API + Streamlit Frontend)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║   ⚡ GOVERNANCE ACTIONS DASHBOARD                         ║"
echo "║      Launching Application...                             ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ using your package manager"
    exit 1
fi

echo -e "${GREEN}[INFO] Python installation found${NC}"
python3 --version
echo

# Check if we're in the right directory
if [ ! -f "atlan_api_server.py" ]; then
    echo -e "${RED}[ERROR] atlan_api_server.py not found${NC}"
    echo "Please run this script from the src/ directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo -e "${GREEN}[INFO] Starting Governance Actions Dashboard...${NC}"
echo

# Make the Python script executable
chmod +x run_governance_dashboard.py

# Run the startup script
python3 run_governance_dashboard.py

echo
echo -e "${GREEN}[INFO] Dashboard stopped${NC}"
