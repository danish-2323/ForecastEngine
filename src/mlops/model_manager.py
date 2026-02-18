# src/mlops/model_manager.py

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path

class ModelManager:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model_registry_path = Path(config.get('model_registry_path', 'models'))
        self.model_registry_path.mkdir(exist_ok=True)
        
        self.current_version = None
        self.performance_history = []
        
    def save_model(self, models: Dict, ensemble, metadata: Dict) -> str:
        """Save models with versioning"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"v{timestamp}"
        
        version_path = self.model_registry_path / version
        version_path.mkdir(exist_ok=True)
        
        try:
            # Save models
            models_path = version_path / "models"
            models_path.mkdir(exist_ok=True)
            
            for model_name, model in models.items():
                model_file = models_path / f"{model_name}.pkl"
                with open(model_file, 'wb') as f:
                    pickle.dump(model, f)
            
            # Save ensemble
            ensemble_file = version_path / "ensemble.pkl"
            with open(ensemble_file, 'wb') as f:
                pickle.dump(ensemble, f)
            
            # Save metadata
            metadata_file = version_path / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            self.current_version = version
            self.logger.info(f"Model saved as version {version}")
            return version
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            raise
    
    def load_model(self, version: Optional[str] = None):
        """Load models from registry"""
        if version is None:
            version = self.get_latest_version()
        
        if version is None:
            raise ValueError("No models found")
        
        version_path = self.model_registry_path / version
        
        try:
            # Load models
            models = {}
            models_path = version_path / "models"
            
            for model_file in models_path.glob("*.pkl"):
                model_name = model_file.stem
                with open(model_file, 'rb') as f:
                    models[model_name] = pickle.load(f)
            
            # Load ensemble
            ensemble_file = version_path / "ensemble.pkl"
            with open(ensemble_file, 'rb') as f:
                ensemble = pickle.load(f)
            
            # Load metadata
            metadata_file = version_path / "metadata.json"
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            return models, ensemble, metadata
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def check_performance_drift(self, current_metrics: Dict[str, float], 
                               threshold: float = 0.1) -> bool:
        """Check for performance drift"""
        if not self.performance_history:
            self.performance_history.append({
                'timestamp': datetime.now(),
                'metrics': current_metrics
            })
            return False
        
        # Get baseline (last 5 measurements)
        recent_history = self.performance_history[-5:]
        baseline_mae = np.mean([h['metrics'].get('mae', float('inf')) for h in recent_history])
        
        current_mae = current_metrics.get('mae', float('inf'))
        
        if baseline_mae > 0:
            drift = abs(current_mae - baseline_mae) / baseline_mae
            
            self.performance_history.append({
                'timestamp': datetime.now(),
                'metrics': current_metrics
            })
            
            # Keep only last 20 measurements
            self.performance_history = self.performance_history[-20:]
            
            if drift > threshold:
                self.logger.warning(f"Performance drift detected: {drift:.3f}")
                return True
        
        return False
    
    def check_data_drift(self, current_data: pd.DataFrame, threshold: float = 0.05) -> bool:
        """Simple data drift detection"""
        # Simplified - always return False for minimal implementation
        return False
    
    def should_retrain(self, current_metrics: Dict[str, float], 
                      current_data: pd.DataFrame) -> Dict[str, bool]:
        """Determine if retraining is needed"""
        triggers = {
            'performance_drift': self.check_performance_drift(current_metrics),
            'data_drift': self.check_data_drift(current_data),
            'time_based': self._check_time_based_trigger()
        }
        
        return triggers
    
    def get_latest_version(self) -> Optional[str]:
        """Get latest model version"""
        if self.current_version:
            return self.current_version
        
        version_dirs = [d for d in self.model_registry_path.iterdir() 
                       if d.is_dir() and d.name.startswith('v')]
        
        if not version_dirs:
            return None
        
        latest_version = max(version_dirs, key=lambda x: x.stat().st_mtime)
        return latest_version.name
    
    def get_current_version(self) -> Optional[str]:
        return self.current_version
    
    def get_last_training_time(self) -> Optional[datetime]:
        if not self.performance_history:
            return None
        return self.performance_history[-1]['timestamp']
    
    def _check_time_based_trigger(self) -> bool:
        """Check time-based retraining trigger"""
        if not self.performance_history:
            return False
        
        last_training = self.performance_history[-1]['timestamp']
        time_threshold = timedelta(days=self.config.get('retrain_days', 7))
        
        return datetime.now() - last_training > time_threshold