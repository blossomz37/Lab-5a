#!/bin/bash

# Setup script for book data processing environment
# This script creates venv and installs all dependencies

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================================"
echo "ENVIRONMENT SETUP FOR BOOK DATA PROCESSING"
echo "================================================"
echo ""

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Found Python ${PYTHON_VERSION}${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✅ pip upgraded${NC}"

# Install requirements
echo ""
if [ -f "requirements.txt" ]; then
    echo "Installing requirements from requirements.txt..."
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✅ All requirements installed${NC}"
else
    echo "No requirements.txt found, installing packages individually..."
    pip install pandas duckdb openpyxl --quiet
    echo -e "${GREEN}✅ Required packages installed${NC}"
    
    # Create requirements.txt
    echo "Creating requirements.txt..."
    pip freeze | grep -E "pandas|duckdb|openpyxl" > requirements.txt
    echo -e "${GREEN}✅ requirements.txt created${NC}"
fi

# Check data files
echo ""
echo "Checking data files..."
if [ -d "data_raw" ]; then
    EXCEL_COUNT=$(find data_raw -name "*.xlsx" 2>/dev/null | wc -l)
    if [ "$EXCEL_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Found $EXCEL_COUNT Excel files in data_raw/${NC}"
    else
        echo -e "${YELLOW}⚠️  No Excel files found in data_raw/${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  data_raw directory not found${NC}"
fi

# Final instructions
echo ""
echo "================================================"
echo -e "${GREEN}SETUP COMPLETE!${NC}"
echo "================================================"
echo ""
echo "Your environment is ready. You can now:"
echo ""
echo "1. Run the environment check:"
echo "   python3 scripts/check_environment.py"
echo ""
echo "2. Process the data:"
echo "   python3 scripts/create_duckdb.py"
echo "   python3 scripts/verify_duckdb.py"
echo ""
echo "3. Or use the automated processing script:"
echo "   ./scripts/run_processing.sh"
echo ""
echo "Note: Virtual environment is currently activated."
echo "To deactivate: deactivate"
echo "To reactivate: source venv/bin/activate"
echo ""