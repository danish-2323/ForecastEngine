# scripts/backfill_data.py

"""
ForecastEngine Data Backfill Script
CLI script to backfill historical forecasts and retrain models
"""

import sys
import os
from pathlib import Path
import argparse
import pandas as pd
import yaml
import logging
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from forecast_engine import ForecastEngine
from data_ingestion.data_connector import DataConnector

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_config(config_path):
    """Load configuration"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {
            'target_column': 'value',
            'date_column': 'date',
            'data_path': 'data/sample_data.csv'
        }

def generate_date_ranges(start_date, end_date, window_days=30):
    """Generate date ranges for backfill processing"""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    ranges = []
    current = start
    
    while current < end:
        range_end = min(current + timedelta(days=window_days), end)
        ranges.append((current, range_end))
        current = range_end + timedelta(days=1)
    
    return ranges

def backfill_forecasts(config, args):
    """Backfill historical forecasts"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting forecast backfill process...")
    
    # Load data
    data_connector = DataConnector(config)
    full_data = data_connector.load_training_data(
        target_column=config['target_column'],
        date_column=config['date_column']
    )
    
    logger.info(f"Loaded {len(full_data)} records from {full_data[config['date_column']].min()} to {full_data[config['date_column']].max()}")
    
    # Generate date ranges for backfill
    date_ranges = generate_date_ranges(args.start_date, args.end_date, args.window_days)
    
    logger.info(f"Processing {len(date_ranges)} date ranges...")
    
    backfill_results = []
    
    for i, (range_start, range_end) in enumerate(date_ranges):
        logger.info(f"Processing range {i+1}/{len(date_ranges)}: {range_start.date()} to {range_end.date()}")
        
        try:
            # Filter training data up to range_start
            train_data = full_data[full_data[config['date_column']] <= range_start]
            
            if len(train_data) < args.min_train_samples:
                logger.warning(f"Insufficient training data ({len(train_data)} samples), skipping...")
                continue
            
            # Initialize and train engine
            engine = ForecastEngine(config)
            engine.fit(
                target_column=config['target_column'],
                date_column=config['date_column'],
                train_end_date=range_start.strftime('%Y-%m-%d')
            )
            
            # Generate forecast
            forecast_result = engine.predict(
                horizon=args.forecast_horizon,
                confidence_levels=[0.1, 0.5, 0.9],
                include_explanation=False  # Skip explanations for speed
            )
            
            # Store results
            result = {
                'forecast_date': range_start.strftime('%Y-%m-%d'),
                'train_samples': len(train_data),
                'forecast_horizon': args.forecast_horizon,
                'forecast_mean': sum(forecast_result['forecast']) / len(forecast_result['forecast']),
                'forecast_values': forecast_result['forecast']
            }
            
            backfill_results.append(result)
            
            if args.save_individual and args.output_dir:
                # Save individual forecast
                output_path = Path(args.output_dir)
                output_path.mkdir(exist_ok=True)
                
                import json
                with open(output_path / f"backfill_{range_start.strftime('%Y%m%d')}.json", 'w') as f:
                    json.dump(result, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to process range {range_start.date()}: {str(e)}")
            continue
    
    # Save consolidated results
    if args.output_dir:
        output_path = Path(args.output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save as JSON
        import json
        with open(output_path / f"backfill_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(backfill_results, f, indent=2, default=str)
        
        # Save as CSV for analysis
        if backfill_results:
            summary_data = []
            for result in backfill_results:
                summary_data.append({
                    'forecast_date': result['forecast_date'],
                    'train_samples': result['train_samples'],
                    'forecast_mean': result['forecast_mean']
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_csv(output_path / f"backfill_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)
        
        logger.info(f"Results saved to {output_path}")
    
    logger.info(f"Backfill completed: {len(backfill_results)} successful forecasts")
    return backfill_results

def validate_backfill_results(config, backfill_results):
    """Validate backfill results against actual data"""
    logger = logging.getLogger(__name__)
    
    logger.info("Validating backfill results...")
    
    # Load actual data
    data_connector = DataConnector(config)
    actual_data = data_connector.load_training_data(
        target_column=config['target_column'],
        date_column=config['date_column']
    )
    
    validation_results = []
    
    for result in backfill_results:
        forecast_date = pd.to_datetime(result['forecast_date'])
        horizon = result['forecast_horizon']
        
        # Get actual values for the forecast period
        forecast_end = forecast_date + timedelta(days=horizon)
        actual_period = actual_data[
            (actual_data[config['date_column']] > forecast_date) & 
            (actual_data[config['date_column']] <= forecast_end)
        ]
        
        if len(actual_period) > 0:
            actual_mean = actual_period[config['target_column']].mean()
            forecast_mean = result['forecast_mean']
            
            error = abs(actual_mean - forecast_mean)
            error_pct = (error / actual_mean * 100) if actual_mean > 0 else 0
            
            validation_results.append({
                'forecast_date': result['forecast_date'],
                'actual_mean': actual_mean,
                'forecast_mean': forecast_mean,
                'absolute_error': error,
                'error_percentage': error_pct
            })
    
    if validation_results:
        validation_df = pd.DataFrame(validation_results)
        
        logger.info("=== BACKFILL VALIDATION RESULTS ===")
        logger.info(f"Total forecasts validated: {len(validation_results)}")
        logger.info(f"Mean absolute error: {validation_df['absolute_error'].mean():.2f}")
        logger.info(f"Mean percentage error: {validation_df['error_percentage'].mean():.1f}%")
        logger.info(f"Best forecast error: {validation_df['error_percentage'].min():.1f}%")
        logger.info(f"Worst forecast error: {validation_df['error_percentage'].max():.1f}%")
        
        return validation_df
    
    return None

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="ForecastEngine Data Backfill")
    
    parser.add_argument('--config', '-c', default='config/simple_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--start-date', '-s', required=True,
                       help='Backfill start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', '-e', required=True,
                       help='Backfill end date (YYYY-MM-DD)')
    parser.add_argument('--window-days', '-w', type=int, default=30,
                       help='Days between backfill points')
    parser.add_argument('--forecast-horizon', '-h', type=int, default=7,
                       help='Forecast horizon for each backfill')
    parser.add_argument('--min-train-samples', type=int, default=50,
                       help='Minimum training samples required')
    parser.add_argument('--output-dir', '-o', default='output/backfill',
                       help='Output directory for results')
    parser.add_argument('--save-individual', action='store_true',
                       help='Save individual forecast files')
    parser.add_argument('--validate', action='store_true',
                       help='Validate results against actual data')
    
    args = parser.parse_args()
    
    logger = setup_logging()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Run backfill
        results = backfill_forecasts(config, args)
        
        # Validate if requested
        if args.validate and results:
            validation_results = validate_backfill_results(config, results)
            
            if validation_results is not None and args.output_dir:
                output_path = Path(args.output_dir)
                validation_results.to_csv(
                    output_path / f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
                    index=False
                )
        
        logger.info("Backfill process completed successfully!")
        
    except Exception as e:
        logger.error(f"Backfill failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()