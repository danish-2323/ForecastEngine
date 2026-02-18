# ForecastEngine - Quick Start Guide

## 🚀 Running the Complete System

### Prerequisites
```bash
pip install pandas numpy scikit-learn plotly streamlit fastapi uvicorn pyyaml
```

### 1. Run Core Forecasting Engine
```bash
python run_forecast.py
```
This will:
- Load sample data
- Train multiple models (ARIMA, Random Forest, Linear)
- Create ensemble predictions
- Generate uncertainty intervals
- Provide AI explanations
- Run scenario analysis

### 2. Launch Interactive Dashboard
```bash
python run_dashboard.py
```
- Opens Streamlit dashboard at http://localhost:8501
- Interactive forecasting interface
- Scenario planning tools
- Model performance monitoring

### 3. Start REST API Server
```bash
python run_api.py
```
- FastAPI server at http://localhost:8000
- API documentation at http://localhost:8000/docs
- Enterprise-ready endpoints

## 📁 Project Structure

```
FORECASTENGINE/
├── src/
│   ├── forecast_engine.py      # Main orchestration
│   ├── data_ingestion/         # Data loading & validation
│   ├── feature_engineering/    # Time-series features
│   ├── models/                 # ML models (ARIMA, RF, Linear)
│   ├── ensemble/               # Model combination
│   ├── uncertainty/            # Prediction intervals
│   ├── explainability/         # AI explanations
│   ├── scenarios/              # What-if analysis
│   ├── evaluation/             # Performance metrics
│   ├── mlops/                  # Model versioning
│   ├── api/                    # REST API
│   └── dashboard/              # Streamlit UI
├── data/
│   └── sample_data.csv         # Sample time-series data
├── config/
│   └── simple_config.yaml     # Configuration
├── run_forecast.py             # Core engine runner
├── run_dashboard.py            # Dashboard runner
└── run_api.py                  # API runner
```

## 🎯 Key Features Implemented

### ✅ Data Ingestion
- CSV data loading with validation
- Missing value handling
- Schema validation

### ✅ Feature Engineering
- Lag features (1, 2, 3, 7, 14, 30 periods)
- Rolling window statistics (mean, std)
- Date-based features (day of week, month, etc.)
- Seasonality indicators

### ✅ Models
- **ARIMA**: Statistical time-series model
- **Random Forest**: Machine learning ensemble
- **Linear Regression**: Simple baseline model

### ✅ Ensemble Intelligence
- Weighted averaging based on performance
- Automatic model selection
- Graceful failure handling

### ✅ Uncertainty Quantification
- Prediction intervals at multiple confidence levels
- Residual-based uncertainty estimation
- Risk assessment metrics

### ✅ Explainable AI
- Feature importance analysis
- Business-friendly explanations
- Forecast change attribution

### ✅ Scenario Planning
- Price change impact analysis
- Demand shock simulations
- Marketing campaign effects
- Economic downturn scenarios

### ✅ MLOps
- Model versioning and registry
- Performance drift detection
- Data drift monitoring
- Automated retraining triggers

### ✅ Enterprise APIs
- FastAPI REST endpoints
- Authentication ready
- Comprehensive error handling
- API documentation

### ✅ Interactive Dashboard
- Real-time forecasting interface
- Scenario analysis tools
- Performance monitoring
- Visualization charts

## 🔧 Configuration

Edit `config/simple_config.yaml` to customize:
- Target and date columns
- Model parameters
- Feature engineering settings
- Ensemble methods
- Uncertainty quantification

## 📊 Sample Output

When you run `python run_forecast.py`, you'll see:

```
2024-01-15 10:30:15 - __main__ - INFO - Starting ForecastEngine...
2024-01-15 10:30:15 - __main__ - INFO - Training models...
2024-01-15 10:30:16 - src.models.model_factory - INFO - ARIMA model trained successfully
2024-01-15 10:30:17 - src.models.model_factory - INFO - Random Forest model trained successfully
2024-01-15 10:30:17 - src.models.model_factory - INFO - Linear model trained successfully
2024-01-15 10:30:17 - __main__ - INFO - Generating forecast...
2024-01-15 10:30:18 - __main__ - INFO - Forecast Results:
2024-01-15 10:30:18 - __main__ - INFO - 30-day forecast: [215.3, 218.7, 222.1, 225.8, 229.2]...
2024-01-15 10:30:18 - __main__ - INFO - Key insights:
2024-01-15 10:30:18 - __main__ - INFO -   - Strong seasonal pattern detected
2024-01-15 10:30:18 - __main__ - INFO -   - Positive long-term trend continues
2024-01-15 10:30:18 - __main__ - INFO - Running scenario analysis...
2024-01-15 10:30:18 - __main__ - INFO - Scenario impact: -5.0%
2024-01-15 10:30:18 - __main__ - INFO - ForecastEngine completed successfully!
```

## 🎓 Academic & Professional Use

This implementation is suitable for:
- **Final-year projects**: Complete ML system with documentation
- **Seminar presentations**: Live demos and explanations
- **Startup prototypes**: Production-ready architecture
- **Enterprise deployment**: Scalable and maintainable code

## 🚀 Next Steps

1. **Customize Data**: Replace `data/sample_data.csv` with your data
2. **Tune Models**: Adjust parameters in `config/simple_config.yaml`
3. **Add Models**: Implement XGBoost, LSTM, or Prophet models
4. **Deploy**: Use Docker Compose for production deployment
5. **Scale**: Add cloud storage and distributed computing

---

**ForecastEngine**: Enterprise AI forecasting made simple and powerful! 🎯