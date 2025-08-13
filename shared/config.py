"""
Configuration management for Book Data Processing project
Handles environment variables, defaults, and validation
"""

import os
import logging
from pathlib import Path
from typing import Any, Optional, Union
from dataclasses import dataclass

# Try to import python-dotenv, but don't require it
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration class with environment variable support"""
    
    # Database settings
    db_path: str
    db_timeout: int
    db_pooling: bool
    
    # Application settings
    app_env: str
    debug: bool
    app_title: str
    max_search_results: int
    default_page_size: int
    
    # Streamlit settings
    streamlit_port: int
    streamlit_host: str
    streamlit_gather_usage_stats: bool
    streamlit_primary_color: str
    
    # Performance settings
    enable_caching: bool
    cache_ttl: int
    max_cache_size: int
    enable_monitoring: bool
    
    # Cloud settings
    cloud_platform: Optional[str]
    cloud_db_url: Optional[str]
    cloud_optimizations: bool
    
    # Feature flags
    enable_experimental: bool
    enable_export: bool
    enable_favorites: bool
    enable_advanced_search: bool
    enable_price_alerts: bool
    
    # Logging settings
    log_level: str
    log_file: Optional[str]
    log_queries: bool
    log_performance: bool
    
    # API keys (future use)
    google_books_api_key: Optional[str]
    goodreads_api_key: Optional[str]
    analytics_key: Optional[str]

def get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean environment variable"""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')

def get_int_env(key: str, default: int = 0) -> int:
    """Get integer environment variable"""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        logger.warning(f"Invalid integer value for {key}, using default: {default}")
        return default

def get_str_env(key: str, default: str = "") -> str:
    """Get string environment variable"""
    return os.getenv(key, default)

def get_optional_str_env(key: str) -> Optional[str]:
    """Get optional string environment variable"""
    value = os.getenv(key)
    return value if value and value.strip() else None

def load_config() -> Config:
    """Load configuration from environment variables and .env file"""
    
    # Load .env file if available
    if DOTENV_AVAILABLE:
        # Look for .env file in project root
        project_root = Path(__file__).parent.parent
        env_file = project_root / '.env'
        
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded environment from: {env_file}")
        else:
            logger.info("No .env file found, using system environment variables")
    else:
        logger.warning("python-dotenv not installed, .env files will be ignored")
        logger.info("Install with: pip install python-dotenv")
    
    # Determine smart database path
    db_path = get_database_path()
    
    # Load all configuration
    config = Config(
        # Database settings
        db_path=db_path,
        db_timeout=get_int_env('DB_TIMEOUT', 30),
        db_pooling=get_bool_env('DB_POOLING', True),
        
        # Application settings
        app_env=get_str_env('APP_ENV', 'development'),
        debug=get_bool_env('DEBUG', True),
        app_title=get_str_env('APP_TITLE', 'Book Data Explorer'),
        max_search_results=get_int_env('MAX_SEARCH_RESULTS', 100),
        default_page_size=get_int_env('DEFAULT_PAGE_SIZE', 20),
        
        # Streamlit settings
        streamlit_port=get_int_env('STREAMLIT_PORT', 8501),
        streamlit_host=get_str_env('STREAMLIT_HOST', 'localhost'),
        streamlit_gather_usage_stats=get_bool_env('STREAMLIT_GATHER_USAGE_STATS', False),
        streamlit_primary_color=get_str_env('STREAMLIT_PRIMARY_COLOR', '#1f77b4'),
        
        # Performance settings
        enable_caching=get_bool_env('ENABLE_CACHING', True),
        cache_ttl=get_int_env('CACHE_TTL', 3600),
        max_cache_size=get_int_env('MAX_CACHE_SIZE', 100),
        enable_monitoring=get_bool_env('ENABLE_MONITORING', False),
        
        # Cloud settings
        cloud_platform=get_optional_str_env('CLOUD_PLATFORM'),
        cloud_db_url=get_optional_str_env('CLOUD_DB_URL'),
        cloud_optimizations=get_bool_env('CLOUD_OPTIMIZATIONS', False),
        
        # Feature flags
        enable_experimental=get_bool_env('ENABLE_EXPERIMENTAL', False),
        enable_export=get_bool_env('ENABLE_EXPORT', True),
        enable_favorites=get_bool_env('ENABLE_FAVORITES', False),
        enable_advanced_search=get_bool_env('ENABLE_ADVANCED_SEARCH', True),
        enable_price_alerts=get_bool_env('ENABLE_PRICE_ALERTS', False),
        
        # Logging settings
        log_level=get_str_env('LOG_LEVEL', 'INFO'),
        log_file=get_optional_str_env('LOG_FILE'),
        log_queries=get_bool_env('LOG_QUERIES', False),
        log_performance=get_bool_env('LOG_PERFORMANCE', False),
        
        # API keys
        google_books_api_key=get_optional_str_env('GOOGLE_BOOKS_API_KEY'),
        goodreads_api_key=get_optional_str_env('GOODREADS_API_KEY'),
        analytics_key=get_optional_str_env('ANALYTICS_KEY'),
    )
    
    # Log configuration summary
    logger.info(f"Configuration loaded:")
    logger.info(f"  Environment: {config.app_env}")
    logger.info(f"  Debug mode: {config.debug}")
    logger.info(f"  Database: {config.db_path}")
    logger.info(f"  Cloud platform: {config.cloud_platform or 'none'}")
    
    return config

def get_database_path() -> str:
    """Smart database path detection with environment variable support"""
    
    # Check explicit environment variable first
    env_db_path = get_str_env('DB_PATH')
    if env_db_path:
        return env_db_path
    
    # Check for cloud-specific configurations
    cloud_db_url = get_optional_str_env('CLOUD_DB_URL')
    if cloud_db_url:
        return cloud_db_url
    
    # Cloud platform detection
    if os.environ.get('STREAMLIT_SHARING') or get_str_env('CLOUD_PLATFORM') == 'streamlit_cloud':
        return "books_data.duckdb"
    
    if get_str_env('CLOUD_PLATFORM') in ['railway', 'render', 'heroku']:
        return "books_data.duckdb"
    
    # Local development paths
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    
    possible_paths = [
        project_root / "data" / "processed" / "books_data.duckdb",
        project_root / "books_data.duckdb",
        "books_data.duckdb"
    ]
    
    for path in possible_paths:
        if path.exists() if isinstance(path, Path) else Path(path).exists():
            return str(path)
    
    # Default path for new installations
    return str(project_root / "data" / "processed" / "books_data.duckdb")

def validate_config(config: Config) -> list[str]:
    """Validate configuration and return list of warnings/errors"""
    warnings = []
    
    # Validate database path
    db_path = Path(config.db_path)
    if not db_path.exists() and not config.cloud_db_url:
        warnings.append(f"Database file not found: {config.db_path}")
        warnings.append("Run Phase 1 ETL to create the database")
    
    # Validate port range
    if not (1024 <= config.streamlit_port <= 65535):
        warnings.append(f"Invalid port number: {config.streamlit_port}")
    
    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if config.log_level.upper() not in valid_log_levels:
        warnings.append(f"Invalid log level: {config.log_level}")
    
    # Validate cache settings
    if config.cache_ttl < 0:
        warnings.append("Cache TTL cannot be negative")
    
    if config.max_search_results > 1000:
        warnings.append("Large search result limits may impact performance")
    
    return warnings

# Global configuration instance
_config: Optional[Config] = None

def get_config() -> Config:
    """Get global configuration instance (singleton pattern)"""
    global _config
    if _config is None:
        _config = load_config()
        
        # Validate configuration
        warnings = validate_config(_config)
        for warning in warnings:
            logger.warning(warning)
    
    return _config

def reload_config() -> Config:
    """Reload configuration (useful for testing)"""
    global _config
    _config = None
    return get_config()