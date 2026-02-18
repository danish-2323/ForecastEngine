# src/scenarios/scenario_engine.py

import pandas as pd
import numpy as np
from typing import Dict
import logging

class ScenarioEngine:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def run_scenario(self, scenario_config: Dict, models: Dict, ensemble, horizon: int) -> Dict:
        """Run what-if scenario analysis"""
        self.logger.info(f"Running scenario: {scenario_config.get('name', 'unnamed')}")
        
        # Get baseline forecast
        baseline_forecast = self._get_baseline_forecast(models, ensemble, horizon)
        
        # Apply scenario modifications
        scenario_forecast = self._apply_scenario_modifications(
            baseline_forecast, scenario_config, horizon
        )
        
        # Calculate impact
        impact_analysis = self._calculate_impact_analysis(
            baseline_forecast, scenario_forecast, scenario_config
        )
        
        return {
            'scenario_name': scenario_config.get('name', 'unnamed'),
            'scenario_forecast': scenario_forecast.tolist() if hasattr(scenario_forecast, 'tolist') else scenario_forecast,
            'baseline_forecast': baseline_forecast.tolist() if hasattr(baseline_forecast, 'tolist') else baseline_forecast,
            'impact_analysis': impact_analysis,
            'scenario_config': scenario_config
        }
    
    def _get_baseline_forecast(self, models, ensemble, horizon):
        """Get baseline forecast"""
        # Create dummy features for prediction
        dummy_features = pd.DataFrame({
            'lag_1': [100] * horizon,
            'lag_7': [100] * horizon,
            'rolling_mean_7': [100] * horizon,
            'day_of_week': [1] * horizon,
            'month': [1] * horizon
        })
        
        try:
            baseline = ensemble.predict(dummy_features, horizon=horizon, models=models)
            return baseline
        except Exception as e:
            self.logger.warning(f"Baseline forecast failed: {e}")
            return np.array([100.0] * horizon)
    
    def _apply_scenario_modifications(self, baseline_forecast, scenario_config, horizon):
        """Apply scenario modifications"""
        scenario_forecast = np.array(baseline_forecast).copy()
        
        # Price change impact
        if 'price_change' in scenario_config:
            price_elasticity = scenario_config.get('price_elasticity', -0.5)
            price_change = scenario_config['price_change']
            demand_change = price_elasticity * price_change
            scenario_forecast *= (1 + demand_change)
        
        # Demand multiplier
        if 'demand_multiplier' in scenario_config:
            multiplier = scenario_config['demand_multiplier']
            scenario_forecast *= multiplier
        
        # Seasonal boost
        if 'seasonal_boost' in scenario_config:
            boost = scenario_config['seasonal_boost']
            for i in range(horizon):
                decay_factor = max(0.1, 1 - (i / horizon) * 0.5)
                scenario_forecast[i] *= (1 + boost * decay_factor)
        
        # Economic impact
        if 'economic_impact' in scenario_config:
            impact = scenario_config['economic_impact']
            scenario_forecast *= (1 + impact)
        
        return scenario_forecast
    
    def _calculate_impact_analysis(self, baseline_forecast, scenario_forecast, scenario_config):
        """Calculate scenario impact"""
        baseline_array = np.array(baseline_forecast)
        scenario_array = np.array(scenario_forecast)
        
        absolute_difference = scenario_array - baseline_array
        percentage_difference = ((scenario_array - baseline_array) / baseline_array) * 100
        
        return {
            'total_impact': {
                'absolute': float(np.sum(absolute_difference)),
                'percentage': float(np.mean(percentage_difference))
            },
            'average_impact': {
                'absolute': float(np.mean(absolute_difference)),
                'percentage': float(np.mean(percentage_difference))
            },
            'impact_timeline': {
                'absolute': absolute_difference.tolist(),
                'percentage': percentage_difference.tolist()
            }
        }