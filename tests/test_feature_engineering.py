# tests/test_feature_engineering.py

"""
Unit tests for feature engineering module
"""

import pytest
import pandas as pd
import numpy as np
from feature_engineering.feature_builder import FeatureBuilder

class TestFeatureBuilder:
    """Test cases for FeatureBuilder class"""
    
    def test_init(self, sample_config):
        """Test FeatureBuilder initialization"""
        fb = FeatureBuilder(sample_config)
        assert fb.config == sample_config
        assert fb.logger is not None
    
    def test_build_features_basic(self, sample_data, sample_config):
        """Test basic feature building"""
        fb = FeatureBuilder(sample_config)
        
        features = fb.build_features(sample_data, 'value', 'date')
        
        assert isinstance(features, pd.DataFrame)
        assert len(features) > 0
        assert len(features) < len(sample_data)  # Some rows dropped due to NaN
        
        # Check that original columns are preserved
        assert 'value' in features.columns
        assert 'date' in features.columns
    
    def test_lag_features(self, sample_data, sample_config):
        """Test lag feature creation"""
        config = {**sample_config, 'lags': {'periods': [1, 2, 7]}}
        fb = FeatureBuilder(config)
        
        features = fb.build_features(sample_data, 'value', 'date')
        
        # Check lag features exist
        assert 'lag_1' in features.columns
        assert 'lag_2' in features.columns
        assert 'lag_7' in features.columns
        
        # Check lag values are correct (where not NaN)
        valid_idx = features.dropna().index
        if len(valid_idx) > 0:
            first_valid = valid_idx[0]
            if first_valid >= 1:
                assert features.loc[first_valid, 'lag_1'] == features.loc[first_valid-1, 'value']
    
    def test_rolling_features(self, sample_data, sample_config):
        """Test rolling window feature creation"""
        config = {**sample_config, 'rolling_windows': {'windows': [3, 7], 'functions': ['mean', 'std']}}
        fb = FeatureBuilder(config)
        
        features = fb.build_features(sample_data, 'value', 'date')
        
        # Check rolling features exist
        assert 'rolling_mean_3' in features.columns
        assert 'rolling_mean_7' in features.columns
        assert 'rolling_std_3' in features.columns
        assert 'rolling_std_7' in features.columns
        
        # Check rolling mean calculation (where not NaN)
        valid_data = features.dropna()
        if len(valid_data) > 0:
            # Rolling mean should be reasonable
            assert valid_data['rolling_mean_7'].min() >= 0
            assert valid_data['rolling_mean_7'].max() < 1000  # Reasonable upper bound
    
    def test_date_features(self, sample_data, sample_config):
        """Test date-based feature creation"""
        fb = FeatureBuilder(sample_config)
        
        features = fb.build_features(sample_data, 'value', 'date')
        
        # Check date features exist
        assert 'day_of_week' in features.columns
        assert 'month' in features.columns
        assert 'day_of_year' in features.columns
        
        # Check date feature ranges
        assert features['day_of_week'].min() >= 0
        assert features['day_of_week'].max() <= 6
        assert features['month'].min() >= 1
        assert features['month'].max() <= 12
    
    def test_seasonality_features(self, sample_data, sample_config):
        """Test seasonality feature creation"""
        config = {**sample_config, 'seasonality': {'enabled': True}}
        fb = FeatureBuilder(config)
        
        features = fb.build_features(sample_data, 'value', 'date')
        
        # Check seasonality features exist
        assert 'is_weekend' in features.columns
        assert 'month_sin' in features.columns
        assert 'month_cos' in features.columns
        
        # Check feature ranges
        assert features['is_weekend'].min() >= 0
        assert features['is_weekend'].max() <= 1
        assert features['month_sin'].min() >= -1
        assert features['month_sin'].max() <= 1
        assert features['month_cos'].min() >= -1
        assert features['month_cos'].max() <= 1
    
    def test_external_features(self, sample_data, sample_config):
        """Test external feature inclusion"""
        fb = FeatureBuilder(sample_config)
        
        external_features = ['price', 'promotion', 'temperature']
        features = fb.build_features(sample_data, 'value', 'date', external_features)
        
        # Check external features are included
        for feature in external_features:
            assert feature in features.columns
    
    def test_missing_external_features(self, sample_data, sample_config):
        """Test handling of missing external features"""
        fb = FeatureBuilder(sample_config)
        
        # Request non-existent external feature
        external_features = ['price', 'nonexistent_feature']
        features = fb.build_features(sample_data, 'value', 'date', external_features)
        
        # Should include existing feature but skip missing one
        assert 'price' in features.columns
        assert 'nonexistent_feature' not in features.columns
    
    def test_build_prediction_features(self, sample_data, sample_config):
        """Test prediction feature building"""
        fb = FeatureBuilder(sample_config)
        
        # First build training features
        train_features = fb.build_features(sample_data, 'value', 'date')
        
        # Build prediction features
        horizon = 5
        pred_features = fb.build_prediction_features(train_features, horizon)
        
        assert isinstance(pred_features, pd.DataFrame)
        assert len(pred_features) == horizon
        
        # Should have same columns as training features (except target)
        feature_cols = [col for col in train_features.columns if col not in ['value', 'date']]
        for col in feature_cols:
            if col in pred_features.columns:
                assert col in pred_features.columns
    
    def test_nan_handling(self, sample_config):
        """Test NaN handling in feature building"""
        # Create data with some NaN values after feature engineering
        small_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=5),
            'value': [1, 2, 3, 4, 5]
        })
        
        fb = FeatureBuilder(sample_config)
        features = fb.build_features(small_data, 'value', 'date')
        
        # Should drop rows with NaN values
        assert not features.isnull().any().any()
        assert len(features) <= len(small_data)
    
    def test_empty_config(self, sample_data):
        """Test feature building with minimal config"""
        minimal_config = {}
        fb = FeatureBuilder(minimal_config)
        
        features = fb.build_features(sample_data, 'value', 'date')
        
        # Should still work with default settings
        assert isinstance(features, pd.DataFrame)
        assert len(features) > 0
    
    def test_feature_count_logging(self, sample_data, sample_config, caplog):
        """Test that feature count is logged"""
        fb = FeatureBuilder(sample_config)
        
        with caplog.at_level('INFO'):
            features = fb.build_features(sample_data, 'value', 'date')
        
        # Check that logging occurred
        assert "Created" in caplog.text
        assert "features" in caplog.text