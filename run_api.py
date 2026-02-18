#!/usr/bin/env python3
"""
ForecastEngine API Runner
Launch the FastAPI server
"""

import sys
import os
import subprocess
from pathlib import Path

def run_api():
    """Run the FastAPI server"""
    
    # Add src directory to Python path
    src_path = Path(__file__).parent / "src"
    api_path = src_path / "api" / "main.py"
    
    if not api_path.exists():
        print(f"❌ API file not found: {api_path}")
        sys.exit(1)
    
    print("🚀 Starting ForecastEngine API Server...")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    try:
        # Change to src directory
        os.chdir(src_path)
        
        # Run FastAPI with uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 API server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_api()