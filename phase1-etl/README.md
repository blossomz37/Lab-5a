# Phase 1: ETL Pipeline

Extract, Transform, Load pipeline that processes Excel book data into a DuckDB database.

## 🎯 Objectives

Learn data engineering fundamentals:
- ETL pipeline design and implementation
- Data validation and quality assurance  
- Database schema design and optimization
- Error handling and logging
- Virtual environment management

## 📊 Input Data

**Source**: 14 Excel files in `../data/raw/`
**Format**: `20250811_{genre}_raw_data.xlsx`
**Total Records**: ~1,400 books
**Genres**: 14 different book genres (100 books each)

## 🚀 Quick Start

```bash
# Navigate to phase1-etl directory
cd phase1-etl

# Set up environment (first time only)
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh

# Run the ETL pipeline
./scripts/run_processing.sh
```

## 📁 Directory Structure

```
phase1-etl/
├── README.md              # This file
├── scripts/               # Processing scripts
│   ├── setup_environment.sh   # Environment setup
│   ├── check_environment.py   # Environment validation
│   ├── create_duckdb.py       # Main ETL script (enhanced)
│   ├── create_duckdb_basic.py # Simple ETL (for learning)
│   ├── verify_duckdb.py       # Basic verification
│   ├── verify_duckdb_enhanced.py # Advanced verification
│   ├── examine_excel.py       # Excel file analysis
│   └── run_processing.sh      # Full pipeline orchestration
└── docs/                  # Documentation
    ├── SETUP_GUIDE.md     # Detailed setup instructions
    └── STUDENT_GUIDE.md   # Lab exercises and learning guide
```

## 🔧 Scripts Overview

### Core Scripts
- **`create_duckdb.py`**: Main ETL script with logging, validation, and indexes
- **`verify_duckdb.py`**: Database validation and statistics  
- **`run_processing.sh`**: Full pipeline with error handling

### Setup & Utilities
- **`setup_environment.sh`**: One-command environment setup
- **`check_environment.py`**: Validates environment before processing
- **`examine_excel.py`**: Flexible Excel file analysis tool

### Educational Versions
- **`create_duckdb_basic.py`**: Simplified ETL for learning concepts
- **`verify_duckdb_enhanced.py`**: Advanced verification with data quality checks

## 💻 Commands Reference

### Environment Setup
```bash
# Complete environment setup
./scripts/setup_environment.sh

# Check if environment is ready
python3 scripts/check_environment.py
```

### ETL Processing
```bash
# Full pipeline (recommended)
./scripts/run_processing.sh

# Individual steps
python3 scripts/create_duckdb.py      # Create database
python3 scripts/verify_duckdb.py     # Basic verification
python3 scripts/verify_duckdb_enhanced.py  # Advanced verification
```

### Data Exploration
```bash
# Examine Excel files
python3 scripts/examine_excel.py --all           # All files summary
python3 scripts/examine_excel.py --all -d       # Detailed analysis
python3 scripts/examine_excel.py filename.xlsx  # Specific file
```

## 🗄️ Output Database

**Location**: `../data/processed/books_data.duckdb`
**Format**: DuckDB database file
**Tables**: 
- `books` - Main table with all book data
- `genre_summary` - View with genre statistics

**Schema**: 27+ columns including:
- Core: Title, Author, ASIN, Genre
- Metrics: Price, Rating, Review Count
- Metadata: Release Date, Series, Publisher
- Analysis: Topics, POV, Romance/Supernatural flags

## 🔍 Data Quality Checks

The enhanced scripts perform comprehensive validation:
- ✅ Missing value detection
- ✅ Duplicate record identification  
- ✅ Invalid price/rating validation
- ✅ Data type consistency checks
- ✅ Column completeness verification

## 📈 Features

### Enhanced ETL (`create_duckdb.py`)
- **Logging**: Comprehensive processing logs
- **Validation**: Data quality checks at each step
- **Indexing**: Database indexes for performance
- **Views**: Pre-built analytical views
- **Error Handling**: Graceful failure recovery

### Verification Tools
- **Basic**: Row counts, column info, sample data
- **Enhanced**: Data quality report, statistics, sample queries

### Environment Management
- **Virtual Environment**: Isolated Python dependencies
- **Dependency Checking**: Validates required packages
- **Cross-Platform**: Works on macOS, Linux, Windows

## 🚨 Common Issues & Solutions

### "Virtual environment not found"
```bash
./scripts/setup_environment.sh  # Creates and configures venv
```

### "No Excel files found"
```bash
# Ensure you're in the project root and Excel files exist
ls ../data/raw/*.xlsx
```

### "Import errors" 
```bash
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt  # Install dependencies
```

### "Database creation failed"
```bash
python3 scripts/check_environment.py  # Diagnose issues
```

## 🎓 Learning Exercises

1. **Compare ETL approaches**: Run both `create_duckdb_basic.py` and `create_duckdb.py`
2. **Data quality analysis**: Review output from `verify_duckdb_enhanced.py`
3. **Performance testing**: Time different script versions
4. **Custom analysis**: Modify scripts to answer specific questions
5. **Error simulation**: Rename Excel files to test error handling

## ➡️ Next Steps

Once ETL is complete:
1. Database will be created in `../data/processed/books_data.duckdb`
2. Proceed to [Phase 2: Web Application](../phase2-webapp/README.md)
3. Launch the interactive dashboard to explore your data!

## 📚 Additional Resources

- [Student Lab Guide](docs/STUDENT_GUIDE.md) - Step-by-step exercises
- [Setup Instructions](docs/SETUP_GUIDE.md) - Detailed environment setup
- [DuckDB Documentation](https://duckdb.org/docs/) - Database reference