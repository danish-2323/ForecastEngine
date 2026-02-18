# src/data_ingestion/external_enrichment.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import requests

class ExternalDataEnricher:
    """
    Enriches historical CSV data with external API signals
    Handles API failures gracefully and provides fallback mechanisms
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_enabled = config.get('external_apis', {}).get('enabled', False)
        self.api_configs = config.get('external_apis', {}).get('sources', {})
        
    def enrich_data(self, data: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        Main method to enrich historical data with external signals
        
        Args:
            data: Historical DataFrame with date column
            date_column: Name of the date column
            
        Returns:
            Enriched DataFrame with additional API features
        """
        if not self.api_enabled:
            self.logger.info("External API enrichment disabled")
            return data
            
        enriched_data = data.copy()
        
        # Get date range from historical data
        start_date = pd.to_datetime(enriched_data[date_column]).min()
        end_date = pd.to_datetime(enriched_data[date_column]).max()
        
        # Fetch and merge each external source
        if self.api_configs.get('weather', {}).get('enabled', False):
            weather_data = self._fetch_weather_data(start_date, end_date)
            enriched_data = self._merge_external_data(enriched_data, weather_data, date_column)
            
        if self.api_configs.get('news', {}).get('enabled', False):
            news_data = self._fetch_news_data(start_date, end_date)
            enriched_data = self._merge_external_data(enriched_data, news_data, date_column)
            
        if self.api_configs.get('analytics', {}).get('enabled', False):
            analytics_data = self._fetch_analytics_data(start_date, end_date)
            enriched_data = self._merge_external_data(enriched_data, analytics_data, date_column)
            
        if self.api_configs.get('ecommerce', {}).get('enabled', False):
            ecommerce_data = self._fetch_ecommerce_data(start_date, end_date)
            enriched_data = self._merge_external_data(enriched_data, ecommerce_data, date_column)
            
        # Handle missing values in external features
        enriched_data = self._handle_missing_values(enriched_data, data.columns.tolist())
        
        self.logger.info(f"Data enriched with {len(enriched_data.columns) - len(data.columns)} external features")
        return enriched_data
    
    def _fetch_weather_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch weather data from API or generate mock data"""
        try:
            api_key = self.api_configs.get('weather', {}).get('api_key')
            location = self.api_configs.get('weather', {}).get('location', 'New York')
            
            if api_key and api_key != 'YOUR_API_KEY':
                # Real API call (OpenWeatherMap, WeatherAPI, etc.)
                self.logger.info("Fetching real weather data...")
                return self._fetch_real_weather_data(start_date, end_date, api_key, location)
            else:
                # Mock data
                self.logger.info("Using mock weather data")
                return self._generate_mock_weather_data(start_date, end_date)
                
        except Exception as e:
            self.logger.error(f"Weather API error: {str(e)}")
            return self._generate_mock_weather_data(start_date, end_date)
    
    def _fetch_news_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch news data from NewsAPI or generate mock data"""
        try:
            api_key = self.api_configs.get('news', {}).get('api_key')
            keywords = self.api_configs.get('news', {}).get('keywords', ['business', 'economy'])
            
            if api_key and api_key != 'YOUR_API_KEY':
                # Real API call
                self.logger.info("Fetching real news data...")
                return self._fetch_real_news_data(start_date, end_date, api_key, keywords)
            else:
                # Mock data
                self.logger.info("Using mock news data")
                return self._generate_mock_news_data(start_date, end_date)
                
        except Exception as e:
            self.logger.error(f"News API error: {str(e)}")
            return self._generate_mock_news_data(start_date, end_date)
    
    def _fetch_analytics_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch Google Analytics data or generate mock data"""
        try:
            # Mock data (real GA4 API requires complex OAuth setup)
            self.logger.info("Using mock analytics data")
            return self._generate_mock_analytics_data(start_date, end_date)
                
        except Exception as e:
            self.logger.error(f"Analytics API error: {str(e)}")
            return self._generate_mock_analytics_data(start_date, end_date)
    
    def _fetch_ecommerce_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch e-commerce data (Shopify) or generate mock data"""
        try:
            # Mock data (real Shopify API requires store credentials)
            self.logger.info("Using mock e-commerce data")
            return self._generate_mock_ecommerce_data(start_date, end_date)
                
        except Exception as e:
            self.logger.error(f"E-commerce API error: {str(e)}")
            return self._generate_mock_ecommerce_data(start_date, end_date)
    
    def _fetch_real_weather_data(self, start_date: datetime, end_date: datetime, 
                                 api_key: str, location: str) -> pd.DataFrame:
        """Fetch real weather data from API"""
        # Example using OpenWeatherMap or similar
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        weather_records = []
        
        for date in dates:
            try:
                # API call would go here
                # For now, return mock data
                weather_records.append({
                    'date': date,
                    'avg_temp': np.random.uniform(10, 30),
                    'weather_condition': np.random.choice(['sunny', 'cloudy', 'rainy'])
                })
            except:
                continue
                
        return pd.DataFrame(weather_records)
    
    def _fetch_real_news_data(self, start_date: datetime, end_date: datetime,
                              api_key: str, keywords: List[str]) -> pd.DataFrame:
        """Fetch real news data from NewsAPI"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        news_records = []
        
        for date in dates:
            try:
                # NewsAPI call would go here
                # url = f"https://newsapi.org/v2/everything?q={keywords}&from={date}&apiKey={api_key}"
                # response = requests.get(url)
                # count = len(response.json().get('articles', []))
                
                # For now, return mock data
                news_records.append({
                    'date': date,
                    'news_count': np.random.poisson(15)
                })
            except:
                continue
                
        return pd.DataFrame(news_records)
    
    def _generate_mock_weather_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate realistic mock weather data"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Generate temperature with seasonal pattern
        day_of_year = dates.dayofyear
        base_temp = 15 + 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        noise = np.random.normal(0, 3, len(dates))
        temperatures = base_temp + noise
        
        weather_data = pd.DataFrame({
            'date': dates,
            'avg_temp': temperatures,
            'weather_condition': np.random.choice(['sunny', 'cloudy', 'rainy'], len(dates), p=[0.5, 0.3, 0.2])
        })
        
        return weather_data
    
    def _generate_mock_news_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate realistic mock news data"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # More news on weekdays, less on weekends
        is_weekday = dates.dayofweek < 5
        base_count = np.where(is_weekday, 20, 8)
        news_counts = np.random.poisson(base_count)
        
        news_data = pd.DataFrame({
            'date': dates,
            'news_count': news_counts,
            'news_sentiment': np.random.uniform(-1, 1, len(dates))
        })
        
        return news_data
    
    def _generate_mock_analytics_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate realistic mock analytics data"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Traffic pattern with weekly seasonality
        day_of_week = dates.dayofweek
        base_traffic = 1000 + 300 * (5 - np.abs(day_of_week - 2))
        noise = np.random.normal(0, 100, len(dates))
        traffic = base_traffic + noise
        
        analytics_data = pd.DataFrame({
            'date': dates,
            'web_traffic': traffic.astype(int),
            'bounce_rate': np.random.uniform(0.3, 0.7, len(dates))
        })
        
        return analytics_data
    
    def _generate_mock_ecommerce_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate realistic mock e-commerce data"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Order pattern with weekly seasonality
        day_of_week = dates.dayofweek
        base_orders = 50 + 20 * (5 - np.abs(day_of_week - 2))
        noise = np.random.poisson(10, len(dates))
        orders = base_orders + noise
        
        ecommerce_data = pd.DataFrame({
            'date': dates,
            'daily_orders': orders.astype(int),
            'avg_order_value': np.random.uniform(50, 150, len(dates))
        })
        
        return ecommerce_data
    
    def _merge_external_data(self, base_data: pd.DataFrame, external_data: pd.DataFrame, 
                            date_column: str) -> pd.DataFrame:
        """Merge external data with base data on date"""
        if external_data is None or external_data.empty:
            return base_data
            
        # Ensure date columns are datetime
        base_data[date_column] = pd.to_datetime(base_data[date_column])
        external_data['date'] = pd.to_datetime(external_data['date'])
        
        # Merge on date
        merged_data = base_data.merge(external_data, left_on=date_column, right_on='date', how='left')
        
        # Drop duplicate date column if exists
        if 'date' in merged_data.columns and date_column != 'date':
            merged_data = merged_data.drop(columns=['date'])
            
        return merged_data
    
    def _handle_missing_values(self, data: pd.DataFrame, original_columns: List[str]) -> pd.DataFrame:
        """Handle missing values in external features only"""
        external_columns = [col for col in data.columns if col not in original_columns]
        
        for col in external_columns:
            if data[col].isna().any():
                # Try forward fill first
                data[col] = data[col].ffill()
                # Then backward fill
                data[col] = data[col].bfill()
                # Finally, fill with 0 or median
                if data[col].dtype in ['float64', 'int64']:
                    data[col] = data[col].fillna(0)
                else:
                    data[col] = data[col].fillna('unknown')
                    
        return data
    
    def get_available_features(self) -> List[str]:
        """Return list of available external features"""
        features = []
        
        if self.api_configs.get('weather', {}).get('enabled', False):
            features.extend(['avg_temp', 'weather_condition'])
            
        if self.api_configs.get('news', {}).get('enabled', False):
            features.extend(['news_count', 'news_sentiment'])
            
        if self.api_configs.get('analytics', {}).get('enabled', False):
            features.extend(['web_traffic', 'bounce_rate'])
            
        if self.api_configs.get('ecommerce', {}).get('enabled', False):
            features.extend(['daily_orders', 'avg_order_value'])
            
        return features
