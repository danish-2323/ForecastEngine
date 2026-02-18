# tests/test_api.py

"""
Unit tests for API endpoints
"""

import pytest
import json
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock the ForecastEngine to avoid actual training during tests
class MockForecastEngine:
    def __init__(self, config):
        self.config = config
        self.is_trained = True
        
    def fit(self, *args, **kwargs):
        return self
        
    def predict(self, horizon, confidence_levels=None, include_explanation=True):
        return {
            'forecast': [100.0 + i for i in range(horizon)],
            'prediction_intervals': {
                f'lower_{level}': [95.0 + i for i in range(horizon)]
                for level in (confidence_levels or [0.1, 0.5, 0.9])
            } | {
                f'upper_{level}': [105.0 + i for i in range(horizon)]
                for level in (confidence_levels or [0.1, 0.5, 0.9])
            },
            'confidence_levels': confidence_levels or [0.1, 0.5, 0.9],
            'horizon': horizon,
            'timestamp': '2024-01-01T00:00:00',
            'model_performance': {'mae': 5.0, 'rmse': 7.0},
            'explanations': {
                'business_insights': ['Test insight 1', 'Test insight 2']
            } if include_explanation else None
        }
    
    def run_scenario(self, scenario_config, horizon):
        return {
            'scenario_name': scenario_config.get('name', 'test'),
            'scenario_forecast': [110.0 + i for i in range(horizon)],
            'baseline_forecast': [100.0 + i for i in range(horizon)],
            'impact_analysis': {
                'total_impact': {'percentage': 10.0}
            }
        }
    
    def evaluate_performance(self):
        return {
            'arima': {'mae': 6.0, 'rmse': 8.0},
            'random_forest': {'mae': 4.0, 'rmse': 6.0},
            'ensemble': {'mae': 5.0, 'rmse': 7.0}
        }

# Mock the model manager
class MockModelManager:
    def get_last_training_time(self):
        return '2024-01-01T00:00:00'
    
    def get_current_version(self):
        return 'v20240101_000000'
    
    def check_performance_drift(self):
        return False
    
    def check_data_drift(self):
        return False

@pytest.fixture
def mock_app():
    """Create test app with mocked dependencies"""
    # Import after mocking
    import api.main as api_main
    
    # Replace the global instances with mocks
    api_main.forecast_engine = MockForecastEngine({})
    api_main.model_manager = MockModelManager()
    
    return api_main.app

@pytest.fixture
def client(mock_app):
    """Create test client"""
    return TestClient(mock_app)

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint returns success"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

class TestForecastEndpoint:
    """Test forecast generation endpoint"""
    
    def test_forecast_success(self, client):
        """Test successful forecast generation"""
        request_data = {
            "horizon": 7,
            "confidence_levels": [0.1, 0.5, 0.9],
            "include_explanation": True
        }
        
        response = client.post("/forecast", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "forecast" in data
        assert "prediction_intervals" in data
        assert "confidence_levels" in data
        assert "horizon" in data
        assert "explanations" in data
        
        assert len(data["forecast"]) == 7
        assert data["horizon"] == 7
        assert data["confidence_levels"] == [0.1, 0.5, 0.9]
    
    def test_forecast_without_explanation(self, client):
        """Test forecast without explanations"""
        request_data = {
            "horizon": 5,
            "include_explanation": False
        }
        
        response = client.post("/forecast", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["forecast"]) == 5
        # Explanations might be None or not included
    
    def test_forecast_invalid_horizon(self, client):
        """Test forecast with invalid horizon"""
        request_data = {
            "horizon": 0,  # Invalid
            "confidence_levels": [0.1, 0.5, 0.9]
        }
        
        response = client.post("/forecast", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_forecast_large_horizon(self, client):
        """Test forecast with maximum horizon"""
        request_data = {
            "horizon": 365,  # Maximum allowed
            "confidence_levels": [0.5]
        }
        
        response = client.post("/forecast", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["forecast"]) == 365

class TestScenarioEndpoint:
    """Test scenario analysis endpoint"""
    
    def test_scenario_success(self, client):
        """Test successful scenario analysis"""
        request_data = {
            "scenario_name": "price_increase",
            "scenario_config": {
                "price_change": 0.1,
                "price_elasticity": -0.5
            },
            "horizon": 14,
            "baseline_comparison": True
        }
        
        response = client.post("/scenario", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "scenario_name" in data
        assert "scenario_forecast" in data
        assert "baseline_forecast" in data
        assert "impact_analysis" in data
        
        assert data["scenario_name"] == "price_increase"
        assert len(data["scenario_forecast"]) == 14
        assert len(data["baseline_forecast"]) == 14
    
    def test_scenario_without_baseline(self, client):
        """Test scenario without baseline comparison"""
        request_data = {
            "scenario_name": "demand_shock",
            "scenario_config": {"demand_multiplier": 1.2},
            "horizon": 7,
            "baseline_comparison": False
        }
        
        response = client.post("/scenario", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["scenario_name"] == "demand_shock"

class TestModelEndpoints:
    """Test model management endpoints"""
    
    def test_model_performance(self, client):
        """Test model performance endpoint"""
        response = client.get("/model/performance")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "model_metrics" in data
        assert "ensemble_performance" in data
        assert "last_updated" in data
        assert "training_status" in data
    
    def test_model_status(self, client):
        """Test model status endpoint"""
        response = client.get("/model/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "is_trained" in data
        assert "timestamp" in data
        # Other fields might be None in mock
    
    def test_train_model(self, client):
        """Test model training endpoint"""
        request_data = {
            "target_column": "value",
            "date_column": "date",
            "external_features": ["price", "promotion"],
            "retrain": False
        }
        
        response = client.post("/train", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "training"

class TestDataEndpoints:
    """Test data quality endpoints"""
    
    def test_data_quality(self, client):
        """Test data quality endpoint"""
        response = client.get("/data/quality")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "overall_score" in data
        assert "timestamp" in data
        
        # Check score is in valid range
        assert 0 <= data["overall_score"] <= 1

class TestExplanationEndpoints:
    """Test explanation endpoints"""
    
    def test_forecast_explanation(self, client):
        """Test forecast explanation endpoint"""
        forecast_id = "test_forecast_123"
        
        response = client.get(f"/explain/forecast/{forecast_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "forecast_id" in data
        assert "key_drivers" in data
        assert "business_insights" in data
        assert "confidence_factors" in data
        
        assert data["forecast_id"] == forecast_id

class TestErrorHandling:
    """Test API error handling"""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/forecast",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        request_data = {}  # Missing required horizon
        
        response = client.post("/forecast", json=request_data)
        
        assert response.status_code == 422
    
    def test_not_found_endpoint(self, client):
        """Test 404 for non-existent endpoint"""
        response = client.get("/nonexistent")
        
        assert response.status_code == 404

class TestAuthentication:
    """Test authentication (if implemented)"""
    
    def test_unauthenticated_request(self, client):
        """Test request without authentication"""
        # Note: This test assumes authentication is implemented
        # If not implemented, this test might need to be skipped
        
        # For now, just test that endpoints are accessible
        # In production, you would test with missing/invalid tokens
        response = client.get("/health")
        assert response.status_code == 200