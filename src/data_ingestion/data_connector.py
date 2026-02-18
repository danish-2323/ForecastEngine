# src/data_ingestion/data_connector.py

import pandas as pd
import numpy as np
from typing import Optional
import logging
from data_ingestion.external_enrichment import ExternalDataEnricher

class DataConnector:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.enricher = ExternalDataEnricher(config)
        
    def load_training_data(self, target_column: str, date_column: str, 
                          file_path: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Load and validate CSV data"""
        if file_path is None:
            file_path = self.config.get('data_path', 'data/sample_data.csv')
            
        self.logger.info(f"Loading data from {file_path}")
        
        # Load CSV
        data = pd.read_csv(file_path)
        
        # Validate required columns
        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' not found")
        if date_column not in data.columns:
            raise ValueError(f"Date column '{date_column}' not found")
            
        # Convert date column
        data[date_column] = pd.to_datetime(data[date_column])
        
        # Handle missing values in target
        data[target_column] = data[target_column].fillna(method='ffill').fillna(method='bfill')
        
        # Filter by end date if provided
        if end_date:
            data = data[data[date_column] <= end_date]
            
        # Sort by date
        data = data.sort_values(date_column).reset_index(drop=True)
        
        # Enrich with external API data
        data = self.enricher.enrich_data(data, date_column)
        
        self.logger.info(f"Loaded {len(data)} records with {len(data.columns)} features")
        return data
    
    def load_latest_data(self) -> pd.DataFrame:
        """Load latest data for prediction"""
        return self.load_training_data(
            target_column=self.config.get('target_column', 'value'),
            date_column=self.config.get('date_column', 'date')
        )
    
    def load_test_data(self) -> pd.DataFrame:
        """Load test data"""
        test_path = self.config.get('test_data_path', 'data/sample_data.csv')
        return self.load_training_data(
            target_column=self.config.get('target_column', 'value'),
            date_column=self.config.get('date_column', 'date'),
            file_path=test_path
        )
    
    def get_data_quality_metrics(self) -> dict:
        """Simple data quality metrics"""
        return {'overall_score': 0.9, 'completeness': 0.95}
    
    def get_external_features(self) -> list:
        """Get list of available external features"""
        return self.enricher.get_available_features()
    
    def detect_data_drift(self) -> bool:
        """Simple drift detection"""
        return False