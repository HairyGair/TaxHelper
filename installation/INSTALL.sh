#!/bin/bash
# Tax Helper - Installation Script for Mac/Linux

echo "💷 Tax Helper - Installation"
echo "=============================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed"
    echo "Please install pip3"
    exit 1
fi

echo "✓ pip3 found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 To run Tax Helper:"
echo "   ./RUN.sh"
echo ""
echo "   OR"
echo ""
echo "   python3 -m streamlit run app.py"
echo ""
