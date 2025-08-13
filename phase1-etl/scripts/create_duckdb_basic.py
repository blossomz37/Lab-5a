#!/usr/bin/env python3
"""
Process all Excel files to DuckDB
Unified approach to convert all genre files to structured database
"""

import sys
import os
from pathlib import Path

# Check if running in virtual environment
if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
    print("⚠️  WARNING: Not running in virtual environment!")
    print("Please activate venv first: source venv/bin/activate")
    print("Or run: python3 scripts/check_environment.py for setup help")
    sys.exit(1)

try:
    import pandas as pd
    import duckdb
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

import glob

def main():
    # Base paths (relative to script location)
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data_raw'
    db_path = project_dir / 'books_data.duckdb'
    
    # Connect to DuckDB
    conn = duckdb.connect(str(db_path))
    
    # Get all Excel files
    excel_files = list(data_dir.glob('*.xlsx'))
    
    print(f"Found {len(excel_files)} Excel files")
    
    # Process each file
    all_data = []
    
    for file_path in excel_files:
        try:
            # Extract genre from filename
            filename = file_path.name
            genre = filename.replace('20250811_', '').replace('_raw_data.xlsx', '')
            
            print(f"Processing {genre}...")
            
            # Read Excel
            df = pd.read_excel(file_path)
            
            # Add metadata
            df['genre'] = genre
            df['source_file'] = filename
            df['ingested_date'] = '2025-08-11'  # From filename
            
            print(f"  {len(df)} rows, {len(df.columns)} columns")
            
            all_data.append(df)
            
        except Exception as e:
            print(f"Error with {file_path}: {e}")
    
    if all_data:
        # Combine all data
        print("Combining all data...")
        combined_df = pd.concat(all_data, ignore_index=True)
        
        print(f"Combined: {len(combined_df)} rows, {len(combined_df.columns)} columns")
        
        # Create DuckDB table
        print("Creating DuckDB table...")
        conn.execute("DROP TABLE IF EXISTS books")
        conn.register('temp_df', combined_df)
        conn.execute("CREATE TABLE books AS SELECT * FROM temp_df")
        
        # Verify
        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        print(f"Table created with {count} rows")
        
        # Show genres
        genres = conn.execute("""
            SELECT genre, COUNT(*) as count 
            FROM books 
            GROUP BY genre 
            ORDER BY count DESC
        """).fetchall()
        
        print("Genre distribution:")
        for genre, count in genres:
            print(f"  {genre}: {count}")
        
        # Show sample columns
        columns = conn.execute("PRAGMA table_info(books)").fetchall()
        print(f"\nTable has {len(columns)} columns:")
        for col in columns[:10]:  # First 10 columns
            print(f"  {col[1]} ({col[2]})")
        if len(columns) > 10:
            print(f"  ... and {len(columns) - 10} more")
    
    conn.close()
    print(f"\nDatabase saved: {db_path}")

if __name__ == "__main__":
    main()
