# src/ensemble/ensemble_manager.py

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from sklearn.metrics import mean_absolute_error
import logging

class EnsembleManager:
    def __init__(self, config: dict):
        self.config = config
        self.method = config.get('method', 'weighted_average')
        self.weights = {}
        self.logger = logging.getLogger(__name__)
        
    def fit(self, models: Dict[str, Any], data: pd.DataFrame, target_column: str):
        """Train ensemble on validation data"""
        self.logger.info(f"Training ensemble using {self.method}")
        
        if self.method == 'weighted_average':
            self._fit_weighted_average(models, data, target_column)
        else:
            # Simple average as fallback
            self.weights = {name: 1.0/len(models) for name in models.keys()}
    
    def predict(self, features: pd.DataFrame, horizon: int, models: Optional[Dict[str, Any]] = None) -> pd.Series:
        """Generate ensemble predictions"""
        if models is None:
            raise ValueError("Models must be provided to ensemble.predict()")
            
        model_predictions = {}
        for model_name, model in models.items():
            try:
                pred = model.predict(features)
                model_predictions[model_name] = pred
            except Exception as e:
                self.logger.warning(f"Model {model_name} prediction failed: {e}")
                continue
        
        if not model_predictions:
            raise ValueError("No models produced predictions")
            
        # Combine predictions
        ensemble_pred = np.zeros_like(list(model_predictions.values())[0])
        total_weight = 0
        
        for model_name, predictions in model_predictions.items():
            weight = self.weights.get(model_name, 1.0/len(model_predictions))
            ensemble_pred += weight * predictions
            total_weight += weight
            
        if total_weight > 0:
            ensemble_pred /= total_weight
            
        return pd.Series(ensemble_pred)
    
    def _fit_weighted_average(self, models, data, target_column):
        """Calculate performance-based weights"""
        # Split data for validation
        split_point = int(len(data) * 0.8)
        train_data = data.iloc[:split_point]
        val_data = data.iloc[split_point:]
        
        weights = {}
        total_inverse_error = 0
        
        for model_name, model in models.items():
            try:
                # Retrain on train split
                model.fit(train_data, target_column)
                
                # Predict on validation
                feature_columns = [col for col in val_data.columns 
                                 if col not in [target_column, 'date'] and not col.startswith('Unnamed')]
                X_val = val_data[feature_columns]
                y_val = val_data[target_column].values
                
                pred = model.predict(X_val)
                mae = mean_absolute_error(y_val, pred)
                
                # Inverse error for weight (better models get higher weights)
                inverse_error = 1.0 / (mae + 1e-8)
                weights[model_name] = inverse_error
                total_inverse_error += inverse_error
                
            except Exception as e:
                self.logger.warning(f"Weight calculation failed for {model_name}: {e}")
                weights[model_name] = 0.1  # Small default weight
                total_inverse_error += 0.1
        
        # Normalize weights
        for model_name in weights:
            weights[model_name] /= total_inverse_error
            
        self.weights = weights
        self.logger.info(f"Model weights: {weights}")
    
    def get_model_weights(self) -> Dict[str, float]:
        return self.weights.copy()
    
    def get_ensemble_info(self) -> Dict[str, Any]:
        return {
            'method': self.method,
            'weights': self.weights,
            'num_models': len(self.weights)
        }