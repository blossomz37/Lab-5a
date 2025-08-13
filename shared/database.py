"""
Shared database utilities for Book Data Processing project
Provides consistent DuckDB connection and query functions
"""

import os
import duckdb
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Try to import configuration, fallback to basic setup
try:
    from .config import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookDatabase:
    """DuckDB database interface for book data"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to DuckDB file. If None, uses configuration or smart path detection
        """
        if db_path is None:
            if CONFIG_AVAILABLE:
                config = get_config()
                db_path = config.db_path
                self.timeout = config.db_timeout
                self.log_queries = config.log_queries
                logger.info("Using database path from configuration")
            else:
                db_path = self._get_database_path()
                self.timeout = 30
                self.log_queries = False
                logger.info("Configuration not available, using smart path detection")
        
        self.db_path = Path(db_path)
        self.conn = None
        
    def _get_database_path(self) -> str:
        """Smart path detection for different environments"""
        
        # Check for Streamlit Cloud environment
        if os.environ.get('STREAMLIT_SHARING'):
            return "books_data.duckdb"
        
        # Check for local development
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        # Try common locations
        possible_paths = [
            project_root / "data" / "processed" / "books_data.duckdb",
            project_root / "books_data.duckdb",
            "books_data.duckdb"
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found database at: {path}")
                return str(path)
        
        # Default path for new database
        default_path = project_root / "data" / "processed" / "books_data.duckdb"
        logger.warning(f"Database not found, will use: {default_path}")
        return str(default_path)
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = duckdb.connect(str(self.db_path))
            logger.info(f"Connected to database: {self.db_path}")
            return self.conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def execute_query(self, query: str) -> List[tuple]:
        """Execute query and return results"""
        if not self.conn:
            self.connect()
        
        try:
            result = self.conn.execute(query).fetchall()
            return result
        except Exception as e:
            logger.error(f"Query failed: {e}")
            logger.error(f"Query: {query}")
            raise
    
    def get_books_count(self, selected_genres: List[str] = None) -> int:
        """Get total number of books"""
        if selected_genres:
            genre_list = "', '".join(selected_genres)
            query = f"SELECT COUNT(*) FROM books WHERE COALESCE(genre_display, genre) IN ('{genre_list}')"
        else:
            query = "SELECT COUNT(*) FROM books"
        
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    def get_genres(self) -> List[str]:
        """Get list of all genres using display names"""
        result = self.execute_query("SELECT DISTINCT COALESCE(genre_display, genre) FROM books ORDER BY COALESCE(genre_display, genre)")
        return [row[0] for row in result]
    
    def get_genre_stats(self, selected_genres: List[str] = None) -> List[Dict[str, Any]]:
        """Get statistics by genre using display names"""
        where_conditions = ["price IS NOT NULL AND reviewAverage IS NOT NULL"]
        
        if selected_genres:
            genre_list = "', '".join(selected_genres)
            where_conditions.append(f"COALESCE(genre_display, genre) IN ('{genre_list}')")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        SELECT 
            COALESCE(genre_display, genre) as genre,
            COUNT(*) as book_count,
            ROUND(AVG(price), 2) as avg_price,
            ROUND(AVG(reviewAverage), 2) as avg_rating,
            ROUND(AVG(nReviews), 0) as avg_reviews
        FROM books
        WHERE {where_clause}
        GROUP BY COALESCE(genre_display, genre)
        ORDER BY book_count DESC
        """
        
        result = self.execute_query(query)
        return [
            {
                'genre': row[0],
                'book_count': row[1],
                'avg_price': row[2],
                'avg_rating': row[3],
                'avg_reviews': int(row[4]) if row[4] else 0
            }
            for row in result
        ]
    
    def search_books(self, title: str = "", author: str = "", genre: str = "", 
                    min_rating: float = 0, max_price: float = 1000, 
                    limit: int = 100) -> List[Dict[str, Any]]:
        """Search books with filters"""
        
        conditions = ["1=1"]  # Base condition
        
        if title:
            conditions.append(f"LOWER(Title) LIKE '%{title.lower()}%'")
        if author:
            conditions.append(f"LOWER(Author) LIKE '%{author.lower()}%'")
        if genre and genre != "All":
            conditions.append(f"COALESCE(genre_display, genre) = '{genre}'")
        if min_rating > 0:
            conditions.append(f"reviewAverage >= {min_rating}")
        if max_price < 1000:
            conditions.append(f"price <= {max_price}")
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        SELECT 
            Title, Author, COALESCE(genre_display, genre) as genre, price, reviewAverage, nReviews, 
            releaseDate, Series, bookURL, coverImage, blurbText, salesRank, subcatsList, topicTags, source_file
        FROM books 
        WHERE {where_clause}
        ORDER BY reviewAverage DESC, nReviews DESC
        LIMIT {limit}
        """
        
        result = self.execute_query(query)
        return [
            {
                'title': row[0],
                'author': row[1],
                'genre': row[2],
                'price': row[3],
                'rating': row[4],
                'reviews': int(row[5]) if row[5] else 0,
                'release_date': row[6],
                'series': row[7],
                'url': row[8],
                'cover_image': row[9],
                'blurb': row[10],
                'sales_rank': row[11],
                'subcats': row[12],
                'topics': row[13],
                'source_file': row[14]
            }
            for row in result
        ]
    
    def get_top_books(self, limit: int = 10, selected_genres: List[str] = None) -> List[Dict[str, Any]]:
        """Get top-rated books"""
        where_conditions = ["reviewAverage IS NOT NULL AND nReviews > 100"]
        
        if selected_genres:
            genre_list = "', '".join(selected_genres)
            where_conditions.append(f"COALESCE(genre_display, genre) IN ('{genre_list}')")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        SELECT Title, Author, COALESCE(genre_display, genre) as genre, reviewAverage, nReviews, price, coverImage, bookURL, blurbText, salesRank, subcatsList, topicTags, releaseDate, source_file
        FROM books 
        WHERE {where_clause}
        ORDER BY reviewAverage DESC, nReviews DESC
        LIMIT {limit}
        """
        
        result = self.execute_query(query)
        return [
            {
                'title': row[0],
                'author': row[1],
                'genre': row[2],
                'rating': row[3],
                'reviews': int(row[4]) if row[4] else 0,
                'price': row[5],
                'cover_image': row[6],
                'book_url': row[7],
                'blurb': row[8],
                'sales_rank': row[9],
                'subcats': row[10],
                'topics': row[11],
                'release_date': row[12],
                'source_file': row[13]
            }
            for row in result
        ]
    
    def get_price_stats(self, selected_genres: List[str] = None) -> Dict[str, float]:
        """Get price statistics"""
        where_conditions = ["price IS NOT NULL AND price > 0"]
        
        if selected_genres:
            genre_list = "', '".join(selected_genres)
            where_conditions.append(f"COALESCE(genre_display, genre) IN ('{genre_list}')")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        SELECT 
            MIN(price) as min_price,
            MAX(price) as max_price,
            ROUND(AVG(price), 2) as avg_price,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price), 2) as median_price
        FROM books
        WHERE {where_clause}
        """
        
        result = self.execute_query(query)
        if result:
            return {
                'min': result[0][0],
                'max': result[0][1],
                'average': result[0][2],
                'median': result[0][3]
            }
        return {'min': 0, 'max': 0, 'average': 0, 'median': 0}
    
    def get_price_data_by_genre(self, selected_genres: List[str] = None) -> List[tuple]:
        """Get price data for genre-based analysis"""
        where_conditions = ["price IS NOT NULL AND price > 0 AND price < 100"]
        
        if selected_genres:
            genre_list = "', '".join(selected_genres)
            where_conditions.append(f"COALESCE(genre_display, genre) IN ('{genre_list}')")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        SELECT COALESCE(genre_display, genre) as genre, price 
        FROM books 
        WHERE {where_clause}
        """
        
        return self.execute_query(query)
    
    def check_table_exists(self, table_name: str = "books") -> bool:
        """Check if table exists"""
        try:
            result = self.execute_query(f"SELECT COUNT(*) FROM {table_name} LIMIT 1")
            return True
        except:
            return False