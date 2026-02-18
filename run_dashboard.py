#!/usr/bin/env python3
"""
ForecastEngine Dashboard Runner
Launch the Streamlit dashboard
"""

import sys
import os
import subprocess
from pathlib import Path

def run_dashboard():
    """Run the Streamlit dashboard"""
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    dashboard_path = src_path / "dashboard" / "app.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        sys.exit(1)
    
    print("🚀 Starting ForecastEngine Dashboard...")
    print("📊 Dashboard will open in your browser at: http://localhost:8501")
    print("=" * 60)
    
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_dashboard()