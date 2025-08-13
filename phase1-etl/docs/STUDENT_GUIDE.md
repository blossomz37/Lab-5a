# Student Guide: Book Data Processing Lab

## Overview
This lab teaches you how to process and analyze book metadata using Python and DuckDB. You'll work with real book data from 14 different genres, learning ETL (Extract, Transform, Load) processes and database operations.

## Github
https://github.com/blossomz37/Lab-5b-ffa

## Learning Objectives
By completing this lab, you will:
- Process Excel files using pandas
- Create and query DuckDB databases
- Perform data aggregation and analysis
- Build automated data pipelines

## Prerequisites
- Basic Python knowledge
- Command line familiarity
- VS Code or similar editor

## Setup Instructions

### 1. Environment Setup
```bash
# Navigate to project directory
cd /Users/carlo/Lab-5a

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Data Files
```bash
# Check Excel files are present
ls data_raw/*.xlsx | wc -l
# Should show: 14
```

## Lab Exercises

### Exercise 1: Create the Database
Run the main processing script to convert Excel files to DuckDB:

```bash
python3 scripts/create_duckdb.py
```

**Expected Output:**
- Creates `books_data.duckdb` database
- Shows processing progress for each genre
- Displays total records (~1,400 books)

### Exercise 2: Verify Database
Check the database structure and contents:

```bash
python3 scripts/verify_duckdb.py
```

**Tasks:**
- Note the total number of records
- Identify which genre has the most books
- Review the column structure

### Exercise 3: Query the Database
Create a new script `scripts/analyze_books.py`:

```python
#!/usr/bin/env python3
import duckdb

conn = duckdb.connect('/Users/carlo/Lab-5a/books_data.duckdb')

# Your queries here
# Example: Find top-rated books
result = conn.execute("""
    SELECT title, author, rating, review_count 
    FROM books 
    WHERE rating >= 4.5 
    ORDER BY review_count DESC 
    LIMIT 10
""").fetchall()

for row in result:
    print(f"{row[0]} by {row[1]} - Rating: {row[2]} ({row[3]} reviews)")

conn.close()
```

### Exercise 4: Data Analysis Tasks

Try these analysis queries:

1. **Price Analysis by Genre**
```sql
SELECT genre, AVG(price) as avg_price, MIN(price), MAX(price)
FROM books
GROUP BY genre
ORDER BY avg_price DESC
```

2. **Popular Authors**
```sql
SELECT author, COUNT(*) as book_count, AVG(rating) as avg_rating
FROM books
GROUP BY author
HAVING COUNT(*) > 1
ORDER BY book_count DESC
```

3. **Romance Subgenres**
```sql
SELECT COUNT(*) as count
FROM books
WHERE has_romance = true
```

4. **Recent Releases**
```sql
SELECT title, author, release_date
FROM books
WHERE release_date >= '2024-01-01'
ORDER BY release_date DESC
```

## Advanced Challenges

### Challenge 1: Data Quality Report
Create a script that checks for:
- Missing values in critical fields
- Duplicate books (same ASIN)
- Invalid price or rating values
- Books without reviews

### Challenge 2: Genre Comparison
Write a script that:
- Compares average ratings across genres
- Finds the most expensive genre
- Identifies genres with supernatural elements

### Challenge 3: Export Results
Modify the scripts to:
- Export query results to CSV
- Create summary statistics JSON file
- Generate a markdown report

## Project Structure
```
Lab-5a/
├── data_raw/           # Source Excel files (DO NOT MODIFY)
├── scripts/            # Your Python scripts
├── venv/              # Python virtual environment
├── books_data.duckdb  # Generated database
└── requirements.txt   # Python dependencies
```

## Common Issues & Solutions

### Issue: "No module named pandas"
**Solution:** Activate virtual environment first:
```bash
source venv/bin/activate
```

### Issue: "books table not found"
**Solution:** Run create_duckdb.py first to create the database

### Issue: Excel file errors
**Solution:** Ensure openpyxl is installed:
```bash
pip install openpyxl
```

## Tips for Success

1. **Always activate venv** before running scripts
2. **Check data types** when querying (prices might be floats)
3. **Use LIMIT** when exploring large result sets
4. **Save your queries** in separate .sql or .py files
5. **Document your findings** with comments

## Submission Requirements

Create a submission folder with:
1. Your analysis scripts
2. A `findings.md` file with interesting insights
3. Any visualizations or exports you create

## Further Learning

- [DuckDB Documentation](https://duckdb.org/docs/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- SQL practice with book data queries
- Data visualization with matplotlib/seaborn

## Support

If you encounter issues:
1. Check error messages carefully
2. Verify file paths are correct
3. Ensure virtual environment is activated
4. Review the README.md for command reference