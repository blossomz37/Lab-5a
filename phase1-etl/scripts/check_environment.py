#!/usr/bin/env python3
"""
Environment checker for book data processing scripts
Ensures virtual environment and dependencies are properly set up
"""

import sys
import os
from pathlib import Path
import subprocess

def check_venv():
    """Check if running in virtual environment"""
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print("⚠️  WARNING: Not running in a virtual environment!")
        print("\nTo set up and activate the virtual environment:")
        print("  1. Create venv:     python3 -m venv venv")
        print("  2. Activate venv:   source venv/bin/activate")
        print("  3. Install deps:    pip install -r requirements.txt")
        print("\nThen run this script again.")
        return False
    
    print("✅ Running in virtual environment")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = {
        'pandas': 'pandas',
        'duckdb': 'duckdb',
        'openpyxl': 'openpyxl'  # Required for Excel file reading
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            missing.append(package_name)
            print(f"❌ {package_name} is NOT installed")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nTo install missing packages:")
        print(f"  pip install {' '.join(missing)}")
        print("\nOr install all requirements:")
        print("  pip install -r requirements.txt")
        return False
    
    return True

def check_data_files():
    """Check if Excel data files exist"""
    script_dir = Path(__file__).parent
    phase_dir = script_dir.parent
    project_dir = phase_dir.parent
    data_dir = project_dir / 'data' / 'raw'
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return False
    
    excel_files = list(data_dir.glob('*.xlsx'))
    if not excel_files:
        print(f"❌ No Excel files found in {data_dir}")
        return False
    
    print(f"✅ Found {len(excel_files)} Excel files in data_raw/")
    return True

def main():
    """Main environment check"""
    print("="*50)
    print("ENVIRONMENT CHECK FOR BOOK DATA PROCESSING")
    print("="*50)
    print()
    
    all_good = True
    
    # Check virtual environment
    print("Checking virtual environment...")
    if not check_venv():
        all_good = False
    print()
    
    # Check dependencies (only if in venv)
    if all_good:
        print("Checking dependencies...")
        if not check_dependencies():
            all_good = False
        print()
    
    # Check data files
    print("Checking data files...")
    if not check_data_files():
        all_good = False
    print()
    
    # Final status
    print("="*50)
    if all_good:
        print("✅ ENVIRONMENT CHECK PASSED - Ready to process data!")
        print("\nYou can now run:")
        print("  python3 scripts/create_duckdb.py")
        print("  python3 scripts/verify_duckdb.py")
        print("\nOr use the automated script:")
        print("  ./scripts/run_processing.sh")
    else:
        print("❌ ENVIRONMENT CHECK FAILED - Please fix issues above")
        sys.exit(1)
    print("="*50)

if __name__ == "__main__":
    main()