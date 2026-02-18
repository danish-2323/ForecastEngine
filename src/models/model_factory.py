# src/models/model_factory.py

import pandas as pd
import numpy as np
from typing import Dict
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

class BaseModel:
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.is_fitted = False
        
    def fit(self, data: pd.DataFrame, target_column: str):
        raise NotImplementedError
        
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError

class ARIMAModel(BaseModel):
    def __init__(self):
        super().__init__("ARIMA")
        
    def fit(self, data: pd.DataFrame, target_column: str):
        """Simple ARIMA-like model using trend + seasonality"""
        self.target_column = target_column
        self.data = data[target_column].values
        
        # Calculate simple trend
        x = np.arange(len(self.data))
        self.trend_coef = np.polyfit(x, self.data, 1)
        
        # Calculate seasonal pattern (weekly)
        self.seasonal_pattern = self._calculate_seasonal_pattern()
        self.is_fitted = True
        return self
        
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model not fitted")
            
        n_periods = len(features)
        predictions = []
        last_value = self.data[-1]
        
        for i in range(n_periods):
            trend_component = last_value + (self.trend_coef[0] * (i + 1))
            seasonal_idx = (len(self.data) + i) % len(self.seasonal_pattern)
            seasonal_component = self.seasonal_pattern[seasonal_idx]
            prediction = trend_component + seasonal_component
            predictions.append(max(0, prediction))
            
        return np.array(predictions)
    
    def _calculate_seasonal_pattern(self) -> np.ndarray:
        """Calculate weekly seasonal pattern"""
        if len(self.data) < 14:
            return np.zeros(7)
            
        weekly_data = self.data[-21:]  # Last 3 weeks
        pattern = []
        for day in range(7):
            day_values = weekly_data[day::7]
            if len(day_values) > 0:
                pattern.append(np.mean(day_values) - np.mean(weekly_data))
            else:
                pattern.append(0)
        return np.array(pattern)

class RandomForestModel(BaseModel):
    def __init__(self, config: dict):
        super().__init__("RandomForest")
        rf_config = config.get('random_forest', {})
        self.model = RandomForestRegressor(
            n_estimators=rf_config.get('n_estimators', 100),
            max_depth=rf_config.get('max_depth', 10),
            random_state=42
        )
        
    def fit(self, data: pd.DataFrame, target_column: str):
        """Fit Random Forest model"""
        feature_columns = [col for col in data.columns 
                          if col not in [target_column, 'date'] and not col.startswith('Unnamed')]
        
        X = data[feature_columns]
        y = data[target_column]
        
        self.model.fit(X, y)
        self.feature_columns = feature_columns
        self.is_fitted = True
        return self
        
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        X = features[self.feature_columns]
        return self.model.predict(X)
    
    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_fitted:
            return {}
        return dict(zip(self.feature_columns, self.model.feature_importances_))

class LinearModel(BaseModel):
    def __init__(self):
        super().__init__("Linear")
        self.model = LinearRegression()
        
    def fit(self, data: pd.DataFrame, target_column: str):
        feature_columns = [col for col in data.columns 
                          if col not in [target_column, 'date'] and not col.startswith('Unnamed')]
        
        X = data[feature_columns]
        y = data[target_column]
        
        self.model.fit(X, y)
        self.feature_columns = feature_columns
        self.is_fitted = True
        return self
        
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model not fitted")
        X = features[self.feature_columns]
        return self.model.predict(X)

class ModelFactory:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def train_models(self, data: pd.DataFrame, target_column: str, date_column: str) -> Dict[str, BaseModel]:
        """Train all enabled models"""
        self.logger.info("Training models...")
        models = {}
        
        # Train ARIMA
        if self.config.get('statistical', {}).get('arima', {}).get('enabled', True):
            try:
                arima_model = ARIMAModel()
                arima_model.fit(data, target_column)
                models['arima'] = arima_model
                self.logger.info("ARIMA model trained")
            except Exception as e:
                self.logger.warning(f"ARIMA training failed: {e}")
        
        # Train Random Forest
        if self.config.get('machine_learning', {}).get('random_forest', {}).get('enabled', True):
            try:
                rf_model = RandomForestModel(self.config.get('machine_learning', {}))
                rf_model.fit(data, target_column)
                models['random_forest'] = rf_model
                self.logger.info("Random Forest model trained")
            except Exception as e:
                self.logger.warning(f"Random Forest training failed: {e}")
        
        # Train Linear
        if self.config.get('machine_learning', {}).get('linear', {}).get('enabled', True):
            try:
                linear_model = LinearModel()
                linear_model.fit(data, target_column)
                models['linear'] = linear_model
                self.logger.info("Linear model trained")
            except Exception as e:
                self.logger.warning(f"Linear training failed: {e}")
        
        self.logger.info(f"Trained {len(models)} models")
        return models