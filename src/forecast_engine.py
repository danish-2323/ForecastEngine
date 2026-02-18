"""
ForecastEngine: Enterprise AI-Powered Forecasting Platform
Main orchestration class that coordinates all forecasting components
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging

from data_ingestion.data_connector import DataConnector
from feature_engineering.feature_builder import FeatureBuilder
from models.model_factory import ModelFactory
from ensemble.ensemble_manager import EnsembleManager
from uncertainty.uncertainty_quantifier import UncertaintyQuantifier
from explainability.explainer import ForecastExplainer
from scenarios.scenario_engine import ScenarioEngine
from evaluation.evaluator import ModelEvaluator
from mlops.model_manager import ModelManager
import yaml
import logging

class ForecastEngine:
    """
    Main ForecastEngine class that orchestrates the entire forecasting pipeline
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ForecastEngine with configuration
        
        Args:
            config: Configuration dictionary containing all settings
        """
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize components
        self.data_connector = DataConnector(config)
        self.feature_builder = FeatureBuilder(config.get('features', {}))
        self.model_factory = ModelFactory(config.get('models', {}))
        self.ensemble_manager = EnsembleManager(config.get('ensemble', {}))
        self.uncertainty_quantifier = UncertaintyQuantifier(config.get('uncertainty', {}))
        self.explainer = ForecastExplainer(config.get('explainability', {}))
        self.scenario_engine = ScenarioEngine(config.get('scenarios', {}))
        self.evaluator = ModelEvaluator(config.get('evaluation', {}))
        
        self.models = {}
        self.is_trained = False
        
    def fit(self, 
            target_column: str,
            date_column: str,
            external_features: Optional[List[str]] = None,
            train_end_date: Optional[str] = None) -> 'ForecastEngine':
        """
        Train the forecasting models on historical data
        
        Args:
            target_column: Name of the target variable to forecast
            date_column: Name of the date column
            external_features: List of external feature columns (auto-detected if None)
            train_end_date: End date for training data
            
        Returns:
            Self for method chaining
        """
        self.logger.info("Starting ForecastEngine training...")
        
        # 1. Load and validate data (automatically enriched with external APIs)
        data = self.data_connector.load_training_data(
            target_column=target_column,
            date_column=date_column,
            end_date=train_end_date
        )
        
        # Auto-detect external features if not provided
        if external_features is None:
            external_features = self.data_connector.get_external_features()
            if external_features:
                self.logger.info(f"Auto-detected external features: {external_features}")
        
        # Store for later use
        self.external_features = external_features
        
        # 2. Build features
        features_data = self.feature_builder.build_features(
            data=data,
            target_column=target_column,
            date_column=date_column,
            external_features=external_features
        )
        
        # 3. Train individual models
        self.models = self.model_factory.train_models(
            data=features_data,
            target_column=target_column,
            date_column=date_column
        )
        
        # 4. Train ensemble
        self.ensemble_manager.fit(
            models=self.models,
            data=features_data,
            target_column=target_column
        )
        
        # 5. Fit uncertainty quantifier
        self.uncertainty_quantifier.fit(
            models=self.models,
            ensemble=self.ensemble_manager,
            data=features_data,
            target_column=target_column
        )
        
        self.is_trained = True
        self.logger.info("ForecastEngine training completed successfully")
        
        return self
    
    def predict(self, 
                horizon: int,
                confidence_levels: List[float] = [0.1, 0.5, 0.9],
                include_explanation: bool = True) -> Dict[str, Any]:
        """
        Generate forecasts with uncertainty intervals and explanations
        
        Args:
            horizon: Number of periods to forecast
            confidence_levels: Confidence levels for prediction intervals
            include_explanation: Whether to include forecast explanations
            
        Returns:
            Dictionary containing forecasts, intervals, and explanations
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
            
        self.logger.info(f"Generating forecasts for {horizon} periods...")
        
        # 1. Get latest data for prediction
        latest_data = self.data_connector.load_latest_data()
        
        # 2. Build features for prediction
        prediction_features = self.feature_builder.build_prediction_features(
            data=latest_data,
            horizon=horizon
        )
        
        # 3. Generate ensemble predictions
        ensemble_forecast = self.ensemble_manager.predict(
            features=prediction_features,
            horizon=horizon,
            models=self.models
        )
        
        # 4. Calculate uncertainty intervals
        uncertainty_intervals = self.uncertainty_quantifier.calculate_intervals(
            forecast=ensemble_forecast,
            confidence_levels=confidence_levels,
            horizon=horizon
        )
        
        # 5. Generate explanations
        explanations = None
        if include_explanation:
            explanations = self.explainer.explain_forecast(
                forecast=ensemble_forecast,
                features=prediction_features,
                models=self.models,
                ensemble=self.ensemble_manager
            )
        
        # 6. Compile results
        results = {
            'forecast': ensemble_forecast,
            'prediction_intervals': uncertainty_intervals,
            'confidence_levels': confidence_levels,
            'horizon': horizon,
            'timestamp': datetime.now().isoformat(),
            'model_performance': self.evaluator.get_latest_metrics(),
            'explanations': explanations
        }
        
        self.logger.info("Forecast generation completed")
        return results
    
    def run_scenario(self, 
                    scenario_config: Dict[str, Any],
                    horizon: int) -> Dict[str, Any]:
        """
        Run what-if scenario analysis
        
        Args:
            scenario_config: Configuration for the scenario
            horizon: Forecast horizon for the scenario
            
        Returns:
            Scenario analysis results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before running scenarios")
            
        return self.scenario_engine.run_scenario(
            scenario_config=scenario_config,
            models=self.models,
            ensemble=self.ensemble_manager,
            horizon=horizon
        )
    
    def evaluate_performance(self, 
                           test_data: Optional[pd.DataFrame] = None,
                           metrics: List[str] = ['mae', 'mape', 'rmse']) -> Dict[str, float]:
        """
        Evaluate model performance on test data
        
        Args:
            test_data: Test dataset for evaluation
            metrics: List of metrics to calculate
            
        Returns:
            Dictionary of performance metrics
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
            
        if test_data is None:
            test_data = self.data_connector.load_test_data()
            
        return self.evaluator.evaluate(
            models=self.models,
            ensemble=self.ensemble_manager,
            test_data=test_data,
            metrics=metrics
        )
    
    def retrain(self, trigger_reason: str = "scheduled") -> bool:
        """
        Retrain models with latest data
        
        Args:
            trigger_reason: Reason for retraining
            
        Returns:
            Success status
        """
        try:
            self.logger.info(f"Starting model retraining. Reason: {trigger_reason}")
            
            # Check if retraining is needed
            if not self._should_retrain():
                self.logger.info("Retraining not needed based on performance metrics")
                return False
            
            # Retrain with latest data
            self.fit(
                target_column=self.config['target_column'],
                date_column=self.config['date_column'],
                external_features=self.config.get('external_features')
            )
            
            self.logger.info("Model retraining completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Retraining failed: {str(e)}")
            return False
    
    def _should_retrain(self) -> bool:
        """
        Determine if model retraining is needed based on performance drift
        """
        current_performance = self.evaluator.get_latest_metrics()
        performance_threshold = self.config.get('retrain_threshold', 0.1)
        
        # Check if performance has degraded beyond threshold
        if current_performance.get('mae_drift', 0) > performance_threshold:
            return True
            
        # Check data drift
        if self.data_connector.detect_data_drift():
            return True
            
        return False
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('ForecastEngine')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

def main():
    """Main function to run ForecastEngine"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting ForecastEngine...")
    
    try:
        # Load configuration
        config_path = "config/simple_config.yaml"
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using default config")
            config = {
                'target_column': 'value',
                'date_column': 'date',
                'data_path': 'data/sample_data.csv'
            }
        
        # Initialize ForecastEngine
        engine = ForecastEngine(config)
        
        # Train the model
        logger.info("Training models...")
        engine.fit(
            target_column=config.get('target_column', 'value'),
            date_column=config.get('date_column', 'date')
        )
        
        # Generate forecast
        logger.info("Generating forecast...")
        forecast_result = engine.predict(
            horizon=30,
            confidence_levels=[0.1, 0.5, 0.9],
            include_explanation=True
        )
        
        # Display results
        logger.info("Forecast Results:")
        logger.info(f"30-day forecast: {forecast_result['forecast'][:5]}... (showing first 5 values)")
        
        if forecast_result.get('explanations'):
            logger.info("Key insights:")
            for insight in forecast_result['explanations'].get('business_insights', []):
                logger.info(f"  - {insight}")
        
        # Run scenario analysis
        logger.info("Running scenario analysis...")
        scenario_config = {
            'name': 'Price Increase Test',
            'type': 'price_change',
            'price_change': 0.1,
            'price_elasticity': -0.5
        }
        
        scenario_result = engine.run_scenario(scenario_config, horizon=30)
        logger.info(f"Scenario impact: {scenario_result['impact_analysis']['total_impact']['percentage']:.1f}%")
        
        # Evaluate performance
        logger.info("Evaluating model performance...")
        performance = engine.evaluate_performance()
        logger.info(f"Model performance: {performance}")
        
        logger.info("ForecastEngine completed successfully!")
        
    except Exception as e:
        logger.error(f"ForecastEngine failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()