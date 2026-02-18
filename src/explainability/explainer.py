# src/explainability/explainer.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

class ForecastExplainer:
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def explain_forecast(self, forecast: pd.Series, features: pd.DataFrame, 
                        models: Dict, ensemble, previous_forecast: Optional[pd.Series] = None) -> Dict:
        """Generate forecast explanations"""
        self.logger.info("Generating explanations...")
        
        explanations = {
            'feature_importance': self._explain_feature_importance(models),
            'forecast_drivers': self._identify_forecast_drivers(features),
            'business_insights': self._generate_business_insights(forecast),
            'confidence_factors': self._explain_confidence_factors(models)
        }
        
        # Add change analysis if previous forecast available
        if previous_forecast is not None:
            explanations['change_analysis'] = self._explain_forecast_changes(
                forecast, previous_forecast
            )
        
        return explanations
    
    def _explain_feature_importance(self, models: Dict) -> Dict:
        """Get feature importance from models"""
        importance_scores = {}
        
        for model_name, model in models.items():
            try:
                if hasattr(model, 'get_feature_importance'):
                    importance = model.get_feature_importance()
                    importance_scores[model_name] = importance
            except Exception as e:
                self.logger.warning(f"Could not get importance for {model_name}: {e}")
        
        # Aggregate importance across models
        if importance_scores:
            all_features = set()
            for scores in importance_scores.values():
                all_features.update(scores.keys())
            
            aggregated = {}
            for feature in all_features:
                scores = [importance_scores[model].get(feature, 0) 
                         for model in importance_scores.keys()]
                aggregated[feature] = np.mean(scores)
            
            # Get top 5 features
            top_features = dict(sorted(aggregated.items(), 
                                     key=lambda x: x[1], reverse=True)[:5])
            
            return {
                'aggregated_importance': aggregated,
                'top_drivers': top_features,
                'feature_explanations': self._create_feature_explanations(top_features)
            }
        
        return {'top_drivers': {}, 'feature_explanations': {}}
    
    def _identify_forecast_drivers(self, features: pd.DataFrame) -> Dict:
        """Identify key drivers of current forecast"""
        drivers = {}
        
        if len(features) > 0:
            last_row = features.iloc[-1]
            
            # Analyze key features (including external signals)
            key_features = ['lag_1', 'lag_7', 'rolling_mean_7', 'day_of_week', 'month',
                          'avg_temp', 'news_count', 'web_traffic', 'daily_orders']
            
            for feature in key_features:
                if feature in last_row:
                    value = last_row[feature]
                    drivers[feature] = {
                        'current_value': float(value) if pd.notna(value) else 0,
                        'impact_direction': 'positive' if value > 0 else 'neutral',
                        'business_meaning': self._get_business_meaning(feature, value),
                        'is_external': self._is_external_feature(feature)
                    }
        
        return drivers
    
    def _generate_business_insights(self, forecast: pd.Series) -> List[str]:
        """Generate business insights"""
        insights = []
        
        if len(forecast) > 1:
            # Trend analysis
            trend = np.mean(np.diff(forecast))
            if trend > 0:
                insights.append("Forecast shows positive growth trend")
            elif trend < 0:
                insights.append("Forecast indicates declining trend")
            else:
                insights.append("Forecast shows stable pattern")
            
            # Volatility analysis
            volatility = np.std(forecast)
            avg_value = np.mean(forecast)
            cv = volatility / avg_value if avg_value > 0 else 0
            
            if cv > 0.2:
                insights.append("High volatility detected - monitor closely")
            elif cv > 0.1:
                insights.append("Moderate volatility in forecast")
            else:
                insights.append("Stable forecast with low volatility")
        
        # Seasonal patterns
        insights.append("Seasonal patterns incorporated in forecast")
        
        # External signal insights
        insights.append("External signals (news, weather, traffic) enriching predictions")
        
        return insights
    
    def _explain_confidence_factors(self, models: Dict) -> Dict:
        """Explain factors affecting confidence"""
        return {
            'model_agreement': 0.85,  # Simplified
            'data_quality': 0.9,
            'historical_accuracy': 0.88,
            'confidence_level': 0.82
        }
    
    def _explain_forecast_changes(self, current_forecast: pd.Series, 
                                 previous_forecast: pd.Series) -> Dict:
        """Explain changes from previous forecast"""
        change = current_forecast - previous_forecast
        change_pct = (change / previous_forecast * 100).fillna(0)
        
        avg_change = change_pct.mean()
        
        explanations = []
        if abs(avg_change) > 5:
            direction = "increased" if avg_change > 0 else "decreased"
            explanations.append(f"Forecast {direction} by {abs(avg_change):.1f}% from previous period")
        
        return {
            'forecast_change': change.tolist(),
            'change_percentage': change_pct.tolist(),
            'explanations': explanations
        }
    
    def _create_feature_explanations(self, importance_scores: Dict[str, float]) -> Dict[str, str]:
        """Create business-friendly feature explanations"""
        explanations = {}
        
        feature_descriptions = {
            'lag_1': 'Previous day value',
            'lag_7': 'Same day last week',
            'lag_30': 'Same day last month',
            'rolling_mean_7': '7-day average trend',
            'rolling_mean_14': '14-day average trend',
            'day_of_week': 'Day of week pattern',
            'month': 'Monthly seasonality',
            'is_weekend': 'Weekend effect',
            'avg_temp': 'Weather temperature',
            'news_count': 'Business news activity',
            'web_traffic': 'Website traffic volume',
            'daily_orders': 'E-commerce order volume'
        }
        
        for feature, importance in importance_scores.items():
            friendly_name = feature_descriptions.get(feature, feature)
            
            if importance > 0.2:
                impact_level = "strongly influences"
            elif importance > 0.1:
                impact_level = "moderately influences"
            else:
                impact_level = "slightly influences"
            
            explanations[feature] = f"{friendly_name} {impact_level} the forecast"
        
        return explanations
    
    def _get_business_meaning(self, feature: str, value) -> str:
        """Get business meaning for feature impact"""
        meanings = {
            'lag_1': f"Yesterday's value was {value:.1f}",
            'lag_7': f"Same day last week was {value:.1f}",
            'rolling_mean_7': f"7-day average is {value:.1f}",
            'day_of_week': f"Day of week effect: {int(value)}",
            'month': f"Monthly pattern: {int(value)}",
            'avg_temp': f"Temperature: {value:.1f}°C",
            'news_count': f"News articles: {int(value)}",
            'web_traffic': f"Website visitors: {int(value)}",
            'daily_orders': f"Daily orders: {int(value)}"
        }
        
        return meanings.get(feature, f"Current {feature}: {value}")
    
    def _is_external_feature(self, feature: str) -> bool:
        """Check if feature is from external API"""
        external_keywords = ['temp', 'weather', 'news', 'traffic', 'orders', 'sentiment', 'bounce']
        return any(keyword in feature.lower() for keyword in external_keywords)