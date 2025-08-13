# Phase 2: Interactive Web Application

Modern, stylish Streamlit web application for exploring and analyzing book data from the DuckDB database.

## 🎯 Objectives

Learn modern web development and data visualization:
- Interactive dashboard design
- Data visualization with Plotly
- User interface/experience principles
- Real-time data querying
- Local development and cloud deployment

## ✅ Prerequisites

1. **Complete Phase 1**: Database must exist at `../data/processed/books_data.duckdb`
2. **Python Virtual Environment**: Activated with required packages

## 🚀 Quick Start

```bash
# From project root directory
# Install dependencies
pip install -r phase2-webapp/requirements.txt

# Launch the application (run from project root)
streamlit run phase2-webapp/app/main.py
```

**Important**: Always run the web app from the project root directory to ensure proper module imports.

Your browser will automatically open to `http://localhost:8501` 🎉

## 📁 Directory Structure

```
phase2-webapp/
├── README.md           # This file
├── requirements.txt    # Web app dependencies
├── app/
│   └── main.py        # Streamlit application
├── docs/              # Web app documentation
└── (future expansion)
    ├── components/    # Reusable UI components
    ├── pages/        # Multi-page apps
    └── utils/        # Helper functions
```

## 🌟 Application Features

### 📊 Dashboard Views

1. **🏠 Dashboard** - Overview with key metrics and charts
2. **📊 Analytics** - Advanced analysis with correlations  
3. **🔍 Search Books** - Interactive search with multiple filters
4. **⭐ Top Rated** - Highest-rated books across genres
5. **💰 Price Analysis** - Price trends and distributions

### 🎨 Interactive Elements

- **Genre Filtering**: Dropdown selection for specific genres
- **Rating Sliders**: Minimum rating thresholds  
- **Price Range**: Maximum price filtering
- **Search Fields**: Title and author text search
- **Results Limits**: Control number of displayed results
- **Real-time Updates**: Instant results as you modify filters

### 📈 Visualizations

- **Bar Charts**: Books per genre, average ratings
- **Scatter Plots**: Price vs rating, books vs reviews
- **Correlation Heatmap**: Relationship analysis
- **Box Plots**: Price distribution by genre  
- **Histograms**: Overall price distribution
- **Interactive Tables**: Searchable, sortable results

## 💻 Application Architecture

### Smart Database Connection
```python
# Automatically detects database location
# Works locally and in cloud deployments
db = BookDatabase()  # Uses ../data/processed/books_data.duckdb
```

### Modular Design
- **Shared utilities** in `../shared/database.py`
- **Cached queries** for performance
- **Responsive layout** with columns
- **Error handling** with user feedback

### Performance Features
- **@st.cache_data** decorators for expensive queries
- **Lazy loading** of data
- **Connection pooling** through context managers
- **Efficient queries** using DuckDB's speed

## 🎨 UI/UX Features

### Modern Styling
- **Custom CSS** with gradients and modern colors
- **Responsive design** works on desktop and mobile
- **Icon integration** with emojis and symbols
- **Card layouts** for organized content display
- **Color-coded metrics** for visual appeal

### User Experience
- **Sidebar navigation** for easy access
- **Progress indicators** during data loading
- **Clear error messages** with actionable guidance
- **Intuitive filters** with sensible defaults
- **Exportable results** (future feature)

## 🔧 Development Commands

### Local Development
```bash
# Standard launch
streamlit run app/main.py

# Development mode with auto-reload
streamlit run app/main.py --server.runOnSave true

# Custom port
streamlit run app/main.py --server.port 8502

# Debug mode
streamlit run app/main.py --logger.level debug
```

### Dependencies Management
```bash
# Install specific version
pip install streamlit==1.28.0

# Update requirements
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt
```

## 🌐 Deployment Options

### 1. Streamlit Cloud (Recommended)
```bash
# 1. Push to GitHub
git add . && git commit -m "Add web app" && git push

# 2. Visit https://share.streamlit.io
# 3. Connect your GitHub repository  
# 4. Deploy automatically!
```

**Pros**: Free, automatic deployment, GitHub integration
**Cons**: Public repositories only (free tier)

### 2. Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway deploy
```

### 3. Render
```bash
# Connect GitHub repo at https://render.com
# Auto-deploy on git push
```

### 4. Local Network Sharing
```bash
# Share on local network
streamlit run app/main.py --server.address 0.0.0.0
```

## 🚨 Troubleshooting

### "Database not found"
**Problem**: App can't locate the DuckDB file  
**Solution**: 
```bash
# Ensure Phase 1 ETL completed successfully
ls ../data/processed/books_data.duckdb

# If missing, run Phase 1
cd ../phase1-etl && ./scripts/run_processing.sh
```

### "Import errors" 
**Problem**: Missing Python packages  
**Solution**:
```bash
source ../venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt  # Install dependencies
```

### "Port already in use"
**Problem**: Port 8501 is occupied  
**Solution**:
```bash
# Use different port
streamlit run app/main.py --server.port 8502

# Or kill existing Streamlit processes
pkill -f streamlit
```

### "Slow performance"
**Problem**: App loads slowly with large dataset  
**Solution**: 
- Reduce query limits in search functions
- Add more `@st.cache_data` decorators
- Optimize database queries

## 🎓 Learning Extensions

### Beginner Enhancements
1. **Add new metrics** to the dashboard
2. **Create custom color schemes**
3. **Add data export buttons**
4. **Implement user favorites**

### Intermediate Features
1. **Multi-page applications** with `st.navigation`
2. **User authentication** with `streamlit-authenticator`
3. **File upload** for new data
4. **Advanced filters** with date ranges

### Advanced Development
1. **Custom components** with React
2. **Real-time updates** with WebSocket
3. **Machine learning integration** for recommendations
4. **API integration** for live book data

## 🔗 Useful Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python](https://plotly.com/python/)
- [DuckDB Python API](https://duckdb.org/docs/api/python/overview)
- [Streamlit Gallery](https://streamlit.io/gallery) - Inspiration and examples

## ➡️ Next Steps

1. **Explore the application** - Try all the different views and filters
2. **Deploy to cloud** - Share your work with others
3. **Customize the design** - Make it your own with colors and layouts
4. **Add new features** - Extend functionality based on your interests
5. **Build your portfolio** - Document your project for job applications

## 🏆 Success Criteria

By completing Phase 2, you should have:
- ✅ A fully functional web application
- ✅ Interactive data visualizations  
- ✅ Multi-view dashboard with filtering
- ✅ Cloud deployment experience
- ✅ Portfolio-ready project
- ✅ Modern web development skills

**Congratulations! You've built a complete data engineering and web development project! 🎉**