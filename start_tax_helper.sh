#!/bin/bash

# UK Tax Helper Launcher
# Professional launcher script for Tax Helper application

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}           UK Self Assessment Tax Helper${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

# Check if Streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo -e "${RED}ERROR: Streamlit is not installed${NC}"
    echo "Installing required dependencies..."
    python3 -m pip install -r "$DIR/requirements.txt"
fi

# Change to app directory
cd "$DIR" || exit 1

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo -e "${RED}ERROR: app.py not found in $DIR${NC}"
    exit 1
fi

# Launch the application
echo -e "${GREEN}Starting Tax Helper...${NC}"
echo ""
echo "The app will open in your default browser."
echo "Press Ctrl+C to stop the server when you're done."
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Run the app
python3 -m streamlit run app.py

# Cleanup message
echo ""
echo -e "${GREEN}Tax Helper has been closed. Thank you for using the app!${NC}"
