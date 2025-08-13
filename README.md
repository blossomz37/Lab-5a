# 📚 Book Data Processing & Analytics Project

A comprehensive data engineering project that demonstrates ETL processes and modern web application development using real book data from 14 genres.

## 🎯 Project Overview

This project consists of two phases:
- **Phase 1**: ETL Pipeline (Excel → DuckDB)  
- **Phase 2**: Interactive Web Application (Streamlit)

**Dataset**: 1,400+ books across 14 genres with ratings, prices, and metadata.

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/blossomz37/Lab-5b-ffa.git
cd Lab-5b-ffa

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Configure environment (optional)
cp .env.example .env
# Edit .env to customize settings
```

### 2. Run Phase 1 (ETL Pipeline)
```bash
# Install ETL dependencies
pip install pandas duckdb openpyxl

# Process Excel files to DuckDB
cd phase1-etl
./scripts/run_processing.sh
```

### 3. Run Phase 2 (Web App)
```bash
# Install web app dependencies (from project root)
pip install -r phase2-webapp/requirements.txt

# Launch web application
streamlit run phase2-webapp/app/main.py
```

Your browser will open to `http://localhost:8501` with the interactive dashboard! 🎉

## 📁 Project Structure

```
Lab-5b-ffa/
├── README.md                     # This file
├── venv/                        # Python virtual environment
├── data/                        # Shared data directory
│   ├── raw/                     # Excel source files (14 genres)
│   └── processed/               # Generated DuckDB database
│
├── phase1-etl/                  # ETL Processing Phase
│   ├── README.md               # ETL-specific documentation
│   ├── scripts/                # Processing scripts
│   │   ├── setup_environment.sh    # Environment setup
│   │   ├── create_duckdb.py        # Main ETL script
│   │   ├── verify_duckdb.py        # Database validation
│   │   └── run_processing.sh       # Full pipeline
│   └── docs/                   # ETL documentation
│
├── phase2-webapp/              # Web Application Phase
│   ├── README.md               # Web app documentation  
│   ├── app/
│   │   └── main.py            # Streamlit application
│   ├── requirements.txt       # Web dependencies
│   └── docs/                  # Web app documentation
│
└── shared/                     # Shared utilities
    ├── database.py            # DuckDB connection utilities
    └── __init__.py           # Package initialization
```

## 🌟 Features

### Phase 1: ETL Pipeline
- ✅ **Automated processing** of 14 Excel files
- ✅ **Data validation** and quality checks  
- ✅ **DuckDB database** creation with indexes
- ✅ **Error handling** and logging
- ✅ **Virtual environment** management

### Phase 2: Web Application  
- 📊 **Interactive dashboard** with key metrics
- 🔍 **Advanced search** with multiple filters
- 📈 **Data visualizations** using Plotly
- ⭐ **Top-rated books** analysis
- 💰 **Price analysis** and trends
- 📱 **Responsive design** for mobile/desktop
- 🚀 **Cloud deployment ready**

## 🛠️ Technology Stack

- **Data Processing**: Python, pandas, DuckDB
- **Web Framework**: Streamlit
- **Visualizations**: Plotly, Altair
- **Database**: DuckDB (embedded analytics)
- **Deployment**: Local development, cloud-ready

## 🎓 Learning Objectives

Students will learn:
1. **ETL Processes** - Extract, Transform, Load workflows
2. **Database Design** - Schema creation, indexing, optimization
3. **Data Quality** - Validation, error handling, logging
4. **Web Development** - Interactive dashboards, user interfaces
5. **Data Visualization** - Charts, graphs, analytics
6. **DevOps Practices** - Virtual environments, deployment

## 📊 Dataset Information

**Genres**: Cozy Mystery, Romance, Fantasy, Science Fiction, Urban Fantasy, Paranormal, Historical Romance, Erotica, Teen/YA, M/T/S, Gay Romance, Science Fiction Romance, SFF

**Data Fields**: Title, Author, ASIN, Price, Rating, Reviews, Genre, Series, Release Date, Publisher, and more.

## 🚀 Deployment Options

### Local Development (Recommended for learning)
```bash
streamlit run phase2-webapp/app/main.py
```

### Cloud Deployment (Portfolio ready)
- **Streamlit Cloud**: Connect GitHub repo, auto-deploy
- **Railway**: `railway deploy`  
- **Render**: Connect GitHub, deploy automatically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both phases
5. Submit a pull request

## 📚 Documentation

- [Phase 1 ETL Guide](phase1-etl/README.md)
- [Phase 2 Web App Guide](phase2-webapp/README.md)
- [Environment Configuration](ENVIRONMENT.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Setup Instructions](phase1-etl/docs/SETUP_GUIDE.md)
- [Student Guide](phase1-etl/docs/STUDENT_GUIDE.md)

## ⚡ Troubleshooting

**Database not found**: Run Phase 1 ETL first to create the database.

**Import errors**: Ensure virtual environment is activated and dependencies installed.

**Port issues**: Streamlit uses port 8501 by default. Change with `--server.port 8502`.

## 📄 License

This project is for educational purposes.

---

**Happy coding! 🚀**