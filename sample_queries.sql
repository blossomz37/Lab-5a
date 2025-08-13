-- Sample DuckDB Queries for Book Database

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
