# 🚀 Deployment Guide

## Overview
This project is designed to work both locally (for development and learning) and in the cloud (for sharing and portfolios).

## 🏠 Local Development

### Quick Start
```bash
# 1. Complete Phase 1 (ETL)
cd phase1-etl
./scripts/run_processing.sh

# 2. Launch Phase 2 (Web App)  
cd ../phase2-webapp
streamlit run app/main.py
```

Opens automatically at: `http://localhost:8501`

### Development Workflow
```bash
# Make changes to app/main.py
# Streamlit auto-reloads on file save
# Refresh browser to see changes
```

## ☁️ Cloud Deployment

### Option 1: Streamlit Cloud (Recommended)

**Prerequisites**: GitHub repository with your code

1. **Prepare for Deployment**
```bash
# Ensure all files are committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy to Streamlit Cloud**
- Visit [share.streamlit.io](https://share.streamlit.io)
- Connect your GitHub account
- Select your repository
- Set main file path: `phase2-webapp/streamlit_app.py`
- Click "Deploy!"

3. **Configuration**
The app includes:
- `streamlit_app.py` - Entry point for Streamlit Cloud
- `.streamlit/config.toml` - Configuration settings
- `requirements.txt` - Dependencies

**Result**: Public URL like `https://yourapp.streamlit.app`

### Option 2: Railway

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Deploy**
```bash
cd phase2-webapp
railway login
railway init
railway deploy
```

### Option 3: Render

1. **Create `render.yaml`** in project root:
```yaml
services:
  - type: web
    name: book-data-explorer
    env: python
    buildCommand: "pip install -r phase2-webapp/requirements.txt"
    startCommand: "streamlit run phase2-webapp/app/main.py --server.port $PORT --server.address 0.0.0.0"
```

2. **Deploy**
- Connect GitHub repository at [render.com](https://render.com)
- Auto-deploys on git push

## 🗃️ Database in Cloud Deployment

### Challenge: DuckDB File Access
Cloud platforms may not have access to your local `books_data.duckdb` file.

### Solutions:

#### Option A: Include Database in Repository
```bash
# Add database to git (if size < 100MB)
git add data/processed/books_data.duckdb
git commit -m "Add database for deployment"
git push
```

#### Option B: Recreate Database in Cloud
Add this to your deployment:
```bash
# In cloud build process
cd phase1-etl
python3 scripts/create_duckdb.py
```

#### Option C: Use Cloud Storage
Upload database to:
- AWS S3
- Google Cloud Storage  
- Dropbox/OneDrive

Update `shared/database.py` with cloud URL.

## 🔧 Environment Variables

For cloud deployment, set these environment variables:

```bash
# Streamlit Cloud
STREAMLIT_SHARING=true

# Custom database path
DB_PATH=/path/to/your/database.duckdb
```

## 📊 Performance Considerations

### Local Development
- ✅ Fast database access
- ✅ No bandwidth limitations
- ✅ Full debugging capabilities

### Cloud Deployment  
- ⚠️ Potential database access latency
- ⚠️ Memory/CPU limitations on free tiers
- ⚠️ Cold start delays

### Optimization Tips
1. **Use caching**: `@st.cache_data` on expensive queries
2. **Limit results**: Add `LIMIT` clauses to queries
3. **Optimize queries**: Use indexes from Phase 1 ETL
4. **Minimize data transfer**: Only fetch needed columns

## 🐛 Troubleshooting

### "Database not found" in cloud
- Ensure database file is included in deployment
- Check file paths are correct for cloud environment
- Verify database was created in Phase 1

### "Module not found" errors
- Ensure `requirements.txt` includes all dependencies
- Check Python version compatibility

### Performance issues
- Increase cache usage with `@st.cache_data`
- Reduce query complexity
- Consider database optimization

### Cloud platform limits
- **Streamlit Cloud**: 1GB RAM, shared CPU
- **Railway**: Varies by plan
- **Render**: 512MB RAM on free tier

## 📱 Mobile Optimization

The app includes responsive design:
- ✅ Works on phones/tablets
- ✅ Touch-friendly controls
- ✅ Readable on small screens

## 🔒 Security Considerations

### Local Development
- Database contains no sensitive data
- Runs on localhost only

### Cloud Deployment
- App will be publicly accessible
- No authentication required
- Data is read-only

## 📈 Monitoring & Analytics

### Streamlit Cloud
- Built-in usage analytics
- Error tracking
- Performance metrics

### Custom Monitoring
Add to your app:
```python
# Simple usage tracking
st.write(f"Last updated: {datetime.now()}")
```

## 🎯 Success Checklist

### Local Deployment ✅
- [ ] Phase 1 ETL completes successfully
- [ ] Database created in `data/processed/`
- [ ] Web app launches on `localhost:8501`
- [ ] All features work correctly

### Cloud Deployment ✅  
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud deployment successful
- [ ] Public URL accessible
- [ ] Database accessible in cloud
- [ ] All features work in production

## 🚀 Next Steps

1. **Test locally** first to ensure everything works
2. **Deploy to cloud** for sharing and portfolio
3. **Share your success** - add the live URL to your resume!
4. **Iterate and improve** - add new features and visualizations

**Congratulations on building and deploying a complete data application! 🎉**