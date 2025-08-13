#!/usr/bin/env python3
"""
Flexible Excel file examination with command-line arguments
"""

import pandas as pd
import sys
import argparse
from pathlib import Path

def examine_file(file_path, detailed=False):
    """Examine a single Excel file"""
    try:
        print(f"\n{'='*60}")
        print(f"Examining: {Path(file_path).name}")
        print('='*60)
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Basic info
        print(f"\n📊 Basic Information:")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Column information
        print(f"\n📋 Columns ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            dtype = str(df[col].dtype)
            non_null = df[col].notna().sum()
            null_pct = (df[col].isna().sum() / len(df)) * 100
            print(f"  {i:2}. {col:<30} {dtype:<10} ({non_null:,} non-null, {null_pct:.1f}% missing)")
        
        # Data types summary
        print(f"\n📈 Data Types Summary:")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {str(dtype):<15}: {count} columns")
        
        if detailed:
            # Numeric columns statistics
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                print(f"\n📊 Numeric Column Statistics:")
                for col in numeric_cols:
                    if df[col].notna().any():
                        print(f"\n  {col}:")
                        print(f"    Min: {df[col].min():.2f}" if pd.api.types.is_float_dtype(df[col]) else f"    Min: {df[col].min()}")
                        print(f"    Max: {df[col].max():.2f}" if pd.api.types.is_float_dtype(df[col]) else f"    Max: {df[col].max()}")
                        print(f"    Mean: {df[col].mean():.2f}")
                        print(f"    Median: {df[col].median():.2f}")
            
            # Sample data
            print(f"\n📖 Sample Data (first 3 rows):")
            print("-" * 60)
            for idx, row in df.head(3).iterrows():
                print(f"\nRow {idx + 1}:")
                for col in ['Title', 'Author', 'price', 'reviewAverage', 'genre'] if 'genre' in df.columns else ['Title', 'Author', 'price', 'reviewAverage']:
                    if col in df.columns:
                        value = row[col]
                        if pd.notna(value):
                            if isinstance(value, str) and len(value) > 50:
                                value = value[:50] + "..."
                            print(f"  {col}: {value}")
        
        # Missing data summary
        missing_data = df.isnull().sum()
        if missing_data.any():
            print(f"\n⚠️  Columns with Missing Data:")
            for col, count in missing_data[missing_data > 0].items():
                pct = (count / len(df)) * 100
                print(f"  {col}: {count} ({pct:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error examining file: {e}")
        return False

def examine_all_files(data_dir, detailed=False):
    """Examine all Excel files in directory"""
    excel_files = list(Path(data_dir).glob('*.xlsx'))
    
    if not excel_files:
        print(f"No Excel files found in {data_dir}")
        return
    
    print(f"Found {len(excel_files)} Excel files")
    
    summary = []
    for file_path in sorted(excel_files):
        if examine_file(file_path, detailed):
            # Collect summary info
            df = pd.read_excel(file_path)
            genre = file_path.stem.replace('20250811_', '').replace('_raw_data', '')
            summary.append({
                'Genre': genre,
                'Rows': len(df),
                'Columns': len(df.columns),
                'File': file_path.name
            })
    
    # Print summary table
    if summary:
        print(f"\n{'='*60}")
        print("SUMMARY OF ALL FILES")
        print('='*60)
        print(f"\n{'Genre':<25} {'Rows':<10} {'Columns':<10} {'File'}")
        print("-" * 70)
        total_rows = 0
        for s in summary:
            print(f"{s['Genre']:<25} {s['Rows']:<10} {s['Columns']:<10} {s['File']}")
            total_rows += s['Rows']
        print("-" * 70)
        print(f"{'TOTAL':<25} {total_rows:<10}")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description='Examine Excel files for book data')
    parser.add_argument('file', nargs='?', help='Specific Excel file to examine')
    parser.add_argument('--all', action='store_true', help='Examine all Excel files in data_raw')
    parser.add_argument('--detailed', '-d', action='store_true', help='Show detailed statistics')
    # Default to data_raw relative to script location
    script_dir = Path(__file__).parent
    default_data_dir = script_dir.parent / 'data_raw'
    parser.add_argument('--dir', default=str(default_data_dir), help='Directory containing Excel files')
    
    args = parser.parse_args()
    
    if args.all:
        examine_all_files(args.dir, args.detailed)
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            # Try in data directory
            file_path = Path(args.dir) / args.file
        
        if file_path.exists():
            examine_file(file_path, args.detailed)
        else:
            print(f"File not found: {args.file}")
            sys.exit(1)
    else:
        # Default: examine first file found
        excel_files = list(Path(args.dir).glob('*.xlsx'))
        if excel_files:
            print("No file specified. Examining first file found...")
            examine_file(excel_files[0], args.detailed)
        else:
            print(f"No Excel files found in {args.dir}")
            print("\nUsage:")
            print("  python examine_excel.py [file]           # Examine specific file")
            print("  python examine_excel.py --all            # Examine all files")
            print("  python examine_excel.py --all --detailed # Detailed examination")
            sys.exit(1)

if __name__ == "__main__":
    main()