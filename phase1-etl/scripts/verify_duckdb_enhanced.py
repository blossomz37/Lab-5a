#!/usr/bin/env python3
"""
Enhanced DuckDB verification with data quality checks
"""

import duckdb
import sys
from pathlib import Path
from datetime import datetime

def check_database_exists(db_path):
    """Check if database file exists"""
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        print("Run create_duckdb.py first to create the database")
        return False
    return True

def run_data_quality_checks(conn):
    """Run comprehensive data quality checks"""
    print("\n" + "="*50)
    print("DATA QUALITY CHECKS")
    print("="*50)
    
    issues = []
    
    # Check for duplicate ASINs
    duplicates = conn.execute("""
        SELECT ASIN, COUNT(*) as count
        FROM books
        GROUP BY ASIN
        HAVING COUNT(*) > 1
    """).fetchall()
    
    if duplicates:
        issues.append(f"Found {len(duplicates)} duplicate ASINs")
        print(f"⚠️  Duplicate ASINs found: {len(duplicates)}")
    else:
        print("✅ No duplicate ASINs")
    
    # Check for missing critical data
    missing_checks = [
        ("Title", "titles"),
        ("Author", "authors"),
        ("ASIN", "ASINs")
    ]
    
    for col, name in missing_checks:
        missing = conn.execute(f"""
            SELECT COUNT(*) 
            FROM books 
            WHERE {col} IS NULL OR {col} = ''
        """).fetchone()[0]
        
        if missing > 0:
            issues.append(f"{missing} missing {name}")
            print(f"⚠️  Missing {name}: {missing}")
        else:
            print(f"✅ All {name} present")
    
    # Check for invalid prices
    invalid_prices = conn.execute("""
        SELECT COUNT(*)
        FROM books
        WHERE price < 0 OR price > 1000
    """).fetchone()[0]
    
    if invalid_prices > 0:
        issues.append(f"{invalid_prices} invalid prices")
        print(f"⚠️  Invalid prices: {invalid_prices}")
    else:
        print("✅ All prices valid")
    
    # Check for invalid ratings
    invalid_ratings = conn.execute("""
        SELECT COUNT(*)
        FROM books
        WHERE reviewAverage IS NOT NULL 
        AND (reviewAverage < 0 OR reviewAverage > 5)
    """).fetchone()[0]
    
    if invalid_ratings > 0:
        issues.append(f"{invalid_ratings} invalid ratings")
        print(f"⚠️  Invalid ratings: {invalid_ratings}")
    else:
        print("✅ All ratings valid")
    
    return issues

def display_statistics(conn):
    """Display comprehensive statistics"""
    print("\n" + "="*50)
    print("DATABASE STATISTICS")
    print("="*50)
    
    # Basic stats
    total = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    print(f"\n📚 Total books: {total:,}")
    
    # Genre breakdown with stats
    print("\n📊 Genre Statistics:")
    genre_stats = conn.execute("""
        SELECT 
            genre,
            COUNT(*) as count,
            ROUND(AVG(price), 2) as avg_price,
            ROUND(AVG(reviewAverage), 2) as avg_rating,
            ROUND(AVG(nReviews), 0) as avg_reviews
        FROM books
        GROUP BY genre
        ORDER BY count DESC
    """).fetchall()
    
    print(f"{'Genre':<25} {'Count':<8} {'Avg Price':<12} {'Avg Rating':<12} {'Avg Reviews'}")
    print("-" * 70)
    for genre, count, avg_price, avg_rating, avg_reviews in genre_stats:
        print(f"{genre:<25} {count:<8} ${avg_price:<11.2f} {avg_rating:<12} {int(avg_reviews) if avg_reviews else 0}")
    
    # Top rated books
    print("\n⭐ Top 5 Rated Books:")
    top_books = conn.execute("""
        SELECT Title, Author, reviewAverage, nReviews, genre
        FROM books
        WHERE reviewAverage IS NOT NULL AND nReviews > 100
        ORDER BY reviewAverage DESC, nReviews DESC
        LIMIT 5
    """).fetchall()
    
    for i, (title, author, rating, reviews, genre) in enumerate(top_books, 1):
        # Truncate long titles
        display_title = title[:50] + "..." if len(title) > 50 else title
        print(f"{i}. {display_title}")
        print(f"   By: {author[:40]}")
        print(f"   Rating: {rating:.1f} ({int(reviews):,} reviews) - Genre: {genre}")
    
    # Price analysis
    print("\n💰 Price Analysis:")
    price_stats = conn.execute("""
        SELECT 
            MIN(price) as min_price,
            MAX(price) as max_price,
            ROUND(AVG(price), 2) as avg_price,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price), 2) as median_price
        FROM books
        WHERE price IS NOT NULL AND price > 0
    """).fetchone()
    
    print(f"  Min: ${price_stats[0]:.2f}")
    print(f"  Max: ${price_stats[1]:.2f}")
    print(f"  Average: ${price_stats[2]:.2f}")
    print(f"  Median: ${price_stats[3]:.2f}")
    
    # Free books
    free_books = conn.execute("SELECT COUNT(*) FROM books WHERE isFree = true").fetchone()[0]
    print(f"  Free books: {free_books}")
    
    # Date range
    print("\n📅 Release Date Range:")
    date_range = conn.execute("""
        SELECT 
            MIN(releaseDate) as earliest,
            MAX(releaseDate) as latest
        FROM books
        WHERE releaseDate IS NOT NULL
    """).fetchone()
    
    print(f"  Earliest: {date_range[0]}")
    print(f"  Latest: {date_range[1]}")

def export_sample_queries(conn):
    """Export useful sample queries"""
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    queries_file = project_dir / 'sample_queries.sql'
    
    sample_queries = """-- Sample DuckDB Queries for Book Database

-- 1. Find all books by a specific author
SELECT Title, genre, price, reviewAverage
FROM books
WHERE Author LIKE '%Stephen King%';

-- 2. Top books with supernatural elements
SELECT Title, Author, genre, reviewAverage, nReviews
FROM books
WHERE hasSupernatural = true
ORDER BY reviewAverage DESC, nReviews DESC
LIMIT 10;

-- 3. Romance books under $5
SELECT Title, Author, price, reviewAverage
FROM books
WHERE hasRomance = true AND price < 5
ORDER BY reviewAverage DESC;

-- 4. Genre comparison
SELECT 
    genre,
    COUNT(*) as book_count,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(reviewAverage), 2) as avg_rating
FROM books
GROUP BY genre
ORDER BY avg_rating DESC;

-- 5. Most reviewed books
SELECT Title, Author, nReviews, reviewAverage, genre
FROM books
ORDER BY nReviews DESC
LIMIT 10;

-- 6. Price distribution by genre
SELECT 
    genre,
    MIN(price) as min_price,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price) as q1,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) as median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price) as q3,
    MAX(price) as max_price
FROM books
WHERE price IS NOT NULL
GROUP BY genre;

-- 7. Books in series
SELECT Title, Author, Series, genre
FROM books
WHERE Series IS NOT NULL AND Series != ''
ORDER BY Series, Title;

-- 8. Traditional vs Self-published
SELECT 
    CASE WHEN isTrad = true THEN 'Traditional' ELSE 'Self-Published' END as pub_type,
    COUNT(*) as count,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(reviewAverage), 2) as avg_rating
FROM books
GROUP BY isTrad;
"""
    
    queries_file.write_text(sample_queries)
    print(f"\n📝 Sample queries saved to: {queries_file}")

def main():
    """Main verification function"""
    # Use relative path
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    db_path = project_dir / 'books_data.duckdb'
    
    # Check database exists
    if not check_database_exists(db_path):
        sys.exit(1)
    
    try:
        conn = duckdb.connect(str(db_path), read_only=True)
        
        print("="*50)
        print(f"DATABASE VERIFICATION REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        # Check if books table exists
        tables = conn.execute("SHOW TABLES").fetchall()
        if not any('books' in str(table) for table in tables):
            print("❌ 'books' table not found in database")
            sys.exit(1)
        
        # Run data quality checks
        issues = run_data_quality_checks(conn)
        
        # Display statistics
        display_statistics(conn)
        
        # Export sample queries
        export_sample_queries(conn)
        
        # Final summary
        print("\n" + "="*50)
        if issues:
            print(f"⚠️  VERIFICATION COMPLETE WITH {len(issues)} WARNINGS")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ VERIFICATION COMPLETE - ALL CHECKS PASSED")
        print("="*50)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()