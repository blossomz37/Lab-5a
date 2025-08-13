#!/usr/bin/env python3
"""
Verify DuckDB database structure and content
"""

import duckdb
from pathlib import Path

def main():
    # Use relative path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    db_path = project_dir / 'books_data.duckdb'
    
    try:
        conn = duckdb.connect(str(db_path))
        
        # Basic stats
        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        print(f"Total records: {count:,}")
        
        # Column info
        columns = conn.execute("PRAGMA table_info(books)").fetchall()
        print(f"\nColumns ({len(columns)}):")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Genre distribution
        print("\nGenre distribution:")
        genres = conn.execute("""
            SELECT genre, COUNT(*) as count 
            FROM books 
            GROUP BY genre 
            ORDER BY count DESC
        """).fetchall()
        
        for genre, count in genres:
            print(f"  {genre}: {count:,}")
        
        # Sample data
        print("\nSample records:")
        sample = conn.execute("""
            SELECT Title, Author, genre, price, reviewAverage, nReviews 
            FROM books 
            LIMIT 3
        """).fetchall()
        
        for i, row in enumerate(sample, 1):
            print(f"\n{i}. Title: {row[0]}")
            print(f"   Author: {row[1]}")
            print(f"   Genre: {row[2]}")
            print(f"   Price: ${row[3]}")
            print(f"   Rating: {row[4]}")
            print(f"   Reviews: {row[5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
