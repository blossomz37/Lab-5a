# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a book data processing pipeline that converts Excel files containing book metadata from various genres into a unified DuckDB database. The project processes approximately 1,400 books across 14 different genres.

## Key Commands

### Environment Setup (First Time)
```bash
# Set up virtual environment and install dependencies
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh

# Check environment is ready
python3 scripts/check_environment.py
```

### Full Processing Pipeline
```bash
# Run complete Excel to DuckDB conversion (with venv checks)
chmod +x scripts/run_processing.sh
./scripts/run_processing.sh
```

### Individual Operations
```bash
# Always activate venv first
source venv/bin/activate

# Create/recreate database from Excel files
python3 scripts/create_duckdb.py

# Verify database contents and structure (basic)
python3 scripts/verify_duckdb.py

# Enhanced verification with data quality checks
python3 scripts/verify_duckdb_enhanced.py

# Examine Excel files
python3 scripts/examine_excel.py --all          # All files
python3 scripts/examine_excel.py --all -d      # Detailed analysis
python3 scripts/examine_excel.py filename.xlsx # Specific file
```

## Architecture

### Data Flow
1. **Input**: 14 Excel files in `data_raw/` directory (format: `20250811_{genre}_raw_data.xlsx`)
2. **Processing**: Python scripts read Excel files using pandas, add metadata (genre, source_file, ingested_date)
3. **Output**: Single DuckDB database `books_data.duckdb` with unified schema

### Database Schema
The `books` table contains 23+ columns including:
- Core book data: asin, title, author, price, rating, review_count, rank_overall
- Metadata: genre, source_file, ingested_date
- Extended info: blurb_text, cover_url, product_url, topic_tags, subcategories
- Analysis fields: blurb_keyphrases, estimated_pov, has_supernatural, has_romance

### Key Scripts
- `setup_environment.sh`: One-time setup for virtual environment and dependencies
- `check_environment.py`: Validates environment setup before processing
- `create_duckdb.py`: Main ETL script with logging, validation, and indexes
- `create_duckdb_basic.py`: Simpler version for educational comparison
- `verify_duckdb.py`: Basic database validation and statistics
- `verify_duckdb_enhanced.py`: Comprehensive data quality checks and reporting
- `examine_excel.py`: Flexible Excel file analysis with command-line options
- `run_processing.sh`: Full-featured orchestration script with error handling

## Dependencies

Required Python packages:
- pandas (for Excel file reading)
- duckdb (for database operations)
- openpyxl (pandas dependency for Excel support)

## Important Notes

- All scripts use relative paths for portability across systems
- Virtual environment usage is enforced for proper dependency management
- Database is recreated on each run (DROP TABLE IF EXISTS pattern)
- Scripts include comprehensive error handling and environment validation
- Genre names are extracted from Excel filenames
- All data files use the date prefix `20250811`
- Enhanced scripts provide data quality checks and identify issues like duplicate ASINs