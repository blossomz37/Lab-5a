#!/usr/bin/env python3
"""
Process all Excel files to DuckDB with improved error handling and validation
"""

import pandas as pd
import duckdb
import glob
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add shared modules to path
script_dir = Path(__file__).parent
phase_dir = script_dir.parent
project_dir = phase_dir.parent
sys.path.insert(0, str(project_dir))

try:
    from shared.data_mapping import get_data_mapper
    DATA_MAPPING_AVAILABLE = True
except ImportError:
    DATA_MAPPING_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate environment before processing"""
    script_dir = Path(__file__).parent
    phase_dir = script_dir.parent
    project_dir = phase_dir.parent
    data_dir = project_dir / 'data' / 'raw'
    
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return False
    
    excel_files = list(data_dir.glob('*.xlsx'))
    if not excel_files:
        logger.error("No Excel files found in data_raw directory")
        return False
    
    logger.info(f"Found {len(excel_files)} Excel files")
    return True

def standardize_columns(df):
    """Standardize column names for consistency"""
    column_mapping = {
        'Title': 'title',
        'ASIN': 'asin',
        'Author': 'author',
        'nReviews': 'review_count',
        'reviewAverage': 'rating',
        'salesRank': 'rank_overall'
    }
    
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df[new_name] = df[old_name]
    
    return df

def validate_data(df, filename):
    """Validate data quality and report issues"""
    issues = []
    
    # Check for required columns
    required_cols = ['Title', 'ASIN', 'Author']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
    
    # Check for empty dataframe
    if df.empty:
        issues.append("Empty dataframe")
    
    # Check for duplicates
    if 'ASIN' in df.columns:
        duplicate_asins = df['ASIN'].duplicated().sum()
        if duplicate_asins > 0:
            issues.append(f"Found {duplicate_asins} duplicate ASINs")
    
    # Check for missing values in critical columns
    for col in ['Title', 'Author']:
        if col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                issues.append(f"{missing} missing values in {col}")
    
    if issues:
        logger.warning(f"Data quality issues in {filename}: {'; '.join(issues)}")
    
    return len(issues) == 0

def process_with_progress(excel_files, db_path):
    """Process files with progress tracking"""
    conn = duckdb.connect(str(db_path))
    all_data = []
    processed = 0
    failed = []
    
    for i, file_path in enumerate(excel_files, 1):
        try:
            filename = file_path.name
            genre = filename.replace('20250811_', '').replace('_raw_data.xlsx', '')
            
            logger.info(f"[{i}/{len(excel_files)}] Processing {genre}...")
            
            # Read with error handling
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # Validate data
            if not validate_data(df, filename):
                logger.warning(f"Data validation warnings for {filename}")
            
            # Standardize columns
            df = standardize_columns(df)
            
            # Add metadata
            df['genre'] = genre
            df['source_file'] = filename
            df['ingested_date'] = datetime.now().strftime('%Y-%m-%d')
            df['processing_timestamp'] = datetime.now().isoformat()
            
            # Apply data mapping if available
            if DATA_MAPPING_AVAILABLE:
                try:
                    data_mapper = get_data_mapper()
                    df['genre_display'] = data_mapper.get_genre_display_name(genre)
                    logger.info(f"  Applied genre mapping: {genre} -> {df['genre_display'].iloc[0]}")
                except Exception as e:
                    logger.warning(f"  Could not apply data mapping: {e}")
                    df['genre_display'] = genre.replace('_', ' ').title()
            else:
                df['genre_display'] = genre.replace('_', ' ').title()
            
            all_data.append(df)
            processed += 1
            
            logger.info(f"  ✓ {len(df)} rows, {len(df.columns)} columns")
            
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            failed.append(file_path)
    
    return all_data, processed, failed, conn

def create_database_with_indexes(conn, combined_df):
    """Create database with proper indexes for performance"""
    # Create main table
    conn.execute("DROP TABLE IF EXISTS books")
    conn.register('books_df', combined_df)
    conn.execute("CREATE TABLE books AS SELECT * FROM books_df")
    
    # Create indexes for common queries
    try:
        conn.execute("CREATE INDEX idx_genre ON books(genre)")
        conn.execute("CREATE INDEX idx_asin ON books(ASIN)")
        conn.execute("CREATE INDEX idx_rating ON books(reviewAverage)")
        logger.info("Created database indexes")
    except Exception as e:
        logger.warning(f"Could not create indexes: {e}")
    
    # Create summary view
    conn.execute("""
        CREATE OR REPLACE VIEW genre_summary AS
        SELECT 
            genre,
            COUNT(*) as book_count,
            AVG(price) as avg_price,
            AVG(reviewAverage) as avg_rating,
            SUM(nReviews) as total_reviews
        FROM books
        GROUP BY genre
    """)
    logger.info("Created genre_summary view")

def generate_report(conn):
    """Generate summary report"""
    report = []
    
    # Total stats
    total = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    report.append(f"Total books: {total:,}")
    
    # Genre distribution
    genres = conn.execute("""
        SELECT genre, COUNT(*) as count 
        FROM books 
        GROUP BY genre 
        ORDER BY count DESC
    """).fetchall()
    
    report.append("\nGenre distribution:")
    for genre, count in genres:
        report.append(f"  {genre}: {count:,}")
    
    # Price statistics
    price_stats = conn.execute("""
        SELECT 
            MIN(price) as min_price,
            MAX(price) as max_price,
            AVG(price) as avg_price
        FROM books
        WHERE price IS NOT NULL
    """).fetchone()
    
    report.append(f"\nPrice range: ${price_stats[0]:.2f} - ${price_stats[1]:.2f}")
    report.append(f"Average price: ${price_stats[2]:.2f}")
    
    # Rating statistics
    rating_stats = conn.execute("""
        SELECT 
            MIN(reviewAverage) as min_rating,
            MAX(reviewAverage) as max_rating,
            AVG(reviewAverage) as avg_rating
        FROM books
        WHERE reviewAverage IS NOT NULL
    """).fetchone()
    
    report.append(f"\nRating range: {rating_stats[0]:.1f} - {rating_stats[1]:.1f}")
    report.append(f"Average rating: {rating_stats[2]:.2f}")
    
    return "\n".join(report)

def main():
    """Main processing function with comprehensive error handling"""
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Set paths (relative to script location)
    script_dir = Path(__file__).parent
    phase_dir = script_dir.parent
    project_dir = phase_dir.parent
    data_dir = project_dir / 'data' / 'raw'
    db_path = project_dir / 'data' / 'processed' / 'books_data.duckdb'
    
    try:
        # Get Excel files
        excel_files = sorted(data_dir.glob('*.xlsx'))
        
        # Process files
        all_data, processed, failed, conn = process_with_progress(excel_files, db_path)
        
        if not all_data:
            logger.error("No data to process")
            sys.exit(1)
        
        # Combine data
        logger.info("Combining all data...")
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Combined: {len(combined_df):,} rows, {len(combined_df.columns)} columns")
        
        # Create database with indexes
        create_database_with_indexes(conn, combined_df)
        
        # Generate report
        report = generate_report(conn)
        print("\n" + "="*50)
        print("DATABASE CREATION SUMMARY")
        print("="*50)
        print(report)
        
        # Report processing results
        if failed:
            print(f"\n⚠️  Failed to process {len(failed)} files:")
            for f in failed:
                print(f"  - {os.path.basename(f)}")
        
        print(f"\n✅ Successfully processed {processed}/{len(excel_files)} files")
        print(f"📁 Database saved: {db_path}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()