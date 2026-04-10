#!/bin/bash
# Real-Time Control Plane Setup Script

set -e

echo "🚀 Setting up Real-Time Governance Control Plane..."
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.8"

if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
    echo "❌ Python 3.8+ required. Current: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install spaCy model
echo "🧠 Installing spaCy language model..."
python -m spacy download en_core_web_lg

# Create config if doesn't exist
if [ ! -f "config.yaml" ]; then
    echo "⚙️  Creating config.yaml..."
    python control_plane.py --create-config
    echo ""
    echo "⚠️  IMPORTANT: Edit config.yaml with your platform credentials"
fi

# Create directories
mkdir -p logs
mkdir -p exports

# Test imports
echo "🧪 Testing dependencies..."
python3 -c "
import snowflake.connector
from presidio_analyzer import AnalyzerEngine
import yaml
print('✅ All dependencies working')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config.yaml with your platform credentials"
echo "  2. Test connection: python control_plane.py --test-connection"
echo "  3. Run scenarios: python control_plane.py --run-all"
echo ""
echo "Documentation: See README.md"