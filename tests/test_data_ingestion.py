# tests/test_data_ingestion.py

"""
Unit tests for data ingestion module
"""

import pytest
import pandas as pd
import numpy as np
from data_ingestion.data_connector import DataConnector

class TestDataConnector:
    """Test cases for DataConnector class"""
    
    def test_init(self, sample_config):
        """Test DataConnector initialization"""
        connector = DataConnector(sample_config)
        assert connector.config == sample_config
        assert connector.logger is not None
    
    def test_load_training_data_success(self, temp_data_file, sample_config):
        """Test successful data loading"""
        config = {**sample_config, 'data_path': temp_data_file}
        connector = DataConnector(config)
        
        data = connector.load_training_data('value', 'date')
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert 'value' in data.columns
        assert 'date' in data.columns
        assert pd.api.types.is_datetime64_any_dtype(data['date'])
    
    def test_load_training_data_missing_target(self, temp_data_file, sample_config):
        """Test loading data with missing target column"""
        config = {**sample_config, 'data_path': temp_data_file}
        connector = DataConnector(config)
        
        with pytest.raises(ValueError, match="Target column 'missing_column' not found"):
            connector.load_training_data('missing_column', 'date')
    
    def test_load_training_data_missing_date(self, temp_data_file, sample_config):
        """Test loading data with missing date column"""
        config = {**sample_config, 'data_path': temp_data_file}
        connector = DataConnector(config)
        
        with pytest.raises(ValueError, match="Date column 'missing_date' not found"):
            connector.load_training_data('value', 'missing_date')
    
    def test_load_training_data_with_end_date(self, temp_data_file, sample_config):
        """Test loading data with end date filter"""
        config = {**sample_config, 'data_path': temp_data_file}
        connector = DataConnector(config)
        
        data = connector.load_training_data('value', 'date', end_date='2023-06-30')
        
        assert len(data) > 0
        assert data['date'].max() <= pd.to_datetime('2023-06-30')
    
    def test_handle_missing_values(self, sample_config):
        """Test missing value handling"""
        # Create data with missing values
        data_with_na = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=10),
            'value': [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10],
            'other': range(10)
        })
        
        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            data_with_na.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            config = {**sample_config, 'data_path': temp_file}
            connector = DataConnector(config)
            
            data = connector.load_training_data('value', 'date')
            
            # Check that missing values are handled
            assert not data['value'].isnull().any()
            assert len(data) > 0
            
        finally:
            import os
            os.unlink(temp_file)
    
    def test_load_latest_data(self, temp_data_file, sample_config):
        """Test loading latest data"""
        config = {**sample_config, 'data_path': temp_data_file, 'target_column': 'value', 'date_column': 'date'}
        connector = DataConnector(config)
        
        data = connector.load_latest_data()
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert 'value' in data.columns
        assert 'date' in data.columns
    
    def test_get_data_quality_metrics(self, sample_config):
        """Test data quality metrics"""
        connector = DataConnector(sample_config)
        
        metrics = connector.get_data_quality_metrics()
        
        assert isinstance(metrics, dict)
        assert 'overall_score' in metrics
        assert 'completeness' in metrics
        assert 0 <= metrics['overall_score'] <= 1
        assert 0 <= metrics['completeness'] <= 1
    
    def test_detect_data_drift(self, sample_config):
        """Test data drift detection"""
        connector = DataConnector(sample_config)
        
        drift_detected = connector.detect_data_drift()
        
        assert isinstance(drift_detected, bool)
    
    def test_data_sorting(self, sample_config):
        """Test that data is properly sorted by date"""
        # Create unsorted data
        unsorted_data = pd.DataFrame({
            'date': ['2023-01-03', '2023-01-01', '2023-01-02'],
            'value': [3, 1, 2]
        })
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            unsorted_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            config = {**sample_config, 'data_path': temp_file}
            connector = DataConnector(config)
            
            data = connector.load_training_data('value', 'date')
            
            # Check that data is sorted
            assert data['date'].is_monotonic_increasing
            assert data['value'].tolist() == [1, 2, 3]
            
        finally:
            import os
            os.unlink(temp_file)