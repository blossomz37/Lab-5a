#!/bin/bash

# Enhanced processing script with error handling and options

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
VENV_PATH="$PROJECT_DIR/venv"
DB_PATH="$PROJECT_DIR/books_data.duckdb"
LOG_FILE="$PROJECT_DIR/processing.log"

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"
    
    # Check virtual environment
    if [ ! -d "$VENV_PATH" ]; then
        print_warning "Virtual environment not found. Creating..."
        python3 -m venv "$VENV_PATH"
        source "$VENV_PATH/bin/activate"
        pip install -q pandas duckdb openpyxl
        print_success "Virtual environment created"
    else
        print_success "Virtual environment found"
    fi
    
    # Check data directory
    if [ ! -d "$PROJECT_DIR/data_raw" ]; then
        print_error "Data directory not found: $PROJECT_DIR/data_raw"
        exit 1
    fi
    
    # Count Excel files
    EXCEL_COUNT=$(find "$PROJECT_DIR/data_raw" -name "*.xlsx" | wc -l)
    if [ "$EXCEL_COUNT" -eq 0 ]; then
        print_error "No Excel files found in data_raw directory"
        exit 1
    fi
    print_success "Found $EXCEL_COUNT Excel files"
}

run_processing() {
    print_header "Processing Excel Files to DuckDB"
    
    cd "$PROJECT_DIR"
    source "$VENV_PATH/bin/activate"
    
    # Start logging
    echo "Processing started at $(date)" > "$LOG_FILE"
    
    # Choose which script to run based on argument
    if [ "$1" == "--improved" ]; then
        if [ -f "scripts/create_duckdb_improved.py" ]; then
            print_success "Using improved processing script"
            python3 scripts/create_duckdb_improved.py 2>&1 | tee -a "$LOG_FILE"
        else
            print_warning "Improved script not found, using standard script"
            python3 scripts/create_duckdb.py 2>&1 | tee -a "$LOG_FILE"
        fi
    else
        python3 scripts/create_duckdb.py 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # Check if database was created
    if [ -f "$DB_PATH" ]; then
        DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
        print_success "Database created successfully (Size: $DB_SIZE)"
    else
        print_error "Database creation failed"
        exit 1
    fi
}

run_verification() {
    print_header "Verifying Database"
    
    source "$VENV_PATH/bin/activate"
    
    # Choose which verification script to run
    if [ "$1" == "--enhanced" ]; then
        if [ -f "scripts/verify_duckdb_enhanced.py" ]; then
            print_success "Using enhanced verification"
            python3 scripts/verify_duckdb_enhanced.py 2>&1 | tee -a "$LOG_FILE"
        else
            print_warning "Enhanced verification not found, using standard"
            python3 scripts/verify_duckdb.py 2>&1 | tee -a "$LOG_FILE"
        fi
    else
        python3 scripts/verify_duckdb.py 2>&1 | tee -a "$LOG_FILE"
    fi
}

examine_files() {
    print_header "Examining Excel Files"
    
    source "$VENV_PATH/bin/activate"
    
    if [ -f "scripts/examine_excel_flexible.py" ]; then
        python3 scripts/examine_excel_flexible.py --all
    else
        python3 scripts/examine_excel.py
    fi
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help         Show this help message"
    echo "  --improved     Use improved processing scripts"
    echo "  --enhanced     Use enhanced verification"
    echo "  --examine      Examine Excel files before processing"
    echo "  --clean        Remove existing database before processing"
    echo "  --verbose      Show detailed output"
    echo ""
    echo "Examples:"
    echo "  $0                    # Standard processing"
    echo "  $0 --improved         # Use improved scripts"
    echo "  $0 --examine --clean  # Examine files and clean before processing"
}

# Main script
main() {
    # Parse arguments
    EXAMINE=false
    CLEAN=false
    IMPROVED=false
    ENHANCED=false
    
    for arg in "$@"; do
        case $arg in
            --help)
                show_usage
                exit 0
                ;;
            --examine)
                EXAMINE=true
                ;;
            --clean)
                CLEAN=true
                ;;
            --improved)
                IMPROVED=true
                ;;
            --enhanced)
                ENHANCED=true
                ;;
            --verbose)
                set -x
                ;;
            *)
                print_warning "Unknown option: $arg"
                ;;
        esac
    done
    
    # Print start time
    print_header "Book Data Processing Pipeline"
    echo "Started at: $(date)"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Examine files if requested
    if [ "$EXAMINE" = true ]; then
        examine_files
    fi
    
    # Clean existing database if requested
    if [ "$CLEAN" = true ] && [ -f "$DB_PATH" ]; then
        print_warning "Removing existing database"
        rm "$DB_PATH"
        [ -f "${DB_PATH}.wal" ] && rm "${DB_PATH}.wal"
    fi
    
    # Run processing
    if [ "$IMPROVED" = true ]; then
        run_processing --improved
    else
        run_processing
    fi
    
    # Run verification
    echo ""
    if [ "$ENHANCED" = true ]; then
        run_verification --enhanced
    else
        run_verification
    fi
    
    # Summary
    echo ""
    print_header "Processing Complete"
    print_success "Database: $DB_PATH"
    print_success "Log file: $LOG_FILE"
    echo "Finished at: $(date)"
    
    # Deactivate virtual environment
    deactivate 2>/dev/null || true
}

# Run main function
main "$@"