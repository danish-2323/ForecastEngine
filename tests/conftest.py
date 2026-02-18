# tests/conftest.py

"""
Pytest configuration and fixtures for ForecastEngine tests
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def sample_data():
    """Generate sample time-series data for testing"""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    n_days = len(dates)
    
    # Generate synthetic data with trend and seasonality
    trend = np.linspace(100, 200, n_days)
    seasonal = 10 * np.sin(2 * np.pi * np.arange(n_days) / 7)  # Weekly seasonality
    noise = np.random.normal(0, 5, n_days)
    
    values = trend + seasonal + noise
    
    data = pd.DataFrame({
        'date': dates,
        'value': values,
        'price': np.random.uniform(9, 11, n_days),
        'promotion': np.random.choice([0, 1], n_days, p=[0.8, 0.2]),
        'temperature': 20 + 10 * np.sin(2 * np.pi * np.arange(n_days) / 365) + np.random.normal(0, 2, n_days)
    })
    
    return data

@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'target_column': 'value',
        'date_column': 'date',
        'lags': {'periods': [1, 7]},
        'rolling_windows': {'windows': [7], 'functions': ['mean']},
        'seasonality': {'enabled': True},
        'statistical': {'arima': {'enabled': True}},
        'machine_learning': {
            'random_forest': {'enabled': True, 'n_estimators': 10},
            'linear': {'enabled': True}
        },
        'ensemble': {'method': 'weighted_average'},
        'uncertainty': {'method': 'residual_based'}
    }

@pytest.fixture
def temp_data_file(sample_data):
    """Create temporary CSV file with sample data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_data.to_csv(f.name, index=False)
        yield f.name
    
    # Cleanup
    os.unlink(f.name)

@pytest.fixture
def temp_model_dir():
    """Create temporary directory for model storage"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir