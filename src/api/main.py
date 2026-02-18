"""
ForecastEngine REST API
Provides enterprise-grade API endpoints for forecasting operations
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime, timedelta
import logging
import asyncio
import json

from ..forecast_engine import ForecastEngine
from ..mlops.model_manager import ModelManager
from ..scenarios.scenario_engine import ScenarioEngine

# Initialize FastAPI app
app = FastAPI(
    title="ForecastEngine API",
    description="Enterprise AI-Powered Forecasting Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Global instances (in production, use dependency injection)
forecast_engine = None
model_manager = None
scenario_engine = None

# Pydantic models for request/response
class ForecastRequest(BaseModel):
    horizon: int = Field(..., ge=1, le=365, description="Forecast horizon in periods")
    confidence_levels: List[float] = Field(default=[0.1, 0.5, 0.9], description="Confidence levels for prediction intervals")
    include_explanation: bool = Field(default=True, description="Include AI explanations")
    target_column: Optional[str] = Field(default=None, description="Target variable name")

class ForecastResponse(BaseModel):
    forecast: List[float]
    prediction_intervals: Dict[str, List[float]]
    confidence_levels: List[float]
    horizon: int
    timestamp: str
    model_performance: Dict[str, float]
    explanations: Optional[Dict[str, Any]]

class ScenarioRequest(BaseModel):
    scenario_name: str = Field(..., description="Name of the scenario")
    scenario_config: Dict[str, Any] = Field(..., description="Scenario configuration")
    horizon: int = Field(..., ge=1, le=365, description="Forecast horizon")
    baseline_comparison: bool = Field(default=True, description="Include baseline comparison")

class ScenarioResponse(BaseModel):
    scenario_name: str
    scenario_forecast: List[float]
    baseline_forecast: List[float]
    impact_analysis: Dict[str, Any]
    confidence_intervals: Dict[str, List[float]]
    timestamp: str

class TrainingRequest(BaseModel):
    target_column: str = Field(..., description="Target variable to forecast")
    date_column: str = Field(..., description="Date column name")
    external_features: Optional[List[str]] = Field(default=None, description="External feature columns")
    train_end_date: Optional[str] = Field(default=None, description="End date for training")
    retrain: bool = Field(default=False, description="Force retrain existing models")

class ModelPerformanceResponse(BaseModel):
    model_metrics: Dict[str, Dict[str, float]]
    ensemble_performance: Dict[str, float]
    last_updated: str
    training_status: str

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validate API token (implement your authentication logic)
    """
    # In production, validate the token against your auth system
    token = credentials.credentials
    if not token or token != "your-api-token":  # Replace with real validation
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return {"user_id": "authenticated_user"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize ForecastEngine components on startup"""
    global forecast_engine, model_manager, scenario_engine
    
    logger.info("Starting ForecastEngine API...")
    
    # Load configuration
    config = {
        "data_sources": {"type": "database", "connection": "postgresql://..."},
        "models": {"ensemble_method": "weighted_average"},
        "uncertainty": {"method": "quantile_regression"},
        "explainability": {"method": "shap"}
    }
    
    # Initialize components
    forecast_engine = ForecastEngine(config)
    model_manager = ModelManager(config)
    scenario_engine = ScenarioEngine(config)
    
    logger.info("ForecastEngine API started successfully")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Forecast endpoints
@app.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(
    request: ForecastRequest,
    user: dict = Depends(get_current_user)
):
    """
    Generate AI-powered forecasts with uncertainty intervals
    """
    try:
        logger.info(f"Generating forecast for horizon: {request.horizon}")
        
        if not forecast_engine or not forecast_engine.is_trained:
            raise HTTPException(
                status_code=400, 
                detail="Model not trained. Please train the model first."
            )
        
        # Generate forecast
        result = forecast_engine.predict(
            horizon=request.horizon,
            confidence_levels=request.confidence_levels,
            include_explanation=request.include_explanation
        )
        
        return ForecastResponse(**result)
        
    except Exception as e:
        logger.error(f"Forecast generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

@app.post("/scenario", response_model=ScenarioResponse)
async def run_scenario_analysis(
    request: ScenarioRequest,
    user: dict = Depends(get_current_user)
):
    """
    Run what-if scenario analysis
    """
    try:
        logger.info(f"Running scenario analysis: {request.scenario_name}")
        
        if not forecast_engine or not forecast_engine.is_trained:
            raise HTTPException(
                status_code=400,
                detail="Model not trained. Please train the model first."
            )
        
        # Run scenario
        result = forecast_engine.run_scenario(
            scenario_config=request.scenario_config,
            horizon=request.horizon
        )
        
        # Add baseline comparison if requested
        if request.baseline_comparison:
            baseline = forecast_engine.predict(horizon=request.horizon)
            result['baseline_forecast'] = baseline['forecast']
        
        return ScenarioResponse(
            scenario_name=request.scenario_name,
            scenario_forecast=result['scenario_forecast'],
            baseline_forecast=result.get('baseline_forecast', []),
            impact_analysis=result.get('impact_analysis', {}),
            confidence_intervals=result.get('confidence_intervals', {}),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Scenario analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scenario analysis failed: {str(e)}")

# Model management endpoints
@app.post("/train")
async def train_model(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """
    Train or retrain forecasting models
    """
    try:
        logger.info("Starting model training...")
        
        # Add training task to background
        background_tasks.add_task(
            _train_model_background,
            request.target_column,
            request.date_column,
            request.external_features,
            request.train_end_date,
            request.retrain
        )
        
        return {
            "message": "Model training started",
            "status": "training",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Training initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.get("/model/performance", response_model=ModelPerformanceResponse)
async def get_model_performance(user: dict = Depends(get_current_user)):
    """
    Get current model performance metrics
    """
    try:
        if not forecast_engine:
            raise HTTPException(status_code=400, detail="ForecastEngine not initialized")
        
        # Get performance metrics
        performance = forecast_engine.evaluate_performance()
        
        return ModelPerformanceResponse(
            model_metrics=performance.get('individual_models', {}),
            ensemble_performance=performance.get('ensemble', {}),
            last_updated=datetime.now().isoformat(),
            training_status="completed" if forecast_engine.is_trained else "not_trained"
        )
        
    except Exception as e:
        logger.error(f"Performance retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Performance retrieval failed: {str(e)}")

@app.get("/model/status")
async def get_model_status(user: dict = Depends(get_current_user)):
    """
    Get current model training and operational status
    """
    try:
        status = {
            "is_trained": forecast_engine.is_trained if forecast_engine else False,
            "last_training": model_manager.get_last_training_time() if model_manager else None,
            "model_version": model_manager.get_current_version() if model_manager else None,
            "performance_drift": model_manager.check_performance_drift() if model_manager else None,
            "data_drift": model_manager.check_data_drift() if model_manager else None,
            "timestamp": datetime.now().isoformat()
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Status retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

# Data endpoints
@app.get("/data/quality")
async def get_data_quality(user: dict = Depends(get_current_user)):
    """
    Get data quality metrics and issues
    """
    try:
        if not forecast_engine:
            raise HTTPException(status_code=400, detail="ForecastEngine not initialized")
        
        # Get data quality metrics
        quality_metrics = forecast_engine.data_connector.get_data_quality_metrics()
        
        return {
            "overall_score": quality_metrics.get('overall_score', 0),
            "completeness": quality_metrics.get('completeness', 0),
            "consistency": quality_metrics.get('consistency', 0),
            "timeliness": quality_metrics.get('timeliness', 0),
            "issues": quality_metrics.get('issues', []),
            "recommendations": quality_metrics.get('recommendations', []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Data quality check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data quality check failed: {str(e)}")

# Explanation endpoints
@app.get("/explain/forecast/{forecast_id}")
async def get_forecast_explanation(
    forecast_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get detailed explanation for a specific forecast
    """
    try:
        # In production, retrieve forecast by ID from database
        # For now, return sample explanation
        explanation = {
            "forecast_id": forecast_id,
            "key_drivers": [
                {"feature": "seasonality", "impact": 0.35, "direction": "positive"},
                {"feature": "trend", "impact": 0.28, "direction": "positive"},
                {"feature": "external_factors", "impact": 0.15, "direction": "negative"}
            ],
            "business_insights": [
                "Holiday season is driving increased demand",
                "Long-term growth trend continues",
                "Economic uncertainty creating some headwinds"
            ],
            "confidence_factors": {
                "model_agreement": 0.85,
                "data_quality": 0.92,
                "historical_accuracy": 0.88
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return explanation
        
    except Exception as e:
        logger.error(f"Explanation retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Explanation retrieval failed: {str(e)}")

# Background task functions
async def _train_model_background(
    target_column: str,
    date_column: str,
    external_features: Optional[List[str]],
    train_end_date: Optional[str],
    retrain: bool
):
    """Background task for model training"""
    try:
        global forecast_engine
        
        if retrain or not forecast_engine.is_trained:
            forecast_engine.fit(
                target_column=target_column,
                date_column=date_column,
                external_features=external_features,
                train_end_date=train_end_date
            )
            logger.info("Model training completed successfully")
        else:
            logger.info("Model already trained, skipping training")
            
    except Exception as e:
        logger.error(f"Background training failed: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "error": exc.detail,
        "status_code": exc.status_code,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)