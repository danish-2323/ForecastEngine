# scripts/retrain_models.py

"""
ForecastEngine Model Retraining Script
CLI script to trigger model retraining based on performance drift
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
from mlops.model_manager import ModelManager

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

def check_retraining_triggers(config, args):
    """Check if retraining is needed"""
    logger = logging.getLogger(__name__)
    
    logger.info("Checking retraining triggers...")
    
    # Initialize model manager
    model_manager = ModelManager(config)
    
    # Initialize engine for current performance check
    engine = ForecastEngine(config)
    
    try:
        # Try to load existing models
        models, ensemble, metadata = model_manager.load_model()
        logger.info(f"Loaded existing models from version: {model_manager.get_current_version()}")
        
        # Set loaded models in engine
        engine.models = models
        engine.ensemble_manager = ensemble
        engine.is_trained = True
        
    except Exception as e:
        logger.warning(f"Could not load existing models: {e}")
        logger.info("Will perform fresh training...")
        return True, "no_existing_models"
    
    # Evaluate current performance
    try:
        current_performance = engine.evaluate_performance()
        current_metrics = current_performance.get('ensemble', {})
        
        if not current_metrics:
            logger.warning("Could not evaluate current performance")
            return True, "evaluation_failed"
        
        logger.info(f"Current performance: {current_metrics}")
        
    except Exception as e:
        logger.error(f"Performance evaluation failed: {e}")
        return True, "evaluation_error"
    
    # Load latest data for drift detection
    latest_data = engine.data_connector.load_latest_data()
    
    # Check retraining triggers
    triggers = model_manager.should_retrain(current_metrics, latest_data)
    
    logger.info("=== RETRAINING TRIGGER ANALYSIS ===")
    for trigger_name, triggered in triggers.items():
        status = "TRIGGERED" if triggered else "OK"
        logger.info(f"{trigger_name}: {status}")
    
    # Determine if retraining is needed
    needs_retraining = any(triggers.values()) or args.force
    
    if needs_retraining:
        triggered_reasons = [name for name, triggered in triggers.items() if triggered]
        if args.force:
            triggered_reasons.append("forced")
        
        reason = ", ".join(triggered_reasons)
        logger.info(f"Retraining REQUIRED: {reason}")
        return True, reason
    else:
        logger.info("Retraining NOT REQUIRED - all triggers OK")
        return False, "no_triggers"

def perform_retraining(config, args, reason):
    """Perform model retraining"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting model retraining (reason: {reason})...")
    
    # Initialize fresh engine
    engine = ForecastEngine(config)
    
    # Train models
    logger.info("Training new models...")
    engine.fit(
        target_column=config.get('target_column', 'value'),
        date_column=config.get('date_column', 'date')
    )
    
    # Evaluate new models
    logger.info("Evaluating new models...")
    new_performance = engine.evaluate_performance()
    
    # Save new models
    model_manager = ModelManager(config)
    
    metadata = {
        'retrain_reason': reason,
        'retrain_timestamp': datetime.now().isoformat(),
        'performance_metrics': new_performance,
        'config': config
    }
    
    new_version = model_manager.save_model(
        models=engine.models,
        ensemble=engine.ensemble_manager,
        metadata=metadata
    )
    
    logger.info(f"New models saved as version: {new_version}")
    
    # Performance comparison
    logger.info("=== RETRAINING RESULTS ===")
    ensemble_metrics = new_performance.get('ensemble', {})
    
    for metric, value in ensemble_metrics.items():
        logger.info(f"New {metric}: {value:.3f}")
    
    # Generate validation forecast
    if args.validate:
        logger.info("Generating validation forecast...")
        
        validation_forecast = engine.predict(
            horizon=args.validation_horizon,
            confidence_levels=[0.1, 0.5, 0.9],
            include_explanation=True
        )
        
        logger.info(f"Validation forecast generated for {args.validation_horizon} days")
        logger.info(f"Mean forecast value: {sum(validation_forecast['forecast']) / len(validation_forecast['forecast']):.2f}")
        
        # Save validation results
        if args.output_dir:
            output_path = Path(args.output_dir)
            output_path.mkdir(exist_ok=True)
            
            import json
            with open(output_path / f"retrain_validation_{new_version}.json", 'w') as f:
                json.dump(validation_forecast, f, indent=2, default=str)
            
            logger.info(f"Validation results saved to {output_path}")
    
    return new_version, new_performance

def cleanup_old_models(config, args):
    """Cleanup old model versions"""
    logger = logging.getLogger(__name__)
    
    if not args.cleanup_old:
        return
    
    logger.info("Cleaning up old model versions...")
    
    model_manager = ModelManager(config)
    registry_path = model_manager.model_registry_path
    
    # Get all version directories
    version_dirs = [d for d in registry_path.iterdir() 
                   if d.is_dir() and d.name.startswith('v')]
    
    if len(version_dirs) <= args.keep_versions:
        logger.info(f"Only {len(version_dirs)} versions found, no cleanup needed")
        return
    
    # Sort by creation time and keep only recent versions
    version_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    versions_to_delete = version_dirs[args.keep_versions:]
    
    for version_dir in versions_to_delete:
        try:
            import shutil
            shutil.rmtree(version_dir)
            logger.info(f"Deleted old version: {version_dir.name}")
        except Exception as e:
            logger.warning(f"Failed to delete {version_dir.name}: {e}")
    
    logger.info(f"Cleanup completed: kept {args.keep_versions} versions")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="ForecastEngine Model Retraining")
    
    parser.add_argument('--config', '-c', default='config/simple_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force retraining regardless of triggers')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check triggers, do not retrain')
    parser.add_argument('--validate', action='store_true',
                       help='Generate validation forecast after retraining')
    parser.add_argument('--validation-horizon', type=int, default=14,
                       help='Horizon for validation forecast')
    parser.add_argument('--output-dir', '-o', default='output/retrain',
                       help='Output directory for results')
    parser.add_argument('--cleanup-old', action='store_true',
                       help='Cleanup old model versions')
    parser.add_argument('--keep-versions', type=int, default=5,
                       help='Number of model versions to keep')
    
    args = parser.parse_args()
    
    logger = setup_logging()
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Check retraining triggers
        needs_retraining, reason = check_retraining_triggers(config, args)
        
        if args.check_only:
            if needs_retraining:
                logger.info(f"RESULT: Retraining needed ({reason})")
                sys.exit(1)  # Exit code 1 indicates retraining needed
            else:
                logger.info("RESULT: No retraining needed")
                sys.exit(0)
        
        # Perform retraining if needed
        if needs_retraining:
            new_version, performance = perform_retraining(config, args, reason)
            
            # Cleanup old models if requested
            cleanup_old_models(config, args)
            
            logger.info(f"Retraining completed successfully! New version: {new_version}")
        else:
            logger.info("No retraining performed - triggers not met")
        
    except Exception as e:
        logger.error(f"Retraining script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()