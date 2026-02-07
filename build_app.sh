#!/bin/bash

# Tax Helper - macOS App Builder
# This script builds Tax Helper.app using PyInstaller

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}         Tax Helper - macOS App Builder${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check Python
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"
echo ""

# Check/Install PyInstaller
echo -e "${YELLOW}Checking PyInstaller...${NC}"
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}Installing PyInstaller...${NC}"
    python3 -m pip install pyinstaller
fi
echo -e "${GREEN}✓ PyInstaller ready${NC}"
echo ""

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build dist "Tax Helper.app"
echo -e "${GREEN}✓ Clean${NC}"
echo ""

# Build the app
echo -e "${YELLOW}Building Tax Helper.app...${NC}"
echo -e "${BLUE}This may take several minutes...${NC}"
echo ""

python3 -m PyInstaller TaxHelper.spec --noconfirm

if [ -d "dist/Tax Helper.app" ]; then
    echo ""
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo ""

    # Move to current directory
    mv "dist/Tax Helper.app" .

    # Show size
    SIZE=$(du -sh "Tax Helper.app" | cut -f1)
    echo -e "${GREEN}Tax Helper.app created (${SIZE})${NC}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}SUCCESS!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Your application is ready!"
    echo ""
    echo "Location: $DIR/Tax Helper.app"
    echo ""
    echo "Next steps:"
    echo "  1. Double-click 'Tax Helper.app' to test it"
    echo "  2. Drag it to your Applications folder"
    echo "  3. Launch from Applications or Spotlight (Cmd+Space)"
    echo ""
    echo "Optional cleanup:"
    echo "  rm -rf build dist"
    echo ""
else
    echo -e "${RED}✗ Build failed${NC}"
    echo "Check the error messages above"
    exit 1
fi
