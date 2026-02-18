# tests/test_external_enrichment.py

import pytest
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_ingestion.external_enrichment import ExternalDataEnricher
from datetime import datetime, timedelta

@pytest.fixture
def enricher_config():
    """Config with all APIs enabled"""
    return {
        'external_apis': {
            'enabled': True,
            'sources': {
                'weather': {'enabled': True},
                'news': {'enabled': True},
                'analytics': {'enabled': True},
                'ecommerce': {'enabled': True}
            }
        }
    }

@pytest.fixture
def sample_data():
    """Sample historical data"""
    dates = pd.date_range(start='2023-01-01', end='2023-01-31', freq='D')
    return pd.DataFrame({
        'date': dates,
        'value': range(100, 100 + len(dates))
    })

def test_enricher_initialization(enricher_config):
    """Test enricher initializes correctly"""
    enricher = ExternalDataEnricher(enricher_config)
    assert enricher.api_enabled == True
    assert 'weather' in enricher.api_configs

def test_enricher_disabled():
    """Test enricher with APIs disabled"""
    config = {'external_apis': {'enabled': False}}
    enricher = ExternalDataEnricher(config)
    
    data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=10),
        'value': range(10)
    })
    
    enriched = enricher.enrich_data(data, 'date')
    assert len(enriched.columns) == len(data.columns)  # No new columns

def test_weather_data_generation(enricher_config):
    """Test weather data generation"""
    enricher = ExternalDataEnricher(enricher_config)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    
    weather_data = enricher._generate_mock_weather_data(start_date, end_date)
    
    assert len(weather_data) == 31
    assert 'avg_temp' in weather_data.columns
    assert 'weather_condition' in weather_data.columns
    assert weather_data['avg_temp'].notna().all()

def test_news_data_generation(enricher_config):
    """Test news data generation"""
    enricher = ExternalDataEnricher(enricher_config)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    
    news_data = enricher._generate_mock_news_data(start_date, end_date)
    
    assert len(news_data) == 31
    assert 'news_count' in news_data.columns
    assert 'news_sentiment' in news_data.columns
    assert (news_data['news_count'] >= 0).all()

def test_analytics_data_generation(enricher_config):
    """Test analytics data generation"""
    enricher = ExternalDataEnricher(enricher_config)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    
    analytics_data = enricher._generate_mock_analytics_data(start_date, end_date)
    
    assert len(analytics_data) == 31
    assert 'web_traffic' in analytics_data.columns
    assert 'bounce_rate' in analytics_data.columns
    assert (analytics_data['web_traffic'] > 0).all()

def test_ecommerce_data_generation(enricher_config):
    """Test e-commerce data generation"""
    enricher = ExternalDataEnricher(enricher_config)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    
    ecommerce_data = enricher._generate_mock_ecommerce_data(start_date, end_date)
    
    assert len(ecommerce_data) == 31
    assert 'daily_orders' in ecommerce_data.columns
    assert 'avg_order_value' in ecommerce_data.columns
    assert (ecommerce_data['daily_orders'] > 0).all()

def test_data_merging(enricher_config, sample_data):
    """Test merging external data with base data"""
    enricher = ExternalDataEnricher(enricher_config)
    
    external_data = pd.DataFrame({
        'date': sample_data['date'],
        'external_feature': range(len(sample_data))
    })
    
    merged = enricher._merge_external_data(sample_data, external_data, 'date')
    
    assert 'external_feature' in merged.columns
    assert len(merged) == len(sample_data)

def test_missing_value_handling(enricher_config):
    """Test handling of missing values in external features"""
    enricher = ExternalDataEnricher(enricher_config)
    
    data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=10),
        'value': range(10),
        'external_feature': [1, 2, None, 4, None, 6, 7, 8, 9, 10]
    })
    
    original_cols = ['date', 'value']
    handled = enricher._handle_missing_values(data, original_cols)
    
    assert handled['external_feature'].notna().all()

def test_full_enrichment(enricher_config, sample_data):
    """Test full enrichment pipeline"""
    enricher = ExternalDataEnricher(enricher_config)
    
    enriched = enricher.enrich_data(sample_data, 'date')
    
    # Should have more columns than original
    assert len(enriched.columns) > len(sample_data.columns)
    
    # Should have external features
    external_features = enricher.get_available_features()
    assert len(external_features) > 0
    
    # Check specific features exist
    assert any('temp' in col or 'news' in col or 'traffic' in col or 'order' in col 
               for col in enriched.columns)

def test_get_available_features(enricher_config):
    """Test getting list of available features"""
    enricher = ExternalDataEnricher(enricher_config)
    features = enricher.get_available_features()
    
    assert 'avg_temp' in features
    assert 'news_count' in features
    assert 'web_traffic' in features
    assert 'daily_orders' in features

def test_enrichment_preserves_original_data(enricher_config, sample_data):
    """Test that enrichment doesn't modify original columns"""
    enricher = ExternalDataEnricher(enricher_config)
    
    original_values = sample_data['value'].copy()
    enriched = enricher.enrich_data(sample_data, 'date')
    
    # Original values should be unchanged
    assert (enriched['value'] == original_values).all()

def test_enrichment_with_partial_apis():
    """Test enrichment with only some APIs enabled"""
    config = {
        'external_apis': {
            'enabled': True,
            'sources': {
                'weather': {'enabled': True},
                'news': {'enabled': False},
                'analytics': {'enabled': False},
                'ecommerce': {'enabled': False}
            }
        }
    }
    
    enricher = ExternalDataEnricher(config)
    features = enricher.get_available_features()
    
    assert 'avg_temp' in features
    assert 'news_count' not in features
    assert 'web_traffic' not in features

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
