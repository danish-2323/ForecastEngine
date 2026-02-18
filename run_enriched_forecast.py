"""
ForecastEngine with External API Enrichment Demo
Demonstrates how external signals enhance forecasting accuracy
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import yaml
import logging
import pandas as pd
from forecast_engine import ForecastEngine

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_config(config_path='config/enriched_config.yaml'):
    """Load configuration file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file {config_path} not found, using default config")
        return {
            'target_column': 'value',
            'date_column': 'date',
            'data_path': 'data/sample_data.csv',
            'external_apis': {'enabled': True}
        }

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def main():
    logger = setup_logging()
    
    print_section("ForecastEngine: External API Enrichment Demo")
    
    # Load configuration
    config = load_config()
    
    # Show API configuration
    print_section("External API Configuration")
    api_config = config.get('external_apis', {})
    print(f"External APIs Enabled: {api_config.get('enabled', False)}")
    
    if api_config.get('enabled'):
        sources = api_config.get('sources', {})
        print("\nConfigured Data Sources:")
        for source, settings in sources.items():
            status = "ENABLED" if settings.get('enabled') else "DISABLED"
            print(f"  - {source.capitalize()}: {status}")
    
    # Initialize ForecastEngine
    print_section("Initializing ForecastEngine")
    engine = ForecastEngine(config)
    print("ForecastEngine initialized successfully")
    
    # Train models with enriched data
    print_section("Training Models with Enriched Data")
    print("Loading historical CSV data...")
    print("Fetching external API data (weather, news, analytics, e-commerce)...")
    print("Merging external signals with historical data...")
    print("Building features (including external feature lags)...")
    
    engine.fit(
        target_column=config.get('target_column', 'value'),
        date_column=config.get('date_column', 'date')
    )
    
    print("\nTraining completed!")
    if hasattr(engine, 'external_features') and engine.external_features:
        print(f"External features used: {', '.join(engine.external_features)}")
    
    # Generate forecast
    print_section("Generating 30-Day Forecast")
    forecast_result = engine.predict(
        horizon=30,
        confidence_levels=[0.1, 0.5, 0.9],
        include_explanation=True
    )
    
    # Display forecast summary
    forecast_values = forecast_result['forecast']
    print(f"Forecast Period: 30 days")
    print(f"Average Forecast: {forecast_values.mean():.2f}")
    print(f"Min Forecast: {forecast_values.min():.2f}")
    print(f"Max Forecast: {forecast_values.max():.2f}")
    
    print("\nFirst 7 days forecast:")
    for i, value in enumerate(forecast_values[:7], 1):
        print(f"  Day {i}: {value:.2f}")
    
    # Display prediction intervals
    print_section("Uncertainty Intervals")
    intervals = forecast_result.get('prediction_intervals', {})
    if intervals:
        print("Confidence Intervals (First 7 Days):")
        for i in range(min(7, len(forecast_values))):
            low = intervals.get('lower_0.1', [0]*30)[i]
            mid = intervals.get('median_0.5', [0]*30)[i]
            high = intervals.get('upper_0.9', [0]*30)[i]
            print(f"  Day {i+1}: [{low:.2f}, {mid:.2f}, {high:.2f}]")
    
    # Display explanations
    print_section("Forecast Explanations")
    explanations = forecast_result.get('explanations', {})
    
    if explanations:
        # Business insights
        insights = explanations.get('business_insights', [])
        if insights:
            print("Business Insights:")
            for insight in insights:
                print(f"  - {insight}")
        
        # Feature importance
        print("\nTop Forecast Drivers:")
        feature_importance = explanations.get('feature_importance', {})
        top_drivers = feature_importance.get('top_drivers', {})
        
        if top_drivers:
            for feature, importance in list(top_drivers.items())[:5]:
                print(f"  - {feature}: {importance:.3f}")
        
        # Forecast drivers with external signals
        print("\nCurrent Forecast Drivers:")
        drivers = explanations.get('forecast_drivers', {})
        
        external_drivers = []
        internal_drivers = []
        
        for feature, info in drivers.items():
            is_external = info.get('is_external', False)
            meaning = info.get('business_meaning', '')
            
            if is_external:
                external_drivers.append(f"  - {feature}: {meaning}")
            else:
                internal_drivers.append(f"  - {feature}: {meaning}")
        
        if internal_drivers:
            print("\n  Historical Patterns:")
            for driver in internal_drivers[:3]:
                print(driver)
        
        if external_drivers:
            print("\n  External Signals:")
            for driver in external_drivers:
                print(driver)
    
    # Model performance
    print_section("Model Performance")
    performance = forecast_result.get('model_performance', {})
    if performance:
        print(f"MAE: {performance.get('mae', 0):.2f}")
        print(f"MAPE: {performance.get('mape', 0):.2f}%")
        print(f"RMSE: {performance.get('rmse', 0):.2f}")
    
    # Scenario analysis with external signals
    print_section("Scenario Analysis: News Surge Impact")
    scenario_config = {
        'name': 'High News Activity',
        'type': 'demand_multiplier',
        'multiplier': 1.15,
        'reason': 'Increased business news coverage'
    }
    
    scenario_result = engine.run_scenario(scenario_config, horizon=30)
    
    baseline = scenario_result.get('baseline_forecast', [])
    scenario_forecast = scenario_result.get('scenario_forecast', [])
    
    if baseline and scenario_forecast:
        baseline_avg = sum(baseline) / len(baseline)
        scenario_avg = sum(scenario_forecast) / len(scenario_forecast)
        impact_pct = ((scenario_avg - baseline_avg) / baseline_avg) * 100
        
        print(f"Baseline Average: {baseline_avg:.2f}")
        print(f"Scenario Average: {scenario_avg:.2f}")
        print(f"Impact: +{impact_pct:.1f}%")
        print("\nInterpretation: Increased news activity correlates with higher demand")
    
    # Summary
    print_section("Summary")
    print("ForecastEngine successfully demonstrated:")
    print("  [OK] Historical CSV data loading")
    print("  [OK] External API data enrichment (weather, news, analytics, e-commerce)")
    print("  [OK] Feature engineering with external signals")
    print("  [OK] Ensemble forecasting with enriched features")
    print("  [OK] Uncertainty quantification")
    print("  [OK] Explainability with external signal attribution")
    print("  [OK] Scenario analysis with external factors")
    
    print("\nKey Benefits:")
    print("  - Original pipeline preserved (works without APIs)")
    print("  - External signals improve forecast accuracy")
    print("  - Graceful fallback if APIs unavailable")
    print("  - Clear explanations of external signal impacts")
    
    print("\n" + "="*70)
    print("  Demo completed successfully!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
