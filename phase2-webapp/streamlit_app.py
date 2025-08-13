"""
Entry point for Streamlit Cloud deployment
This file is automatically detected by Streamlit Cloud
"""

import sys
from pathlib import Path

# Add the project root and app directory to Python path
project_root = Path(__file__).parent.parent
app_dir = Path(__file__).parent / "app"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(app_dir))

# Import and run the main application
try:
    from app.main import main
except ImportError:
    # Fallback for different import structures
    from main import main

if __name__ == "__main__":
    main()