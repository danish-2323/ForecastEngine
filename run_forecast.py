#!/usr/bin/env python3
"""
ForecastEngine Runner Script
Simple script to run the complete forecasting pipeline
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run ForecastEngine
from forecast_engine import main

if __name__ == "__main__":
    print("Starting ForecastEngine...")
    print("=" * 50)
    
    try:
        main()
        print("=" * 50)
        print("ForecastEngine completed successfully!")
        
    except Exception as e:
        print("=" * 50)
        print("ForecastEngine failed: {e}")
        sys.exit(1)