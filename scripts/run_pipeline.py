# scripts/run_pipeline.py

"""
ForecastEngine Pipeline Runner
CLI script to run the complete forecasting pipeline
"""

import sys
import os
from pathlib import Path
import argparse
import yaml
import logging
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from forecast_engine import ForecastEngine

def setup_logging(log_level="INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'logs/pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    return logging.getLogger(__name__)

def load_config(config_path):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {
            'target_column': 'value',
            'date_column': 'date',
            'data_path': 'data/sample_data.csv'
        }

def run_training_pipeline(config, args):
    """Run the complete training pipeline"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ForecastEngine training pipeline...")
    
    # Initialize engine
    engine = ForecastEngine(config)
    
    # Train models
    logger.info("Training models...")
    engine.fit(
        target_column=config.get('target_column', 'value'),
        date_column=config.get('date_column', 'date'),
        external_features=args.external_features
    )
    
    # Generate sample forecast
    logger.info("Generating sample forecast...")
    forecast_result = engine.predict(
        horizon=args.horizon,
        confidence_levels=[0.1, 0.5, 0.9],
        include_explanation=True
    )
    
    # Save results
    if args.output_dir:
        output_path = Path(args.output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save forecast
        import json
        with open(output_path / f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(forecast_result, f, indent=2, default=str)
        
        logger.info(f"Results saved to {output_path}")
    
    # Print summary
    logger.info("=== PIPELINE RESULTS ===")
    logger.info(f"Forecast horizon: {args.horizon} days")
    logger.info(f"Mean forecast: {sum(forecast_result['forecast']) / len(forecast_result['forecast']):.2f}")
    
    if forecast_result.get('explanations'):
        insights = forecast_result['explanations'].get('business_insights', [])
        logger.info("Key insights:")
        for insight in insights[:3]:
            logger.info(f"  - {insight}")
    
    logger.info("Pipeline completed successfully!")
    return forecast_result

def run_evaluation_pipeline(config, args):
    """Run model evaluation pipeline"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting evaluation pipeline...")
    
    engine = ForecastEngine(config)
    engine.fit(
        target_column=config.get('target_column', 'value'),
        date_column=config.get('date_column', 'date')
    )
    
    # Run evaluation
    performance = engine.evaluate_performance()
    
    logger.info("=== EVALUATION RESULTS ===")
    for model_name, metrics in performance.items():
        if isinstance(metrics, dict):
            logger.info(f"{model_name}:")
            for metric, value in metrics.items():
                logger.info(f"  {metric}: {value:.3f}")
    
    return performance

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="ForecastEngine Pipeline Runner")
    
    parser.add_argument('--config', '-c', default='config/simple_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--mode', '-m', choices=['train', 'evaluate', 'both'], default='train',
                       help='Pipeline mode to run')
    parser.add_argument('--horizon', '-h', type=int, default=30,
                       help='Forecast horizon in days')
    parser.add_argument('--external-features', nargs='*', 
                       help='External features to include')
    parser.add_argument('--output-dir', '-o', 
                       help='Output directory for results')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    os.makedirs('logs', exist_ok=True)
    logger = setup_logging(args.log_level)
    
    try:
        # Load configuration
        config = load_config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
        
        # Run pipeline based on mode
        if args.mode in ['train', 'both']:
            train_results = run_training_pipeline(config, args)
        
        if args.mode in ['evaluate', 'both']:
            eval_results = run_evaluation_pipeline(config, args)
        
        logger.info("All pipelines completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()