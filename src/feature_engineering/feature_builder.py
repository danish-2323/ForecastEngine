# src/feature_engineering/feature_builder.py

import pandas as pd
import numpy as np
from typing import List, Optional
import logging

class FeatureBuilder:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def build_features(self, data: pd.DataFrame, target_column: str, 
                      date_column: str, external_features: Optional[List[str]] = None) -> pd.DataFrame:
        """Build time-series features"""
        self.logger.info("Building features...")
        
        features_df = data.copy()
        
        # Lag features for target
        lag_periods = self.config.get('lags', {}).get('periods', [1, 2, 3, 7, 14, 30])
        for lag in lag_periods:
            features_df[f'lag_{lag}'] = features_df[target_column].shift(lag)
            
        # Rolling features for target
        windows = self.config.get('rolling_windows', {}).get('windows', [7, 14, 30])
        for window in windows:
            features_df[f'rolling_mean_{window}'] = features_df[target_column].rolling(window=window).mean()
            features_df[f'rolling_std_{window}'] = features_df[target_column].rolling(window=window).std()
            
        # Date features
        date_series = pd.to_datetime(features_df[date_column])
        features_df['day_of_week'] = date_series.dt.dayofweek
        features_df['month'] = date_series.dt.month
        features_df['day_of_year'] = date_series.dt.dayofyear
        
        # Seasonality (optional)
        if self.config.get('seasonality', {}).get('enabled', True):
            features_df['is_weekend'] = (date_series.dt.dayofweek >= 5).astype(int)
            features_df['month_sin'] = np.sin(2 * np.pi * features_df['month'] / 12)
            features_df['month_cos'] = np.cos(2 * np.pi * features_df['month'] / 12)
            
        # Process external features
        if external_features:
            features_df = self._process_external_features(features_df, external_features)
                    
        # Drop NaN rows
        features_df = features_df.dropna()
        
        self.logger.info(f"Created {len(features_df.columns)} features")
        return features_df
    
    def build_prediction_features(self, data: pd.DataFrame, horizon: int) -> pd.DataFrame:
        """Build features for prediction"""
        # Use last available features
        last_features = data.tail(1).copy()
        prediction_features = pd.concat([last_features] * horizon, ignore_index=True)
        return prediction_features
    
    def _process_external_features(self, features_df: pd.DataFrame, external_features: List[str]) -> pd.DataFrame:
        """Process external features with lag generation"""
        for feature in external_features:
            if feature not in features_df.columns:
                continue
                
            # Keep original feature
            # Generate lags for numeric external features
            if features_df[feature].dtype in ['float64', 'int64']:
                # Create short lags for external signals
                for lag in [1, 3, 7]:
                    features_df[f'{feature}_lag_{lag}'] = features_df[feature].shift(lag)
                    
                # Create rolling mean for external signals
                features_df[f'{feature}_rolling_7'] = features_df[feature].rolling(window=7).mean()
                
        return features_df