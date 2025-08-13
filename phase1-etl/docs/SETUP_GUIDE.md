# Setup Guide for Book Data Processing Lab

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/blossomz37/Lab-5b-ffa.git
cd Lab-5b-ffa

# 2. Run the setup script
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh

# 3. Process the data
./scripts/run_processing.sh
```

## Detailed Setup Instructions

### Step 1: Prerequisites

Ensure you have Python 3.8 or higher installed:
```bash
python3 --version
```

### Step 2: Create Virtual Environment

**Always use a virtual environment for Python projects!**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
# venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt when activated.

### Step 3: Install Dependencies

```bash
# With virtual environment activated
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install pandas duckdb openpyxl
```

### Step 4: Verify Setup

Run the environment checker:
```bash
python3 scripts/check_environment.py
```

This will verify:
- ✅ Virtual environment is active
- ✅ All required packages are installed
- ✅ Data files are present

### Step 5: Process Data

Once setup is complete:
```bash
# Run the full pipeline
./scripts/run_processing.sh

# Or run scripts individually
python3 scripts/create_duckdb.py
python3 scripts/verify_duckdb.py
```

## Common Issues & Solutions

### "Not running in virtual environment"
**Solution:** Activate your virtual environment
```bash
source venv/bin/activate
```

### "No module named pandas/duckdb"
**Solution:** Install missing packages
```bash
pip install -r requirements.txt
```

### "Permission denied" when running shell scripts
**Solution:** Make scripts executable
```bash
chmod +x scripts/*.sh
```

### "No Excel files found"
**Solution:** Ensure you're in the project root directory and data_raw/ contains Excel files

## Working with Virtual Environments

### Why use virtual environments?
- **Isolation**: Keeps project dependencies separate
- **Reproducibility**: Ensures everyone uses the same package versions
- **Clean system**: Doesn't pollute your global Python installation

### Virtual Environment Commands
```bash
# Create new venv
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate (when done working)
deactivate

# Check if venv is active
which python3  # Should show path to venv/bin/python3

# List installed packages
pip list

# Save current packages to requirements
pip freeze > requirements.txt
```

## Project Structure After Setup
```
Lab-5b-ffa/
├── venv/                  # Virtual environment (not in git)
├── data_raw/              # Excel source files
├── scripts/               # Processing scripts
│   ├── setup_environment.sh    # Environment setup
│   ├── check_environment.py    # Environment checker
│   ├── create_duckdb.py       # Main processing
│   ├── verify_duckdb.py       # Database verification
│   └── run_processing.sh      # Automated pipeline
├── requirements.txt       # Python dependencies
└── books_data.duckdb     # Output database (after processing)
```

## Tips for Development

1. **Always activate venv before working**:
   ```bash
   cd Lab-5b-ffa
   source venv/bin/activate
   ```

2. **Check environment before running scripts**:
   ```bash
   python3 scripts/check_environment.py
   ```

3. **Use the automated setup for new environments**:
   ```bash
   ./scripts/setup_environment.sh
   ```

4. **Keep requirements.txt updated**:
   ```bash
   pip freeze > requirements.txt
   ```

## Next Steps

Once setup is complete, refer to:
- `STUDENT_GUIDE.md` for lab exercises
- `README.md` for project overview
- `sample_queries.sql` for example database queries (generated after processing)