"""
Initialize database for Streamlit Cloud deployment
Creates the DuckDB database from Excel files if it doesn't exist
"""

import os
import sys
from pathlib import Path
import duckdb
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add shared module to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from shared.data_mapping import get_data_mapper

def create_database():
    """Create DuckDB database from Excel files"""
    
    # Define paths
    db_path = project_root / "data" / "processed" / "books_data.duckdb"
    raw_data_path = project_root / "data" / "raw"
    
    # Check if database already exists
    if db_path.exists():
        logger.info(f"Database already exists at {db_path}")
        return True
    
    # Create directories if they don't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get data mapper for genre display names
    data_mapper = get_data_mapper()
    
    try:
        # Connect to DuckDB
        conn = duckdb.connect(str(db_path))
        logger.info(f"Creating database at {db_path}")
        
        # Create books table (matching Excel structure)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                Title VARCHAR,
                ASIN VARCHAR,
                kuStatus VARCHAR,
                Author VARCHAR,
                Series VARCHAR,
                nReviews INTEGER,
                reviewAverage FLOAT,
                price FLOAT,
                salesRank INTEGER,
                releaseDate VARCHAR,
                nPages INTEGER,
                publisher VARCHAR,
                isTrad BOOLEAN,
                blurbText TEXT,
                coverImage VARCHAR,
                bookURL VARCHAR,
                topicTags TEXT,
                blurbKeyphrases TEXT,
                subcatsList TEXT,
                isFree BOOLEAN,
                isDuplicateASIN BOOLEAN,
                estimatedBlurbPOV VARCHAR,
                hasSupernatural BOOLEAN,
                hasRomance BOOLEAN,
                genre VARCHAR,
                genre_display VARCHAR,
                source_file VARCHAR
            )
        """)
        
        # Process each Excel file
        excel_files = list(raw_data_path.glob("*.xlsx"))
        
        if not excel_files:
            logger.warning(f"No Excel files found in {raw_data_path}")
            logger.info("Creating empty database structure")
            conn.commit()
            conn.close()
            return True
        
        for file_path in excel_files:
            logger.info(f"Processing {file_path.name}")
            
            try:
                # Read Excel file
                df = pd.read_excel(file_path)
                
                # Extract genre from filename
                filename = file_path.stem
                parts = filename.split('_')
                if len(parts) >= 3:
                    # Remove date prefix and '_raw_data' suffix
                    genre_parts = parts[1:-2]
                    genre = '_'.join(genre_parts)
                else:
                    genre = 'unknown'
                
                # Add metadata columns
                df['genre'] = genre
                df['genre_display'] = data_mapper.get_genre_display_name(genre)
                df['source_file'] = file_path.name
                
                # Insert into DuckDB
                conn.execute("INSERT INTO books SELECT * FROM df")
                logger.info(f"  Added {len(df)} books from {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")
                continue
        
        # Create indexes for better performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_genre ON books(genre)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_genre_display ON books(genre_display)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rating ON books(reviewAverage)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews ON books(nReviews)")
        
        # Commit and close
        conn.commit()
        conn.close()
        
        logger.info("Database created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)