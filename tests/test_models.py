# tests/test_models.py

"""
Unit tests for forecasting models
"""

import pytest
import pandas as pd
import numpy as np
from models.model_factory import ModelFactory, ARIMAModel, RandomForestModel, LinearModel

class TestARIMAModel:
    """Test cases for ARIMA model"""
    
    def test_init(self):
        """Test ARIMA model initialization"""
        model = ARIMAModel()
        assert model.name == "ARIMA"
        assert not model.is_fitted
    
    def test_fit_and_predict(self, sample_data):
        """Test ARIMA model fitting and prediction"""
        model = ARIMAModel()
        
        # Fit model
        fitted_model = model.fit(sample_data, 'value')
        assert fitted_model.is_fitted
        assert fitted_model == model  # Should return self
        
        # Create dummy features for prediction
        dummy_features = pd.DataFrame({'dummy': range(5)})
        predictions = model.predict(dummy_features)
        
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == 5
        assert all(pred >= 0 for pred in predictions)  # Should be non-negative
    
    def test_predict_without_fit(self):
        """Test prediction without fitting raises error"""
        model = ARIMAModel()
        dummy_features = pd.DataFrame({'dummy': range(5)})
        
        with pytest.raises(ValueError, match="Model not fitted"):
            model.predict(dummy_features)
    
    def test_seasonal_pattern_calculation(self, sample_data):
        """Test seasonal pattern calculation"""
        model = ARIMAModel()
        model.fit(sample_data, 'value')
        
        # Check seasonal pattern
        assert hasattr(model, 'seasonal_pattern')
        assert isinstance(model.seasonal_pattern, np.ndarray)
        assert len(model.seasonal_pattern) == 7  # Weekly pattern

class TestRandomForestModel:
    """Test cases for Random Forest model"""
    
    def test_init(self, sample_config):
        """Test Random Forest model initialization"""
        config = sample_config.get('machine_learning', {})
        model = RandomForestModel(config)
        
        assert model.name == "RandomForest"
        assert not model.is_fitted
        assert model.model is not None
    
    def test_fit_and_predict(self, sample_data, sample_config):
        """Test Random Forest fitting and prediction"""
        # Add some features to the data
        sample_data['lag_1'] = sample_data['value'].shift(1)
        sample_data['rolling_mean_7'] = sample_data['value'].rolling(7).mean()
        sample_data = sample_data.dropna()
        
        config = sample_config.get('machine_learning', {})
        model = RandomForestModel(config)
        
        # Fit model
        fitted_model = model.fit(sample_data, 'value')
        assert fitted_model.is_fitted
        assert hasattr(fitted_model, 'feature_columns')
        
        # Predict
        feature_columns = [col for col in sample_data.columns 
                          if col not in ['value', 'date'] and not col.startswith('Unnamed')]
        test_features = sample_data[feature_columns].tail(5)
        
        predictions = model.predict(test_features)
        
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == 5
        assert all(np.isfinite(pred) for pred in predictions)
    
    def test_feature_importance(self, sample_data, sample_config):
        """Test feature importance extraction"""
        # Prepare data with features
        sample_data['lag_1'] = sample_data['value'].shift(1)
        sample_data['price_feature'] = sample_data['price']
        sample_data = sample_data.dropna()
        
        config = sample_config.get('machine_learning', {})
        model = RandomForestModel(config)
        model.fit(sample_data, 'value')
        
        importance = model.get_feature_importance()
        
        assert isinstance(importance, dict)
        assert len(importance) > 0
        assert all(isinstance(v, (int, float)) for v in importance.values())
        assert all(v >= 0 for v in importance.values())  # Importance should be non-negative

class TestLinearModel:
    """Test cases for Linear model"""
    
    def test_init(self):
        """Test Linear model initialization"""
        model = LinearModel()
        assert model.name == "Linear"
        assert not model.is_fitted
    
    def test_fit_and_predict(self, sample_data):
        """Test Linear model fitting and prediction"""
        # Add features
        sample_data['lag_1'] = sample_data['value'].shift(1)
        sample_data['trend'] = range(len(sample_data))
        sample_data = sample_data.dropna()
        
        model = LinearModel()
        
        # Fit model
        fitted_model = model.fit(sample_data, 'value')
        assert fitted_model.is_fitted
        
        # Predict
        feature_columns = [col for col in sample_data.columns 
                          if col not in ['value', 'date'] and not col.startswith('Unnamed')]
        test_features = sample_data[feature_columns].tail(3)
        
        predictions = model.predict(test_features)
        
        assert isinstance(predictions, np.ndarray)
        assert len(predictions) == 3
        assert all(np.isfinite(pred) for pred in predictions)

class TestModelFactory:
    """Test cases for ModelFactory"""
    
    def test_init(self, sample_config):
        """Test ModelFactory initialization"""
        factory = ModelFactory(sample_config)
        assert factory.config == sample_config
        assert factory.logger is not None
    
    def test_train_models(self, sample_data, sample_config):
        """Test training multiple models"""
        # Prepare data with features
        sample_data['lag_1'] = sample_data['value'].shift(1)
        sample_data['lag_7'] = sample_data['value'].shift(7)
        sample_data['rolling_mean_7'] = sample_data['value'].rolling(7).mean()
        sample_data = sample_data.dropna()
        
        factory = ModelFactory(sample_config)
        
        models = factory.train_models(sample_data, 'value', 'date')
        
        assert isinstance(models, dict)
        assert len(models) > 0
        
        # Check that enabled models are trained
        if sample_config.get('statistical', {}).get('arima', {}).get('enabled', True):
            assert 'arima' in models
            assert models['arima'].is_fitted
        
        if sample_config.get('machine_learning', {}).get('random_forest', {}).get('enabled', True):
            assert 'random_forest' in models
            assert models['random_forest'].is_fitted
        
        if sample_config.get('machine_learning', {}).get('linear', {}).get('enabled', True):
            assert 'linear' in models
            assert models['linear'].is_fitted
    
    def test_train_models_with_failures(self, sample_config, caplog):
        """Test model training with some failures"""
        # Create minimal data that might cause some models to fail
        minimal_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=5),
            'value': [1, 2, 3, 4, 5]
        })
        
        factory = ModelFactory(sample_config)
        
        with caplog.at_level('WARNING'):
            models = factory.train_models(minimal_data, 'value', 'date')
        
        # Should still return a dictionary, even if some models fail
        assert isinstance(models, dict)
    
    def test_disabled_models(self, sample_data):
        """Test that disabled models are not trained"""
        # Prepare data
        sample_data['lag_1'] = sample_data['value'].shift(1)
        sample_data = sample_data.dropna()
        
        # Config with all models disabled
        config = {
            'statistical': {'arima': {'enabled': False}},
            'machine_learning': {
                'random_forest': {'enabled': False},
                'linear': {'enabled': False}
            }
        }
        
        factory = ModelFactory(config)
        models = factory.train_models(sample_data, 'value', 'date')
        
        # Should return empty dict or only enabled models
        assert isinstance(models, dict)
        assert 'arima' not in models or not models.get('arima')
        assert 'random_forest' not in models or not models.get('random_forest')
        assert 'linear' not in models or not models.get('linear')
    
    def test_model_prediction_consistency(self, sample_data, sample_config):
        """Test that models produce consistent predictions"""
        # Prepare data
        sample_data['lag_1'] = sample_data['value'].shift(1)
        sample_data['rolling_mean_7'] = sample_data['value'].rolling(7).mean()
        sample_data = sample_data.dropna()
        
        factory = ModelFactory(sample_config)
        models = factory.train_models(sample_data, 'value', 'date')
        
        # Test predictions
        feature_columns = [col for col in sample_data.columns 
                          if col not in ['value', 'date'] and not col.startswith('Unnamed')]
        test_features = sample_data[feature_columns].tail(3)
        
        for model_name, model in models.items():
            predictions = model.predict(test_features)
            
            # Predictions should be consistent across calls
            predictions2 = model.predict(test_features)
            np.testing.assert_array_equal(predictions, predictions2)
            
            # Predictions should be reasonable
            assert all(np.isfinite(pred) for pred in predictions)
            assert len(predictions) == len(test_features)