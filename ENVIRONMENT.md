# 🔧 Environment Configuration Guide

## Overview

This project uses environment variables for flexible configuration across different deployment environments. Configuration is managed through `.env` files and environment variables.

## 📁 Configuration Files

```
Lab-5b-ffa/
├── .env.template     # Complete template with all options
├── .env.example      # Common configuration examples  
├── .env             # Your local config (gitignored)
└── shared/config.py  # Configuration management code
```

## 🚀 Quick Setup

### 1. Create Your Environment File
```bash
# Copy template and customize
cp .env.template .env

# Or use the minimal example
cp .env.example .env
```

### 2. Install python-dotenv
```bash
# Included in requirements.txt
pip install python-dotenv

# Or install individually  
pip install python-dotenv==1.0.0
```

### 3. Customize Configuration
Edit `.env` for your environment:
```bash
# Essential settings
DB_PATH=data/processed/books_data.duckdb
APP_ENV=development
DEBUG=true
```

## ⚙️ Configuration Categories

### 🗄️ Database Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `data/processed/books_data.duckdb` | Database file path |
| `DB_TIMEOUT` | `30` | Connection timeout (seconds) |
| `DB_POOLING` | `true` | Enable connection pooling |
| `CLOUD_DB_URL` | - | Cloud database URL override |

**Examples:**
```bash
# Local development
DB_PATH=data/processed/books_data.duckdb

# Cloud deployment
DB_PATH=books_data.duckdb  
CLOUD_DB_URL=https://storage.cloud.com/books.duckdb
```

### 🎯 Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | Environment (dev/staging/prod) |
| `DEBUG` | `true` | Enable debug mode |
| `APP_TITLE` | `Book Data Explorer` | Application title |
| `MAX_SEARCH_RESULTS` | `100` | Maximum search results |
| `DEFAULT_PAGE_SIZE` | `20` | Default pagination size |

### 🌐 Streamlit Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `STREAMLIT_PORT` | `8501` | Server port |
| `STREAMLIT_HOST` | `localhost` | Server host |
| `STREAMLIT_GATHER_USAGE_STATS` | `false` | Usage analytics |
| `STREAMLIT_PRIMARY_COLOR` | `#1f77b4` | Theme primary color |

### ⚡ Performance Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_CACHING` | `true` | Enable query caching |
| `CACHE_TTL` | `3600` | Cache time-to-live (seconds) |
| `MAX_CACHE_SIZE` | `100` | Maximum cache size (MB) |
| `ENABLE_MONITORING` | `false` | Performance monitoring |

### ☁️ Cloud Deployment

| Variable | Default | Description |
|----------|---------|-------------|
| `CLOUD_PLATFORM` | - | Platform (streamlit_cloud, railway, render) |
| `CLOUD_OPTIMIZATIONS` | `false` | Enable cloud-specific optimizations |

### 🚦 Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_EXPERIMENTAL` | `false` | Experimental features |
| `ENABLE_EXPORT` | `true` | Data export functionality |
| `ENABLE_FAVORITES` | `false` | User favorites system |
| `ENABLE_ADVANCED_SEARCH` | `true` | Advanced search filters |
| `ENABLE_PRICE_ALERTS` | `false` | Price monitoring alerts |

### 📊 Logging & Monitoring

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | - | Log file path (empty = console) |
| `LOG_QUERIES` | `false` | Log SQL queries |
| `LOG_PERFORMANCE` | `false` | Log performance metrics |

## 🌍 Environment Examples

### Local Development
```bash
# .env for local development
DB_PATH=data/processed/books_data.duckdb
APP_ENV=development
DEBUG=true
STREAMLIT_PORT=8501
STREAMLIT_HOST=localhost
ENABLE_CACHING=true
LOG_LEVEL=INFO
```

### Streamlit Cloud
```bash  
# .env for Streamlit Cloud
DB_PATH=books_data.duckdb
APP_ENV=production
DEBUG=false
CLOUD_PLATFORM=streamlit_cloud
CLOUD_OPTIMIZATIONS=true
STREAMLIT_GATHER_USAGE_STATS=false
ENABLE_CACHING=true
LOG_LEVEL=WARNING
```

### Railway Deployment
```bash
# .env for Railway
DB_PATH=books_data.duckdb  
APP_ENV=production
DEBUG=false
CLOUD_PLATFORM=railway
STREAMLIT_PORT=$PORT
STREAMLIT_HOST=0.0.0.0
CLOUD_OPTIMIZATIONS=true
LOG_LEVEL=WARNING
```

### Docker Deployment
```bash
# .env for Docker
DB_PATH=/app/data/books_data.duckdb
APP_ENV=production
DEBUG=false
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0
ENABLE_CACHING=true
MAX_CACHE_SIZE=50
LOG_LEVEL=INFO
```

## 🔑 API Keys (Future Features)

Ready for external service integration:

```bash
# Google Books API (for enhanced book data)
GOOGLE_BOOKS_API_KEY=your_api_key_here

# Goodreads API (for reviews)
GOODREADS_API_KEY=your_api_key_here

# Analytics service
ANALYTICS_KEY=your_analytics_key_here
```

## 🛠️ Usage in Code

### Loading Configuration
```python
from shared.config import get_config

# Get global configuration
config = get_config()

# Access settings
db_path = config.db_path
app_title = config.app_title
debug_mode = config.debug
```

### Feature Flags
```python
from shared.config import get_config

config = get_config()

# Conditional features
if config.enable_experimental:
    show_experimental_features()

if config.enable_export:
    add_export_button()
```

### Database Configuration
```python
from shared.database import BookDatabase

# Automatically uses configuration
db = BookDatabase()  # Uses config.db_path

# Or override
db = BookDatabase(db_path="custom/path.duckdb")
```

## 🔍 Configuration Validation

The system automatically validates configuration:

```python
from shared.config import get_config, validate_config

config = get_config()
warnings = validate_config(config)

for warning in warnings:
    print(f"Warning: {warning}")
```

Common validation checks:
- ✅ Database file exists
- ✅ Port number is valid  
- ✅ Log level is recognized
- ✅ Cache settings are reasonable

## 🚨 Troubleshooting

### "Database not found"
```bash
# Check DB_PATH setting
echo $DB_PATH

# Verify file exists
ls -la data/processed/books_data.duckdb

# Run Phase 1 ETL if missing
cd phase1-etl && ./scripts/run_processing.sh
```

### "Configuration not loading"
```bash
# Install python-dotenv
pip install python-dotenv

# Check .env file exists
ls -la .env

# Verify file format (no spaces around =)
cat .env | grep "="
```

### "Port already in use"
```bash
# Change port in .env
echo "STREAMLIT_PORT=8502" >> .env

# Or find and kill process
lsof -ti:8501 | xargs kill
```

## 🔐 Security Best Practices

### ✅ Do:
- Keep `.env` files gitignored
- Use different configurations per environment
- Rotate API keys regularly
- Use environment variables in production

### ❌ Don't:
- Commit `.env` files to git
- Store secrets in code
- Use production settings in development
- Share API keys in documentation

## 📚 Advanced Usage

### Environment Inheritance
```bash
# Base configuration
cp .env.template .env.base

# Environment-specific overrides
cp .env.base .env.development
cp .env.base .env.production

# Load specific environment
export APP_ENV=production
```

### Dynamic Configuration
```python
import os
from shared.config import reload_config

# Change environment at runtime
os.environ['DEBUG'] = 'false'
config = reload_config()  # Reload with new settings
```

### Testing Configuration
```python
import unittest
from shared.config import Config

class TestConfig(unittest.TestCase):
    def test_default_values(self):
        config = Config(...)
        self.assertEqual(config.app_env, 'development')
        self.assertTrue(config.debug)
```

## 🎯 Next Steps

1. **Copy template**: `cp .env.template .env`
2. **Customize settings** for your environment
3. **Test locally**: `streamlit run phase2-webapp/app/main.py`
4. **Deploy to cloud** with production settings
5. **Monitor and adjust** based on usage patterns

This configuration system makes your application flexible, secure, and ready for any deployment scenario! 🚀