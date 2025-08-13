"""
Book Data Explorer - Interactive Streamlit Web Application
Modern, stylish interface for exploring book data from DuckDB
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import re
from pathlib import Path

# Add shared module to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from shared.database import BookDatabase
    from shared.config import get_config
    from shared.data_mapping import get_data_mapper
except ImportError as e:
    st.error(f"❌ Cannot import shared modules: {e}")
    st.info("Make sure you're running from the project root directory")
    st.stop()

# Load configuration and data mapping
config = get_config()
data_mapper = get_data_mapper()

# Initialize database if it doesn't exist (for deployment)
def ensure_database_exists():
    """Ensure database exists, create if necessary"""
    db_path = project_root / "data" / "processed" / "books_data.duckdb"
    if not db_path.exists():
        st.info("🔄 Initializing database for first use...")
        try:
            # Import and run database creation
            from init_database import create_database
            if create_database():
                st.success("✅ Database created successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to create database. Please check the logs.")
                st.stop()
        except Exception as e:
            st.error(f"❌ Database initialization failed: {e}")
            st.stop()

# Utility functions
def parse_author_markdown(author_text):
    """Parse author markdown link and return clean name and URL"""
    if not author_text:
        return "Unknown Author", None
    
    # Check if it's a markdown link format: [Name](URL)
    markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    match = re.search(markdown_pattern, author_text)
    
    if match:
        author_name = match.group(1)
        author_url = match.group(2)
        return author_name, author_url
    else:
        # Return as-is if not markdown format
        return author_text, None

def format_author_display(author_text):
    """Format author for display in Streamlit using data mapping"""
    # Use data mapping for enhanced author parsing
    author_name, author_url, isbn = data_mapper.extract_author_info(author_text)
    
    if author_url:
        # Create a clickable link
        return f'<a href="{author_url}" target="_blank" style="color: #1f77b4; text-decoration: none;">{author_name}</a>'
    else:
        return author_name

def format_book_card(book):
    """Format book information using data mapping specifications"""
    enhanced_book = data_mapper.get_enhanced_book_data(book)
    
    # Get display configuration
    display_config = data_mapper.get_card_display_config()
    
    # Format primary info
    title = enhanced_book.get('title', enhanced_book.get('Title', 'Unknown Title'))
    author = format_author_display(enhanced_book.get('author', enhanced_book.get('Author', 'Unknown Author')))
    
    # Use genre_display if available, fallback to genre mapping
    genre = enhanced_book.get('genre_display', 
                            data_mapper.get_genre_display_name(
                                enhanced_book.get('genre', enhanced_book.get('Genre', ''))))
    
    # Format rating and reviews
    rating = enhanced_book.get('rating', enhanced_book.get('reviewAverage', 0))
    reviews = enhanced_book.get('reviews', enhanced_book.get('nReviews', 0))
    price = enhanced_book.get('price', 0)
    
    # Format rating with stars
    try:
        rating_float = float(rating) if rating else 0
        star_display = "⭐" * int(rating_float) + f" {rating_float:.1f}"
    except (ValueError, TypeError):
        star_display = "No rating"
    
    # Format reviews count
    try:
        reviews_count = f"{int(reviews):,}" if reviews else "0"
    except (ValueError, TypeError):
        reviews_count = "0"
    
    # Format price
    try:
        price_display = f"${float(price):.2f}" if price else "N/A"
    except (ValueError, TypeError):
        price_display = "N/A"
    
    return {
        'title': title,
        'author': author,
        'genre': genre,
        'rating_display': star_display,
        'reviews_display': reviews_count,
        'price_display': price_display,
        'series': enhanced_book.get('series', enhanced_book.get('Series', '')),
        'enhanced_data': enhanced_book
    }

def format_subcategories(subcats_str):
    """Parse subcategories with markdown links and extract rank, text, and URLs"""
    if not subcats_str or subcats_str.strip() == '' or subcats_str == 'N/A':
        return []
    
    import re
    subcats = []
    
    # Pattern to match markdown links like [#2 in Category](URL)
    markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(markdown_pattern, str(subcats_str))
    
    for text, url in matches:
        # Extract rank number from text like "#2 in Teen & Young Adult..."
        rank_match = re.match(r'^#?(\d+)\s+in\s+(.+)', text.strip())
        if rank_match:
            rank_num = rank_match.group(1)
            category = rank_match.group(2)
            subcats.append({
                'rank': rank_num,
                'category': category,
                'url': url
            })
        else:
            # Fallback if pattern doesn't match
            subcats.append({
                'rank': None,
                'category': text,
                'url': url
            })
    
    return subcats

def format_topics(topics_str):
    """Format topics/tropes from pipe-separated string"""
    if not topics_str or topics_str.strip() == '' or topics_str == 'N/A':
        return []
    
    # Split by | and clean up
    topics = [topic.strip() for topic in str(topics_str).split('|') if topic.strip()]
    return topics

def extract_report_date(source_file):
    """Extract report date from filename like '20250811_genre_raw_data.xlsx'"""
    if not source_file:
        return None
    
    # Extract date from filename pattern
    import re
    match = re.search(r'(\d{8})', str(source_file))
    if match:
        date_str = match.group(1)
        # Convert from YYYYMMDD to M/D/YY
        year = date_str[:4]
        month = date_str[4:6].lstrip('0')  # Remove leading zero
        day = date_str[6:8].lstrip('0')    # Remove leading zero
        return f"{month}/{day}/{year[-2:]}"
    return None

def extract_genre_from_filename(source_file):
    """Extract genre from filename like '20250811_cozy_mystery_raw_data.xlsx'"""
    if not source_file:
        return None
    
    # Extract genre from filename pattern
    import re
    match = re.search(r'\d{8}_([^_]+(?:_[^_]+)*)_raw_data\.xlsx', str(source_file))
    if match:
        genre_code = match.group(1)
        return genre_code.replace('_', ' ').title()
    return None

def format_release_date(date_str):
    """Convert release date to M/D/YY format"""
    if not date_str or str(date_str).strip() == '' or date_str == 'N/A':
        return None
    
    import re
    from datetime import datetime
    
    # Try various date formats
    date_formats = [
        '%Y-%m-%d',      # 2025-01-15
        '%m/%d/%Y',      # 01/15/2025
        '%m-%d-%Y',      # 01-15-2025
        '%B %d, %Y',     # January 15, 2025
        '%b %d, %Y',     # Jan 15, 2025
        '%d/%m/%Y',      # 15/01/2025
        '%Y%m%d',        # 20250115
    ]
    
    date_str = str(date_str).strip()
    
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # Convert to M/D/YY format
            month = str(parsed_date.month)
            day = str(parsed_date.day)
            year = str(parsed_date.year)[-2:]
            return f"{month}/{day}/{year}"
        except ValueError:
            continue
    
    # If no format matches, return as-is
    return date_str

def display_book_with_cover(book, rank=None):
    """Display compact, accessible book card with expandable details"""
    # Get book details
    title = book.get('title', 'Unknown Title')
    author = format_author_display(book.get('author', 'Unknown Author'))
    genre = book.get('genre', 'Unknown Genre')
    rating = book.get('rating', 0)
    reviews = book.get('reviews', 0)
    price = book.get('price', 0)
    cover_image = book.get('cover_image', book.get('coverImage'))
    book_url = book.get('book_url', book.get('url', book.get('bookURL')))
    series = book.get('series', book.get('Series', ''))
    blurb = book.get('blurb', book.get('blurbText', ''))
    sales_rank = book.get('sales_rank', book.get('salesRank'))
    subcats = book.get('subcats', book.get('subcatsList', ''))
    topics = book.get('topics', book.get('topicTags', ''))
    release_date = book.get('release_date', book.get('releaseDate', ''))
    source_file = book.get('source_file', '')
    
    # Format displays
    try:
        rating_float = float(rating) if rating else 0
        star_display = "⭐" * int(rating_float) + f" {rating_float:.1f}"
    except (ValueError, TypeError):
        star_display = "No rating"
    
    try:
        reviews_count = f"{int(reviews):,}" if reviews else "0"
    except (ValueError, TypeError):
        reviews_count = "0"
    
    try:
        price_display = f"${float(price):.2f}" if price else "N/A"
    except (ValueError, TypeError):
        price_display = "N/A"
    
    # Create unique ID for accessibility
    book_id = f"book_{hash(title + str(rank or 0))}"
    
    # Compact layout
    with st.container():
        st.markdown(f'<div class="book-compact" role="article" aria-labelledby="{book_id}-title">', unsafe_allow_html=True)
        
        # Top level - Essential info only
        col1, col2 = st.columns([1, 4])
        
        with col1:
            # Compact cover image
            if cover_image and cover_image.strip() and cover_image != 'N/A':
                try:
                    st.markdown(f'''
                    <a href="{cover_image}" target="_blank" aria-label="View full cover image">
                        <img src="{cover_image}" 
                             style="width:80px; height:auto; border-radius:4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);"
                             alt="Book cover for {title}">
                    </a>
                    ''', unsafe_allow_html=True)
                except:
                    st.markdown('<div style="width:80px; height:120px; background:#f0f0f0; border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:2rem;">📖</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="width:80px; height:120px; background:#f0f0f0; border-radius:4px; display:flex; align-items:center; justify-content:center; font-size:2rem;">📖</div>', unsafe_allow_html=True)
        
        with col2:
            # Essential info - compact layout
            rank_display = f"<span class='rank-compact'>#{rank}</span> " if rank else ""
            
            # Title (clickable)
            if book_url and book_url.strip():
                title_html = f'<a href="{book_url}" target="_blank" class="book-title" id="{book_id}-title">{rank_display}{title}</a>'
            else:
                title_html = f'<span class="book-title" id="{book_id}-title">{rank_display}{title}</span>'
            
            st.markdown(title_html, unsafe_allow_html=True)
            
            # Author and genre (one line)
            st.markdown(f'<div class="book-meta">by {author} • <em>{genre}</em></div>', unsafe_allow_html=True)
            
            # Rating and key info (one line)
            st.markdown(f'''
            <div class="quick-info">
                <span class="book-rating">
                    <span>{star_display}</span>
                    <span>({reviews_count} reviews)</span>
                </span>
                <span><strong>{price_display}</strong></span>
            </div>
            ''', unsafe_allow_html=True)
        
        # Add spacing before expandable details
        st.markdown('<div style="margin-top: 0.5rem;"></div>', unsafe_allow_html=True)
        
        # Expandable detailed information
        with st.expander("📋 Show Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Rankings & Categories**")
                
                # Best Sellers Rank
                if sales_rank and str(sales_rank).strip() and sales_rank != 'N/A':
                    try:
                        rank_num = int(float(sales_rank))
                        st.markdown(f"#{rank_num:,} in Kindle Store")
                    except (ValueError, TypeError):
                        st.markdown(f"{sales_rank} in Kindle Store")
                
                # Subcategories
                subcats_list = format_subcategories(subcats)
                for subcat_data in subcats_list[:3]:
                    if isinstance(subcat_data, dict) and subcat_data.get('rank') and subcat_data.get('category'):
                        rank_num = subcat_data['rank']
                        category = subcat_data['category']
                        amazon_url = subcat_data['url']
                        clickable_category = f'<a href="{amazon_url}" target="_blank" style="color: #1f77b4; text-decoration: none;">{category}</a>'
                        st.markdown(f"#{rank_num} in {clickable_category}", unsafe_allow_html=True)
                
                # Tropes/Topics
                topics_list = format_topics(topics)
                if topics_list:
                    st.markdown("**🏷️ Tropes**")
                    for topic in topics_list[:4]:
                        st.markdown(f"• {topic}")
            
            with col2:
                st.markdown("**📅 Publication Info**")
                
                # Get additional data
                publisher = book.get('publisher', '')
                formatted_release_date = format_release_date(release_date)
                report_date = extract_report_date(source_file)
                genre_from_file = extract_genre_from_filename(source_file)
                
                # First line: Publisher and Release Date
                publisher_text = publisher if publisher and str(publisher).strip() and publisher != 'N/A' else "Not specified"
                release_text = formatted_release_date if formatted_release_date else "Not specified"
                st.markdown(f"**Publisher:** {publisher_text}")
                st.markdown(f"**Release Date:** {release_text}")
                
                # Second line: Genre Report and Report Date
                # Use data mapper to get friendly genre name
                import re
                if genre_from_file:
                    # Extract raw genre code from filename and map to friendly name
                    raw_genre_match = re.search(r'\d{8}_([^_]+(?:_[^_]+)*)_raw_data\.xlsx', str(source_file))
                    if raw_genre_match:
                        raw_genre_code = raw_genre_match.group(1)
                        genre_report_text = data_mapper.get_genre_display_name(raw_genre_code)
                    else:
                        genre_report_text = genre_from_file
                else:
                    genre_report_text = genre
                
                report_text = report_date if report_date else "Not specified"
                st.markdown(f"**Genre Report:** {genre_report_text}")
                st.markdown(f"**Report Date:** {report_text}")
                
                # Series info if available
                if series and str(series).strip() and series != 'N/A':
                    st.markdown(f"**Series:** {series}")
                
                # Book blurb
                if blurb and blurb.strip() and blurb != 'N/A':
                    st.markdown("**📖 Description**")
                    clean_blurb = str(blurb).strip()
                    # Format paragraphs with proper spacing
                    paragraphs = clean_blurb.split('\n\n')  # Split on double line breaks
                    formatted_paragraphs = []
                    for para in paragraphs:
                        if para.strip():
                            # Replace single line breaks with spaces, preserve paragraph breaks
                            formatted_para = para.replace('\n', ' ').strip()
                            formatted_paragraphs.append(formatted_para)
                    
                    formatted_blurb = '<br><br>'.join(formatted_paragraphs)
                    
                    st.markdown(f'''
                    <div style="
                        font-size: 0.9em; 
                        line-height: 1.5; 
                        max-height: 150px; 
                        overflow-y: scroll; 
                        padding: 0.75rem; 
                        background: #f8f9fa; 
                        border: 1px solid #dee2e6;
                        border-radius: 4px; 
                        color: #333333;
                        scrollbar-width: thin;
                        scrollbar-color: #6c757d #f8f9fa;
                    ">
                        {formatted_blurb}
                    </div>
                    ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title=f"📚 {config.app_title}",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    /* Analytics section header adjustments - more specific selectors */
    .analytics-section .stMarkdown h1,
    .analytics-section [data-testid="stMarkdownContainer"] h1 {
        font-size: 1.8rem !important;
        margin-bottom: 0.5rem !important;
        margin-top: 1rem !important;
        line-height: 1.3 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        text-overflow: unset !important;
        overflow: visible !important;
    }
    .analytics-section .stMarkdown h2,
    .analytics-section [data-testid="stMarkdownContainer"] h2 {
        font-size: 1.3rem !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0.8rem !important;
        line-height: 1.3 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        text-overflow: unset !important;
        overflow: visible !important;
    }
    .analytics-section .stMarkdown h3,
    .analytics-section [data-testid="stMarkdownContainer"] h3 {
        font-size: 1.1rem !important;
        margin-bottom: 0.3rem !important;
        margin-top: 0.5rem !important;
        line-height: 1.3 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        text-overflow: unset !important;
        overflow: visible !important;
    }
    /* Target Streamlit's specific header elements */
    .analytics-section [data-testid="stHeader"] h1 {
        font-size: 1.8rem !important;
        margin-bottom: 0.5rem !important;
        margin-top: 1rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        text-overflow: unset !important;
        overflow: visible !important;
    }
    .analytics-section [data-testid="stSubheader"] h2 {
        font-size: 1.3rem !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0.8rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        text-overflow: unset !important;
        overflow: visible !important;
    }
    /* Fix metric card text truncation - reduce size to 75% */
    .analytics-section [data-testid="metric-container"],
    .analytics-section [data-testid="stMetric"],
    .analytics-section [data-testid="metric-container"] *,
    .analytics-section [data-testid="stMetric"] *,
    .analytics-section div[data-testid="metric-container"] *,
    .analytics-section div[data-testid="stMetric"] * {
        font-size: 0.75em !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        text-overflow: unset !important;
        overflow: visible !important;
        line-height: 1.3 !important;
    }
    
    /* Additional global metric targeting */
    .analytics-section .metric-container *,
    .analytics-section .stMetric *,
    .analytics-section [class*="metric"] *,
    .analytics-section [class*="Metric"] * {
        font-size: 0.75em !important;
        white-space: normal !important;
        text-overflow: unset !important;
        overflow: visible !important;
    }
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .book-card {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: box-shadow 0.2s ease;
    }
    .book-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .book-compact {
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 0.25rem;
        transition: all 0.2s ease;
        min-height: auto;
    }
    .book-compact:hover {
        background: rgba(0, 0, 0, 0.02);
    }
    .book-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.25rem;
        line-height: 1.3;
    }
    .book-meta {
        font-size: 0.9rem;
        color: #6c757d;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    .book-rating {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        margin-bottom: 0.25rem;
    }
    .quick-info {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.25rem;
        font-size: 0.85rem;
    }
    .rank-compact {
        background: #e3f2fd;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        color: #1565c0;
    }
    .expand-toggle {
        background: none;
        border: none;
        color: #1f77b4;
        cursor: pointer;
        font-size: 0.8rem;
        padding: 0.25rem 0;
        text-decoration: underline;
    }
    .expand-toggle:hover {
        color: #0d47a1;
    }
    /* Accessibility improvements */
    .book-card:focus-within {
        outline: 2px solid #1f77b4;
        outline-offset: 2px;
    }
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        border: 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    /* Hide browser autocomplete suggestions and floating text */
    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus,
    input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 30px white inset !important;
        -webkit-text-fill-color: #333 !important;
    }
    /* Hide browser autocomplete dropdown */
    input::-webkit-search-cancel-button,
    input::-webkit-search-decoration {
        -webkit-appearance: none;
    }
    /* Disable browser search suggestions */
    .stTextInput input {
        autocomplete: off !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_database():
    """Load database connection with caching"""
    try:
        db = BookDatabase()
        with db:
            if not db.check_table_exists():
                st.error("📊 Database not found! Please run Phase 1 ETL first.")
                st.info("Run: `python phase1-etl/scripts/create_duckdb.py`")
                st.stop()
            return True
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.info("Make sure the database exists in `data/processed/books_data.duckdb`")
        st.stop()

def get_genre_stats(selected_genres=None):
    """Get genre statistics (no caching for dynamic filtering)"""
    db = BookDatabase()
    with db:
        return db.get_genre_stats(selected_genres)

def get_top_books(limit=10, selected_genres=None):
    """Get top books (no caching for dynamic filtering)"""
    db = BookDatabase()
    with db:
        return db.get_top_books(limit, selected_genres)

def get_price_stats(selected_genres=None):
    """Get price statistics (no caching for dynamic filtering)"""
    db = BookDatabase()
    with db:
        return db.get_price_stats(selected_genres)

def search_books(title, author, genre, min_rating, max_rating, min_price, max_price, limit):
    """Search books (not cached for real-time results)"""
    db = BookDatabase()
    with db:
        return db.search_books(title, author, genre, min_rating, max_rating, min_price, max_price, limit)

def get_authors_by_genre(selected_genres=None):
    """Get unique authors by genre (no caching for dynamic filtering)"""
    db = BookDatabase()
    with db:
        return db.get_authors_by_genre(selected_genres)

def main():
    """Main application"""
    
    # Ensure database exists (important for deployment)
    ensure_database_exists()
    
    # Load database
    load_database()
    
    # Header
    st.markdown('<h1 class="main-header">📚 Book Data Explorer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Explore 1,400+ books across 14 genres with interactive analytics</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🔍 Explore Options")
    
    page = st.sidebar.selectbox(
        "Choose a view:",
        ["🏠 Dashboard", "📊 Analytics", "🔍 Search Books", "⭐ Top Rated", "💰 Price Analysis"]
    )
    
    # Global genre filter
    st.sidebar.markdown("---")
    st.sidebar.subheader("📚 Filter by Genre")
    
    db = BookDatabase()
    with db:
        all_genres = db.get_genres()
    
    selected_genres = st.sidebar.multiselect(
        "Select genres to display:",
        options=all_genres,
        default=all_genres,
        help="Choose one or more genres to filter the data. Default shows all genres."
    )
    
    if page == "🏠 Dashboard":
        show_dashboard(selected_genres)
    elif page == "📊 Analytics":
        show_analytics(selected_genres)
    elif page == "🔍 Search Books":
        show_search(selected_genres)
    elif page == "⭐ Top Rated":
        show_top_books(selected_genres)
    elif page == "💰 Price Analysis":
        show_price_analysis(selected_genres)

def show_dashboard(selected_genres):
    """Dashboard overview"""
    
    if not selected_genres:
        st.warning("Please select at least one genre to display data.")
        return
    
    # Get basic stats
    db = BookDatabase()
    with db:
        total_books = db.get_books_count(selected_genres)
        genres = selected_genres if selected_genres else db.get_genres()
    
    price_stats = get_price_stats(selected_genres)
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h2>{total_books:,}</h2>
            <p>Total Books</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h2>{len(genres)}</h2>
            <p>Genres</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <h2>${price_stats['average']:.2f}</h2>
            <p>Avg Price</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Genre distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Unique Authors by Genre")
        authors_stats = get_authors_by_genre(selected_genres)
        df_authors = pd.DataFrame(authors_stats)
        
        fig = px.bar(
            df_authors, 
            x='unique_authors', 
            y='genre',
            orientation='h',
            color='unique_authors',
            color_continuous_scale='viridis',
            title="Number of Unique Authors per Genre"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⭐ Average Rating by Genre")
        genre_stats = get_genre_stats(selected_genres)
        df_genres = pd.DataFrame(genre_stats)
        
        fig = px.bar(
            df_genres, 
            x='avg_rating', 
            y='genre',
            orientation='h',
            color='avg_rating',
            color_continuous_scale='plasma',
            title="Average Rating per Genre"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

def calculate_market_metrics(df):
    """Calculate author-focused market metrics with explanations"""
    
    # Market Opportunity Index (MOI)
    # Formula: (avg_price * avg_reviews * avg_rating) / book_count
    # Higher = better revenue potential with less competition
    df['market_opportunity'] = (df['avg_price'] * df['avg_reviews'] * df['avg_rating']) / df['book_count']
    
    # Competition Level
    # Formula: book_count / max(book_count) * 100
    # Higher = more competitive (more books in genre)
    df['competition_level'] = (df['book_count'] / df['book_count'].max()) * 100
    
    # Quality Threshold
    # Formula: avg_rating weighted by review volume
    # Shows minimum quality expectations for success
    df['quality_threshold'] = df['avg_rating'] * (df['avg_reviews'] / df['avg_reviews'].max())
    
    # Revenue Potential
    # Formula: avg_price * avg_reviews (proxy for sales volume)
    # Higher = better earning potential
    df['revenue_potential'] = df['avg_price'] * df['avg_reviews']
    
    # Market Entry Difficulty
    # Formula: (competition_level + quality_threshold) / 2
    # Higher = harder to break into
    df['entry_difficulty'] = (df['competition_level'] + (df['quality_threshold'] * 20)) / 2
    
    return df

def show_analytics(selected_genres):
    """Author-focused market analytics with interpretations"""
    
    if not selected_genres:
        st.warning("Please select at least one genre to display data.")
        return
    
    st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
    st.header("📊 Author Market Intelligence")
    st.markdown("*Analytics designed to help authors make data-driven decisions about their next book.*")
    
    genre_stats = get_genre_stats(selected_genres)
    df = pd.DataFrame(genre_stats)
    
    if df.empty:
        st.warning("No data available for selected genres.")
        return
    
    # Calculate market metrics
    df = calculate_market_metrics(df)
    
    # Market Overview Dashboard
    st.subheader("🎯 Market Opportunity Overview")
    
    # Custom function to create metric with tooltip
    def create_metric_with_tooltip(label, value, delta, tooltip_text):
        """Create a custom metric card with tooltip"""
        # Don't truncate - let it wrap
        display_value = value
        
        return f"""
        <div style="background-color: #262730; padding: 1rem; border-radius: 0.5rem; height: 100%; min-height: 120px;">
            <div style="color: #808495; font-size: 0.9rem; margin-bottom: 0.25rem;">{label}</div>
            <div title="{tooltip_text}" style="
                color: #fafafa; 
                font-size: 1.2rem; 
                font-weight: bold; 
                cursor: help; 
                margin-bottom: 0.25rem;
                word-wrap: break-word;
                overflow-wrap: break-word;
                white-space: normal;
                line-height: 1.3;
                min-height: 2.4rem;
            ">
                {display_value}
            </div>
            <div style="color: #5ec85e; font-size: 0.9rem;">↑ {delta}</div>
        </div>
        """
    
    # First row - 2 columns
    col1, col2 = st.columns(2)
    
    # Best opportunity
    best_opportunity = df.loc[df['market_opportunity'].idxmax()]
    with col1:
        st.markdown(
            create_metric_with_tooltip(
                "🏆 Best Opportunity",
                best_opportunity['genre'],
                f"MOI: {best_opportunity['market_opportunity']:.0f}",
                f"Genre: {best_opportunity['genre']}"
            ),
            unsafe_allow_html=True
        )
    
    # Highest revenue potential
    best_revenue = df.loc[df['revenue_potential'].idxmax()]
    with col2:
        st.markdown(
            create_metric_with_tooltip(
                "💰 Highest Revenue",
                best_revenue['genre'],
                f"${best_revenue['revenue_potential']:.0f}",
                f"Genre: {best_revenue['genre']}"
            ),
            unsafe_allow_html=True
        )
    
    # Add vertical spacing between rows
    st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
    
    # Second row - 2 columns
    col3, col4 = st.columns(2)
    
    # Lowest competition
    lowest_competition = df.loc[df['competition_level'].idxmin()]
    with col3:
        st.markdown(
            create_metric_with_tooltip(
                "🎯 Least Competitive",
                lowest_competition['genre'],
                f"{lowest_competition['competition_level']:.0f}% full",
                f"Genre: {lowest_competition['genre']}"
            ),
            unsafe_allow_html=True
        )
    
    # Easiest entry
    easiest_entry = df.loc[df['entry_difficulty'].idxmin()]
    with col4:
        st.markdown(
            create_metric_with_tooltip(
                "🚀 Easiest Entry",
                easiest_entry['genre'],
                f"{easiest_entry['entry_difficulty']:.0f}% difficulty",
                f"Genre: {easiest_entry['genre']}"
            ),
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Key Insights for Authors
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Market Opportunity Index")
        
        # Sort by market opportunity
        df_sorted = df.sort_values('market_opportunity', ascending=True)
        
        fig = px.bar(
            df_sorted,
            x='market_opportunity',
            y='genre',
            orientation='h',
            color='market_opportunity',
            color_continuous_scale='RdYlGn',
            title="Market Opportunity by Genre",
            labels={'market_opportunity': 'Market Opportunity Index'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📖 How to Interpret Market Opportunity Index"):
            st.markdown("""
            **Calculation:** `(Average Price × Average Reviews × Average Rating) ÷ Number of Books`
            
            **What it means:**
            - Higher values = better opportunity for new authors
            - Combines revenue potential with competition level
            - Green bars = high opportunity, red bars = saturated markets
            
            **How to use:**
            - Target genres with highest MOI scores
            - Avoid oversaturated markets (red bars)
            - Consider your writing strengths vs. opportunity
            """)
    
    with col2:
        st.subheader("⚔️ Competition vs Revenue")
        
        fig = px.scatter(
            df,
            x='competition_level',
            y='revenue_potential',
            size='avg_rating',
            color='genre',
            hover_name='genre',
            hover_data=['book_count', 'avg_price', 'avg_reviews'],
            title="Competition Level vs Revenue Potential",
            labels={
                'competition_level': 'Competition Level (%)',
                'revenue_potential': 'Revenue Potential ($)'
            }
        )
        
        # Add quadrant lines
        fig.add_hline(y=df['revenue_potential'].median(), line_dash="dash", line_color="gray")
        fig.add_vline(x=df['competition_level'].median(), line_dash="dash", line_color="gray")
        
        # Set same height as the first chart for alignment
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📖 How to Interpret Competition vs Revenue"):
            st.markdown("""
            **Quadrants:**
            - **Top Left** (low competition, high revenue) = 🎯 **IDEAL TARGETS**
            - **Top Right** (high competition, high revenue) = 💪 **COMPETITIVE MARKETS**
            - **Bottom Left** (low competition, low revenue) = 🤔 **NICHE MARKETS**
            - **Bottom Right** (high competition, low revenue) = ❌ **AVOID**
            
            **Bubble size** = Average rating (larger = higher quality expected)
            """)
    
    # Author Success Thresholds
    st.subheader("🎯 Success Thresholds by Genre")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Quality & Price Analysis")
        
        fig = px.scatter(
            df,
            x='avg_rating',
            y='avg_price',
            size='avg_reviews',
            color='competition_level',
            hover_name='genre',
            title="Rating vs Price (Bubble = Review Volume)",
            labels={
                'avg_rating': 'Average Rating',
                'avg_price': 'Average Price ($)',
                'competition_level': 'Competition Level'
            },
            color_continuous_scale='RdYlBu_r'
        )
        # Set same height as the second chart for alignment
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📖 How to Use Quality & Price Analysis"):
            st.markdown("""
            **What to look for:**
            - **High rating + High price** = Premium positioning possible
            - **Large bubbles** = High review volume (engaged readers)
            - **Blue dots** = Less competitive (easier entry)
            - **Red dots** = Highly competitive (need strong differentiation)
            
            **Strategy tips:**
            - Price slightly below genre average initially
            - Aim for rating above genre average
            - Consider review volume as engagement indicator
            """)
    
    with col2:
        st.subheader("🚀 Market Entry Difficulty")
        
        df_entry = df.sort_values('entry_difficulty', ascending=True)
        
        fig = px.bar(
            df_entry,
            x='entry_difficulty',
            y='genre',
            orientation='h',
            color='entry_difficulty',
            color_continuous_scale='RdYlGn_r',
            title="Market Entry Difficulty Score",
            labels={'entry_difficulty': 'Entry Difficulty (%)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📖 How to Interpret Entry Difficulty"):
            st.markdown("""
            **Calculation:** `(Competition Level + Quality Expectations) ÷ 2`
            
            **Difficulty levels:**
            - **0-25%** = 🟢 **BEGINNER FRIENDLY** - Lower competition, achievable quality standards
            - **26-50%** = 🟡 **MODERATE** - Some competition, decent quality needed
            - **51-75%** = 🟠 **CHALLENGING** - High competition or quality standards
            - **76-100%** = 🔴 **EXPERT LEVEL** - Saturated market with high expectations
            
            **Green bars** = easier markets for new authors to enter
            """)
    
    # Actionable Recommendations
    st.subheader("💡 Data-Driven Recommendations")
    
    # Generate recommendations
    recommendations = []
    
    # Best opportunity
    top_opportunity = df.nlargest(2, 'market_opportunity')
    for _, row in top_opportunity.iterrows():
        recommendations.append(f"🎯 **{row['genre']}** shows strong market opportunity (MOI: {row['market_opportunity']:.0f}) with ${row['avg_price']:.2f} average pricing")
    
    # Low competition opportunities
    low_competition = df[df['competition_level'] < df['competition_level'].median()]
    if not low_competition.empty:
        best_low_comp = low_competition.loc[low_competition['revenue_potential'].idxmax()]
        recommendations.append(f"🚀 **{best_low_comp['genre']}** has lower competition ({best_low_comp['competition_level']:.0f}%) with good revenue potential")
    
    # Quality threshold insights
    high_standards = df[df['avg_rating'] > 4.5]
    if not high_standards.empty:
        recommendations.append(f"⭐ High-quality genres like **{', '.join(high_standards['genre'].head(2))}** expect {high_standards['avg_rating'].mean():.1f}+ star ratings")
    
    # Price insights
    price_range = f"💰 Optimal pricing ranges from ${df['avg_price'].min():.2f} to ${df['avg_price'].max():.2f}, with most genres averaging ${df['avg_price'].median():.2f}"
    recommendations.append(price_range)
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")
    
    st.markdown("---")
    st.caption("📊 Data based on current bestseller rankings and market performance. Update frequency varies by data source.")
    st.markdown('</div>', unsafe_allow_html=True)

def show_search(selected_genres):
    """Search interface"""
    st.header("🔍 Search Books")
    
    # Search filters
    col1, col2 = st.columns(2)
    
    with col1:
        title_search = st.text_input("📖 Book Title", placeholder="Enter title keywords...", key="book_title_search")
        author_search = st.text_input("✍️ Author Name", placeholder="Enter author name...", key="author_name_search")
    
    with col2:
        # Use selected genres for dropdown, but allow "All" option
        db = BookDatabase()
        with db:
            all_available_genres = db.get_genres()
        available_genres = ["All"] + (selected_genres if selected_genres else all_available_genres)
        genre_filter = st.selectbox("📚 Genre", available_genres)
        
        rating_range = st.slider("⭐ Rating Range", 0.0, 5.0, (0.0, 5.0), 0.1)
    
    col3, col4 = st.columns(2)
    with col3:
        price_range = st.slider("💰 Price Range", 0, 100, (0, 100), 1)
    with col4:
        limit = st.slider("📊 Results Limit", 10, 500, 50)
    
    # Search button
    if st.button("🔍 Search Books", type="primary"):
        with st.spinner("Searching..."):
            # Apply global genre filter to search
            effective_genre = genre_filter if genre_filter != "All" else None
            if selected_genres and effective_genre and effective_genre not in selected_genres:
                st.warning(f"Selected genre '{effective_genre}' is not in your current genre filter. Showing all selected genres instead.")
                effective_genre = None
            
            min_rating, max_rating = rating_range
            min_price, max_price = price_range
            results = search_books(title_search, author_search, effective_genre, min_rating, max_rating, min_price, max_price, limit)
            
            # Filter results to only show books from selected genres
            if selected_genres and results:
                results = [book for book in results if book['genre'] in selected_genres]
        
        if results:
            st.success(f"Found {len(results)} books")
            
            # Display results with cover images
            for book in results:
                display_book_with_cover(book)
        else:
            st.warning("No books found matching your criteria")

def show_top_books(selected_genres):
    """Top rated books"""
    
    if not selected_genres:
        st.warning("Please select at least one genre to display data.")
        return
    st.header("⭐ Top Rated Books")
    
    limit = st.slider("Number of books to show", 5, 50, 20)
    
    top_books = get_top_books(limit, selected_genres)
    
    for i, book in enumerate(top_books, 1):
        display_book_with_cover(book, rank=i)

def show_price_analysis(selected_genres):
    """Price analysis dashboard"""
    
    if not selected_genres:
        st.warning("Please select at least one genre to display data.")
        return
    st.header("💰 Price Analysis")
    st.markdown("*Understanding pricing strategies and market positioning across genres*")
    
    # Get price data and stats
    db = BookDatabase()
    with db:
        price_data = db.get_price_data_by_genre(selected_genres)
    
    df_prices = pd.DataFrame(price_data, columns=['genre', 'price'])
    price_stats = get_price_stats(selected_genres)
    
    # Create two columns for the main charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Price Distribution by Genre")
        
        # Box plot with enhanced styling
        fig = px.box(
            df_prices, 
            x='genre', 
            y='price',
            title="Price Range and Outliers by Genre",
            color='genre',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_xaxes(tickangle=45)
        fig.update_layout(
            height=400,
            bargap=0.3,  # Add spacing between boxes
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📖 How to Read Box Plots"):
            st.markdown("""
            **Box Plot Components:**
            - **Box** = Middle 50% of prices (25th to 75th percentile)
            - **Line in box** = Median price
            - **Whiskers** = Range of typical prices
            - **Dots** = Outliers (unusually high/low prices)
            
            **What to look for:**
            - **Wide boxes** = High price variation within genre
            - **High medians** = Premium pricing opportunities
            - **Many outliers above** = Super-premium market exists
            """)
    
    with col2:
        st.subheader("📈 Overall Price Distribution")
        
        # Enhanced histogram with count-based color intensity
        fig = px.histogram(
            df_prices, 
            x='price', 
            nbins=25,
            title="Frequency of Books at Different Price Points",
            color_discrete_sequence=['#2E86AB'],
            marginal="rug"  # Add rug plot to show individual data points
        )
        
        # Intensify colors based on count
        fig.update_traces(
            marker_color='#2E86AB',
            marker_line_color='white',
            marker_line_width=1,
            opacity=0.8
        )
        
        fig.update_layout(
            height=400,
            bargap=0.2,  # Add spacing between bars
            xaxis_title="Price ($)",
            yaxis_title="Number of Books"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📖 How to Use Price Distribution"):
            st.markdown("""
            **What this shows:**
            - **Peak areas** = Most common price points in market
            - **Gaps** = Underserved price segments (opportunities)
            - **Long tail** = Premium pricing potential
            
            **Pricing strategy tips:**
            - **Price near peaks** = Compete in crowded segments
            - **Price in gaps** = Stand out from competition
            - **Consider genre medians** = Stay competitive within your genre
            """)
    
    st.markdown("---")
    
    # Price statistics with enhanced presentation
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🎯 Key Price Metrics")
        
        # Create enhanced metrics display
        metrics_html = f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white;">
                <h3 style="margin: 0; font-size: 1.2rem;">Average Price</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold;">${price_stats['average']:.2f}</p>
            </div>
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1rem; border-radius: 8px; color: white;">
                <h3 style="margin: 0; font-size: 1.2rem;">Median Price</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold;">${price_stats['median']:.2f}</p>
            </div>
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1rem; border-radius: 8px; color: white;">
                <h3 style="margin: 0; font-size: 1.2rem;">Lowest Price</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold;">${price_stats['min']:.2f}</p>
            </div>
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1rem; border-radius: 8px; color: white;">
                <h3 style="margin: 0; font-size: 1.2rem;">Highest Price</h3>
                <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold;">${price_stats['max']:.2f}</p>
            </div>
        </div>
        """
        st.markdown(metrics_html, unsafe_allow_html=True)
        
    
    with col4:
        st.subheader("💡 Pricing Insights")
        
        # Generate dynamic insights
        insights = []
        
        # Price spread analysis
        price_spread = price_stats['max'] - price_stats['min']
        avg_vs_median = price_stats['average'] - price_stats['median']
        
        if avg_vs_median > 1.0:
            insights.append("📈 **High-value outliers detected** - Premium pricing opportunities exist in these genres")
        elif avg_vs_median < -0.5:
            insights.append("📉 **Budget-focused market** - Most books are priced below average, suggesting price-sensitive readers")
        else:
            insights.append("⚖️ **Balanced pricing** - Market shows healthy distribution across price points")
        
        if price_spread > 20:
            insights.append("🎯 **Wide price range** - Multiple market segments from budget ($%.2f) to premium ($%.2f)" % (price_stats['min'], price_stats['max']))
        else:
            insights.append("🎯 **Narrow price range** - Concentrated market with limited pricing flexibility")
        
        # Recommendation based on median
        if price_stats['median'] < 5:
            insights.append("💰 **Budget market dominance** - Consider competitive pricing under $%.2f for maximum reach" % (price_stats['median'] + 1))
        elif price_stats['median'] > 15:
            insights.append("💎 **Premium market** - Readers willing to pay $%.2f+ - focus on value and quality" % price_stats['median'])
        else:
            insights.append("🎪 **Mid-market sweet spot** - $%.2f-$%.2f range offers good balance of accessibility and value" % (price_stats['median'] - 2, price_stats['median'] + 2))
        
        for i, insight in enumerate(insights, 1):
            st.markdown(f"{i}. {insight}")
    
    # Add horizontal line to separate content from expanders
    st.markdown("---")
    
    # Now create aligned expander section
    col5, col6 = st.columns(2)
    
    with col5:
        with st.expander("📖 Understanding Price Metrics"):
            st.markdown("""
            **Key differences:**
            - **Average** = Total value ÷ number of books (affected by outliers)
            - **Median** = Middle price when all prices are sorted (more representative)
            - **Range** = Shows market breadth from budget to premium
            
            **For pricing decisions:**
            - **Price near median** = Appeal to typical buyers
            - **Price above average** = Target premium market
            - **Consider the range** = Understand competitive landscape
            """)
    
    with col6:
        with st.expander("📖 How to Use These Insights"):
            st.markdown("""
            **For new authors:**
            - **Start near median price** = Proven acceptable price point
            - **Test premium pricing** = If quality justifies it
            - **Monitor competitor pricing** = Stay within market expectations
            
            **For established authors:**
            - **Premium positioning** = Charge above median if you have following
            - **Value pricing** = Below median for wider market reach
            - **Series pricing** = First book lower, sequels at median+
            """)
    
    st.markdown("---")
    st.caption("💡 **Tip:** Use these insights alongside your genre's specific data to make informed pricing decisions that balance accessibility with profitability.")

if __name__ == "__main__":
    main()