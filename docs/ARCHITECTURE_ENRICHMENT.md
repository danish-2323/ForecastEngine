# External API Enrichment Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FORECASTENGINE SYSTEM                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES LAYER                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Historical   │  │  Weather     │  │    News      │  │  Analytics │ │
│  │  CSV Data    │  │    API       │  │    API       │  │    API     │ │
│  │              │  │              │  │              │  │            │ │
│  │ • Dates      │  │ • Temp       │  │ • Count      │  │ • Traffic  │ │
│  │ • Values     │  │ • Conditions │  │ • Sentiment  │  │ • Bounce   │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
│         │                 │                  │                 │        │
│         │                 └──────────┬───────┴─────────────────┘        │
│         │                            │                                  │
└─────────┼────────────────────────────┼──────────────────────────────────┘
          │                            │
          │                            │
┌─────────▼────────────────────────────▼──────────────────────────────────┐
│                    DATA INGESTION & ENRICHMENT                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │              DataConnector (data_connector.py)                    │ │
│  │  • Load historical CSV                                            │ │
│  │  • Validate data quality                                          │ │
│  │  • Call ExternalDataEnricher                                      │ │
│  └───────────────────────────┬───────────────────────────────────────┘ │
│                              │                                         │
│  ┌───────────────────────────▼───────────────────────────────────────┐ │
│  │        ExternalDataEnricher (external_enrichment.py)              │ │
│  │                                                                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │ │
│  │  │ Fetch        │  │ Fetch        │  │ Fetch        │           │ │
│  │  │ Weather      │  │ News         │  │ Analytics    │           │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │ │
│  │         │                  │                  │                   │ │
│  │         └──────────────────┼──────────────────┘                   │ │
│  │                            │                                      │ │
│  │  ┌─────────────────────────▼──────────────────────────┐          │ │
│  │  │  Merge on Date (align with historical data)        │          │ │
│  │  └─────────────────────────┬──────────────────────────┘          │ │
│  │                            │                                      │ │
│  │  ┌─────────────────────────▼──────────────────────────┐          │ │
│  │  │  Handle Missing Values (forward fill, zero fill)   │          │ │
│  │  └─────────────────────────┬──────────────────────────┘          │ │
│  │                            │                                      │ │
│  └────────────────────────────┼──────────────────────────────────────┘ │
│                               │                                        │
│                    ┌──────────▼──────────┐                            │
│                    │  Enriched Dataset   │                            │
│                    │  (CSV + API data)   │                            │
│                    └──────────┬──────────┘                            │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                      FEATURE ENGINEERING LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │           FeatureBuilder (feature_builder.py)                     │ │
│  │                                                                    │ │
│  │  Historical Features:          External Features:                 │ │
│  │  • lag_1, lag_7, lag_30       • news_count                        │ │
│  │  • rolling_mean_7             • news_count_lag_1                  │ │
│  │  • rolling_std_7              • news_count_lag_7                  │ │
│  │  • day_of_week                • avg_temp                          │ │
│  │  • month, is_weekend          • avg_temp_rolling_7                │ │
│  │                               • web_traffic                        │ │
│  │                               • daily_orders                       │ │
│  └───────────────────────────┬───────────────────────────────────────┘ │
│                              │                                         │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                         MODEL TRAINING LAYER                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   ARIMA      │  │ RandomForest │  │   Linear     │                 │
│  │              │  │              │  │              │                 │
│  │ (Historical  │  │ (Historical  │  │ (Historical  │                 │
│  │  only)       │  │  + External) │  │  + External) │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
│         │                  │                  │                        │
│         └──────────────────┼──────────────────┘                        │
│                            │                                           │
│  ┌─────────────────────────▼──────────────────────────┐               │
│  │         Ensemble Manager (weighted average)        │               │
│  └─────────────────────────┬──────────────────────────┘               │
│                            │                                           │
└────────────────────────────┼────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                    PREDICTION & EXPLANATION LAYER                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    Forecast Generation                            │ │
│  │  • 30-day predictions                                             │ │
│  │  • Confidence intervals (10%, 50%, 90%)                           │ │
│  └───────────────────────────┬───────────────────────────────────────┘ │
│                              │                                         │
│  ┌───────────────────────────▼───────────────────────────────────────┐ │
│  │              Explainability (explainer.py)                        │ │
│  │                                                                    │ │
│  │  Feature Importance:                                              │ │
│  │  • lag_7: 0.298                                                   │ │
│  │  • news_count [EXTERNAL]: 0.245                                   │ │
│  │  • web_traffic [EXTERNAL]: 0.187                                  │ │
│  │                                                                    │ │
│  │  Business Insights:                                               │ │
│  │  • "External signals enriching predictions"                       │ │
│  │  • "Increased demand correlated with news activity"               │ │
│  └───────────────────────────┬───────────────────────────────────────┘ │
│                              │                                         │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                           OUTPUT LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  Dashboard   │  │   REST API   │  │   Reports    │  │   Alerts   │ │
│  │              │  │              │  │              │  │            │ │
│  │ • Forecasts  │  │ • Endpoints  │  │ • PDF/Excel  │  │ • Email    │ │
│  │ • Intervals  │  │ • JSON       │  │ • Charts     │  │ • Slack    │ │
│  │ • Insights   │  │ • Auth       │  │ • Summaries  │  │ • SMS      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Sequence

```
1. User Request
   ↓
2. Load Historical CSV (data_connector.py)
   ↓
3. Check if external APIs enabled
   ↓
4. Fetch External Data (parallel)
   ├─ Weather API
   ├─ News API
   ├─ Analytics API
   └─ E-commerce API
   ↓
5. Merge External Data with Historical (date-aligned)
   ↓
6. Handle Missing Values (forward fill, zero fill)
   ↓
7. Feature Engineering
   ├─ Historical features (lags, rolling windows)
   └─ External features (lags, rolling windows)
   ↓
8. Model Training
   ├─ ARIMA (historical only)
   ├─ RandomForest (historical + external)
   └─ Linear (historical + external)
   ↓
9. Ensemble Prediction (weighted average)
   ↓
10. Uncertainty Quantification (confidence intervals)
    ↓
11. Explainability Generation
    ├─ Feature importance
    ├─ External signal attribution
    └─ Business insights
    ↓
12. Return Results
```

## Failure Handling Flow

```
API Call → Success? ─Yes→ Use Real Data
              │
              No
              ↓
         Retry (3x)
              │
              ↓
         Still Failed?
              │
              ├─Yes→ Use Mock Data (log warning)
              │
              └─No→ Use Real Data
              
Final Result: System ALWAYS works (graceful degradation)
```

## Module Interaction

```
forecast_engine.py (Main Orchestrator)
    │
    ├─→ data_connector.py
    │       │
    │       └─→ external_enrichment.py
    │               │
    │               ├─→ Weather API
    │               ├─→ News API
    │               ├─→ Analytics API
    │               └─→ E-commerce API
    │
    ├─→ feature_builder.py
    │       │
    │       └─→ Process external features
    │
    ├─→ model_factory.py
    │       │
    │       └─→ Train with enriched features
    │
    ├─→ ensemble_manager.py
    │
    ├─→ uncertainty_quantifier.py
    │
    └─→ explainer.py
            │
            └─→ Highlight external signals
```

## Key Design Principles

1. **Non-Invasive**: Original pipeline unchanged
2. **Graceful Degradation**: Works without APIs
3. **Parallel Fetching**: Fast API calls
4. **Date Alignment**: Automatic merging
5. **Missing Value Handling**: Robust fallbacks
6. **Feature Generation**: Automatic lag creation
7. **Explainability**: Clear attribution
8. **Configurability**: Easy enable/disable

## Configuration Flow

```
enriched_config.yaml
    │
    ├─→ external_apis.enabled = true/false
    │
    ├─→ sources.weather.enabled = true/false
    ├─→ sources.news.enabled = true/false
    ├─→ sources.analytics.enabled = true/false
    └─→ sources.ecommerce.enabled = true/false
    
If enabled = false → Skip enrichment (historical only)
If enabled = true → Fetch and merge external data
```

## Performance Optimization

```
┌─────────────────────────────────────┐
│  Parallel API Fetching              │
│  ┌─────────┐  ┌─────────┐          │
│  │Weather  │  │  News   │          │
│  │  API    │  │  API    │          │
│  └────┬────┘  └────┬────┘          │
│       │            │                │
│       └────────┬───┘                │
│                │                    │
│  ┌─────────┐  │  ┌─────────┐       │
│  │Analytics│  │  │E-commerce│      │
│  │  API    │  │  │  API    │       │
│  └────┬────┘  │  └────┬────┘       │
│       │       │       │             │
│       └───────┴───────┘             │
│                │                    │
│         All Complete                │
└─────────────────────────────────────┘
```

This architecture ensures:
- ✓ Fast data enrichment
- ✓ Fault tolerance
- ✓ Backward compatibility
- ✓ Easy maintenance
- ✓ Clear separation of concerns
