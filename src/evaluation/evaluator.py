# src/evaluation/evaluator.py

import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging

class ModelEvaluator:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.latest_metrics = {}
        
    def evaluate(self, models: Dict, ensemble, test_data: pd.DataFrame, 
                metrics: List[str] = ['mae', 'mape', 'rmse']) -> Dict[str, float]:
        """Evaluate model performance"""
        self.logger.info("Evaluating models...")
        
        target_column = self.config.get('target_column', 'value')
        feature_columns = [col for col in test_data.columns 
                          if col not in [target_column, 'date'] and not col.startswith('Unnamed')]
        
        X_test = test_data[feature_columns]
        y_test = test_data[target_column].values
        
        results = {}
        
        # Evaluate individual models
        for model_name, model in models.items():
            try:
                predictions = model.predict(X_test)
                model_metrics = self._calculate_metrics(y_test, predictions, metrics)
                results[model_name] = model_metrics
            except Exception as e:
                self.logger.warning(f"Evaluation failed for {model_name}: {e}")
                results[model_name] = {metric: float('inf') for metric in metrics}
        
        # Evaluate ensemble
        try:
            ensemble_predictions = ensemble.predict(X_test, horizon=len(X_test), models=models)
            ensemble_metrics = self._calculate_metrics(y_test, ensemble_predictions, metrics)
            results['ensemble'] = ensemble_metrics
        except Exception as e:
            self.logger.warning(f"Ensemble evaluation failed: {e}")
            results['ensemble'] = {metric: float('inf') for metric in metrics}
        
        self.latest_metrics = results
        return results
    
    def backtest(self, models: Dict, data: pd.DataFrame, target_column: str, 
                test_size: float = 0.2, n_splits: int = 3) -> Dict:
        """Perform time-series backtesting"""
        self.logger.info(f"Backtesting with {n_splits} splits...")
        
        results = {model_name: [] for model_name in models.keys()}
        total_size = len(data)
        test_samples = int(total_size * test_size)
        
        for split in range(n_splits):
            test_end = total_size - (split * (test_samples // n_splits))
            test_start = test_end - test_samples
            train_end = test_start
            
            if train_end < test_samples:
                break
                
            train_data = data.iloc[:train_end]
            test_data = data.iloc[test_start:test_end]
            
            for model_name, model in models.items():
                try:
                    model.fit(train_data, target_column)
                    
                    feature_columns = [col for col in test_data.columns 
                                     if col not in [target_column, 'date'] and not col.startswith('Unnamed')]
                    X_test = test_data[feature_columns]
                    y_test = test_data[target_column].values
                    
                    predictions = model.predict(X_test)
                    mae = mean_absolute_error(y_test, predictions)
                    results[model_name].append(mae)
                    
                except Exception as e:
                    self.logger.warning(f"Backtesting failed for {model_name}: {e}")
                    results[model_name].append(float('inf'))
        
        # Calculate summary
        backtest_summary = {}
        for model_name, scores in results.items():
            if scores:
                backtest_summary[model_name] = {
                    'mean_mae': np.mean(scores),
                    'std_mae': np.std(scores)
                }
        
        return backtest_summary
    
    def get_latest_metrics(self) -> Dict:
        return self.latest_metrics.copy()
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, metrics: List[str]) -> Dict[str, float]:
        """Calculate performance metrics"""
        results = {}
        
        # Ensure same length
        min_len = min(len(y_true), len(y_pred))
        y_true = y_true[:min_len]
        y_pred = y_pred[:min_len]
        
        for metric in metrics:
            try:
                if metric.lower() == 'mae':
                    results['mae'] = mean_absolute_error(y_true, y_pred)
                elif metric.lower() == 'mape':
                    results['mape'] = self._calculate_mape(y_true, y_pred)
                elif metric.lower() == 'rmse':
                    results['rmse'] = np.sqrt(mean_squared_error(y_true, y_pred))
            except Exception as e:
                self.logger.warning(f"Failed to calculate {metric}: {e}")
                results[metric] = float('inf')
        
        return results
    
    def _calculate_mape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate Mean Absolute Percentage Error"""
        mask = y_true != 0
        if not np.any(mask):
            return float('inf')
        return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100