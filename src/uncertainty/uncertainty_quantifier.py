# src/uncertainty/uncertainty_quantifier.py

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

class UncertaintyQuantifier:
    def __init__(self, config: dict):
        self.config = config
        self.method = config.get('method', 'residual_based')
        self.logger = logging.getLogger(__name__)
        self.residuals_std = None
        
    def fit(self, models: Dict, ensemble, data: pd.DataFrame, target_column: str):
        """Fit uncertainty quantification"""
        self.logger.info(f"Fitting uncertainty using {self.method}")
        
        try:
            # Generate predictions on training data
            feature_columns = [col for col in data.columns 
                              if col not in [target_column, 'date'] and not col.startswith('Unnamed')]
            
            X = data[feature_columns]
            y = data[target_column].values
            
            # Get ensemble predictions
            predictions = ensemble.predict(X, horizon=len(X), models=models)
            
            # Calculate residuals
            residuals = y - predictions
            self.residuals_std = np.std(residuals)
            
            self.logger.info(f"Residual std: {self.residuals_std:.3f}")
            
        except Exception as e:
            self.logger.warning(f"Uncertainty fitting failed: {e}")
            self.residuals_std = 1.0  # Default fallback
    
    def calculate_intervals(self, forecast: pd.Series, confidence_levels: List[float], 
                          horizon: int) -> Dict[str, List[float]]:
        """Calculate prediction intervals"""
        self.logger.info(f"Calculating intervals for {len(confidence_levels)} confidence levels")
        
        intervals = {}
        
        if self.residuals_std is None:
            self.residuals_std = 1.0
        
        # Convert forecast to numpy array
        if isinstance(forecast, pd.Series):
            forecast_values = forecast.values
        else:
            forecast_values = np.array(forecast)
        
        for confidence_level in confidence_levels:
            # Calculate z-score for confidence level
            alpha = 1 - confidence_level
            z_score = self._get_z_score(alpha / 2)
            
            # Calculate interval width
            interval_width = z_score * self.residuals_std
            
            # Calculate bounds
            lower_bound = forecast_values - interval_width
            upper_bound = forecast_values + interval_width
            
            intervals[f'lower_{confidence_level}'] = lower_bound.tolist()
            intervals[f'upper_{confidence_level}'] = upper_bound.tolist()
        
        return intervals
    
    def get_confidence_score(self, forecast: pd.Series) -> float:
        """Calculate confidence score"""
        if self.residuals_std is None:
            return 0.5
        
        # Lower residual std = higher confidence
        max_std = 10.0
        confidence = max(0, 1 - (self.residuals_std / max_std))
        return min(1.0, confidence)
    
    def _get_z_score(self, alpha: float) -> float:
        """Get z-score for confidence level"""
        z_scores = {
            0.025: 1.96,   # 95% confidence
            0.05: 1.645,   # 90% confidence
            0.1: 1.282,    # 80% confidence
            0.25: 0.674,   # 50% confidence
        }
        return z_scores.get(alpha, 1.96)