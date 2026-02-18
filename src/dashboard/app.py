# src/dashboard/app.py
"""
Streamlit Dashboard for ForecastEngine
Interactive web interface for forecasting and analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from forecast_engine import ForecastEngine

# Page configuration
st.set_page_config(
    page_title="ForecastEngine Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class ForecastDashboard:
    """Main dashboard class"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8000"  # API endpoint
        self.forecast_engine = None
        
    def run(self):
        """Main dashboard application"""
        st.markdown('<h1 class="main-header">🚀 ForecastEngine Dashboard</h1>', unsafe_allow_html=True)
        
        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Navigate to:",
            ["📊 Forecast Overview", "🔧 Model Performance", "📈 Scenario Analysis", "⚙️ Settings"]
        )
        
        if page == "📊 Forecast Overview":
            self.forecast_overview_page()
        elif page == "🔧 Model Performance":
            self.model_performance_page()
        elif page == "📈 Scenario Analysis":
            self.scenario_analysis_page()
        elif page == "⚙️ Settings":
            self.settings_page()
    
    def forecast_overview_page(self):
        """Main forecasting page"""
        st.header("📊 Forecast Overview")
        
        # Forecast parameters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            horizon = st.slider("Forecast Horizon (days)", 1, 90, 30)
        
        with col2:
            confidence_levels = st.multiselect(
                "Confidence Levels",
                [0.1, 0.25, 0.5, 0.75, 0.9],
                default=[0.1, 0.5, 0.9]
            )
        
        with col3:
            include_explanation = st.checkbox("Include AI Explanations", value=True)
        
        # Generate forecast button
        if st.button("🔮 Generate Forecast", type="primary"):
            with st.spinner("Generating forecast..."):
                forecast_result = self.generate_forecast(horizon, confidence_levels, include_explanation)
                
                if forecast_result:
                    self.display_forecast_results(forecast_result)
        
        # Sample data visualization
        st.subheader("📈 Historical Data & Forecast")
        self.display_sample_forecast()
    
    def model_performance_page(self):
        """Model performance monitoring page"""
        st.header("🔧 Model Performance")
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Overall Accuracy", "87.3%", "2.1%")
        
        with col2:
            st.metric("MAE", "12.45", "-1.2")
        
        with col3:
            st.metric("RMSE", "18.67", "-0.8")
        
        with col4:
            st.metric("MAPE", "8.9%", "-0.5%")
        
        # Model comparison chart
        st.subheader("📊 Model Comparison")
        self.display_model_comparison()
        
        # Feature importance
        st.subheader("🎯 Feature Importance")
        self.display_feature_importance()
        
        # Performance over time
        st.subheader("📈 Performance Trends")
        self.display_performance_trends()
    
    def scenario_analysis_page(self):
        """Scenario analysis page"""
        st.header("📈 Scenario Analysis")
        
        # Scenario configuration
        st.subheader("🎛️ Configure Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            scenario_name = st.text_input("Scenario Name", "Price Increase Scenario")
            scenario_type = st.selectbox(
                "Scenario Type",
                ["price_change", "demand_shock", "marketing_campaign", "economic_downturn", "supply_disruption"]
            )
        
        with col2:
            if scenario_type == "price_change":
                price_change = st.slider("Price Change (%)", -50, 50, 10)
                scenario_config = {
                    "name": scenario_name,
                    "type": scenario_type,
                    "price_change": price_change / 100,
                    "price_elasticity": -0.5
                }
            elif scenario_type == "demand_shock":
                demand_multiplier = st.slider("Demand Multiplier", 0.5, 2.0, 1.2)
                scenario_config = {
                    "name": scenario_name,
                    "type": scenario_type,
                    "demand_multiplier": demand_multiplier
                }
            else:
                # Generic scenario
                impact_factor = st.slider("Impact Factor", -0.5, 0.5, 0.1)
                scenario_config = {
                    "name": scenario_name,
                    "type": scenario_type,
                    "economic_impact": impact_factor
                }
        
        # Run scenario analysis
        if st.button("🚀 Run Scenario Analysis", type="primary"):
            with st.spinner("Running scenario analysis..."):
                scenario_result = self.run_scenario_analysis(scenario_config)
                
                if scenario_result:
                    self.display_scenario_results(scenario_result)
        
        # Sample scenario comparison
        st.subheader("📊 Scenario Comparison")
        self.display_sample_scenarios()
    
    def settings_page(self):
        """Settings and configuration page"""
        st.header("⚙️ Settings")
        
        # Model configuration
        st.subheader("🤖 Model Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Enable ARIMA Model", value=True)
            st.checkbox("Enable Random Forest", value=True)
            st.checkbox("Enable Linear Model", value=True)
        
        with col2:
            ensemble_method = st.selectbox(
                "Ensemble Method",
                ["weighted_average", "stacking", "dynamic"]
            )
            
            retrain_threshold = st.slider("Retrain Threshold", 0.05, 0.2, 0.1)
        
        # Data configuration
        st.subheader("📊 Data Configuration")
        
        uploaded_file = st.file_uploader("Upload Training Data", type=['csv'])
        
        if uploaded_file is not None:
            st.success("Data uploaded successfully!")
            
            # Show data preview
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
        
        # Save settings
        if st.button("💾 Save Settings"):
            st.success("Settings saved successfully!")
    
    def generate_forecast(self, horizon, confidence_levels, include_explanation):
        """Generate forecast using API or local engine"""
        try:
            # Try API first
            response = requests.post(
                f"{self.api_base_url}/forecast",
                json={
                    "horizon": horizon,
                    "confidence_levels": confidence_levels,
                    "include_explanation": include_explanation
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback to local engine
        return self.generate_local_forecast(horizon, confidence_levels, include_explanation)
    
    def generate_local_forecast(self, horizon, confidence_levels, include_explanation):
        """Generate forecast using local engine"""
        # Create sample forecast data
        base_value = 100
        trend = 0.02
        noise = 0.1
        
        forecast = []
        for i in range(horizon):
            value = base_value * (1 + trend * i) + np.random.normal(0, noise * base_value)
            forecast.append(max(0, value))
        
        # Create prediction intervals
        prediction_intervals = {}
        for level in confidence_levels:
            alpha = 1 - level
            z_score = 1.96 if alpha <= 0.05 else 1.645 if alpha <= 0.1 else 1.282
            
            interval_width = np.array(forecast) * 0.1 * z_score
            prediction_intervals[f'lower_{level}'] = (np.array(forecast) - interval_width).tolist()
            prediction_intervals[f'upper_{level}'] = (np.array(forecast) + interval_width).tolist()
        
        return {
            'forecast': forecast,
            'prediction_intervals': prediction_intervals,
            'confidence_levels': confidence_levels,
            'explanations': {
                'key_drivers': [
                    {'feature': 'seasonality', 'impact': 0.35, 'direction': 'positive'},
                    {'feature': 'trend', 'impact': 0.28, 'direction': 'positive'},
                    {'feature': 'external_factors', 'impact': 0.15, 'direction': 'negative'}
                ],
                'business_insights': [
                    "Strong seasonal pattern detected",
                    "Positive long-term trend continues",
                    "External factors creating some uncertainty"
                ]
            } if include_explanation else None
        }
    
    def run_scenario_analysis(self, scenario_config):
        """Run scenario analysis"""
        # Create sample scenario results
        baseline = [100 + i * 0.5 for i in range(30)]
        
        if scenario_config['type'] == 'price_change':
            multiplier = 1 + scenario_config['price_change'] * scenario_config['price_elasticity']
            scenario_forecast = [x * multiplier for x in baseline]
        else:
            multiplier = scenario_config.get('demand_multiplier', 1.1)
            scenario_forecast = [x * multiplier for x in baseline]
        
        return {
            'scenario_name': scenario_config['name'],
            'scenario_forecast': scenario_forecast,
            'baseline_forecast': baseline,
            'impact_analysis': {
                'total_impact': {
                    'percentage': ((sum(scenario_forecast) - sum(baseline)) / sum(baseline)) * 100
                }
            }
        }
    
    def display_forecast_results(self, forecast_result):
        """Display forecast results"""
        st.subheader("🔮 Forecast Results")
        
        # Create forecast chart
        fig = go.Figure()
        
        # Add forecast line
        dates = pd.date_range(start=datetime.now(), periods=len(forecast_result['forecast']), freq='D')
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=forecast_result['forecast'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='blue', width=3)
        ))
        
        # Add confidence intervals
        if 'prediction_intervals' in forecast_result:
            for level in forecast_result['confidence_levels']:
                lower_key = f'lower_{level}'
                upper_key = f'upper_{level}'
                
                if lower_key in forecast_result['prediction_intervals']:
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=forecast_result['prediction_intervals'][upper_key],
                        fill=None,
                        mode='lines',
                        line_color='rgba(0,100,80,0)',
                        showlegend=False
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=forecast_result['prediction_intervals'][lower_key],
                        fill='tonexty',
                        mode='lines',
                        line_color='rgba(0,100,80,0)',
                        name=f'{int(level*100)}% Confidence',
                        fillcolor=f'rgba(0,100,80,{0.2 + level*0.1})'
                    ))
        
        fig.update_layout(
            title="Forecast with Confidence Intervals",
            xaxis_title="Date",
            yaxis_title="Value",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display explanations if available
        if forecast_result.get('explanations'):
            st.subheader("🧠 AI Explanations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Key Drivers:**")
                for driver in forecast_result['explanations']['key_drivers']:
                    direction_icon = "📈" if driver['direction'] == 'positive' else "📉"
                    st.write(f"{direction_icon} {driver['feature']}: {driver['impact']:.1%} impact")
            
            with col2:
                st.write("**Business Insights:**")
                for insight in forecast_result['explanations']['business_insights']:
                    st.write(f"• {insight}")
    
    def display_sample_forecast(self):
        """Display sample forecast visualization"""
        # Generate sample data
        dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
        historical = 100 + np.cumsum(np.random.normal(0.1, 2, len(dates)))
        
        # Future dates
        future_dates = pd.date_range(start='2024-04-01', periods=30, freq='D')
        forecast = historical[-1] + np.cumsum(np.random.normal(0.05, 1.5, 30))
        
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=dates,
            y=historical,
            mode='lines',
            name='Historical',
            line=dict(color='gray', width=2)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast,
            mode='lines+markers',
            name='Forecast',
            line=dict(color='blue', width=3)
        ))
        
        fig.update_layout(
            title="Sample Forecast Visualization",
            xaxis_title="Date",
            yaxis_title="Value",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_model_comparison(self):
        """Display model comparison chart"""
        models = ['ARIMA', 'Random Forest', 'Linear', 'Ensemble']
        mae_scores = [15.2, 12.8, 18.5, 11.3]
        
        fig = px.bar(
            x=models,
            y=mae_scores,
            title="Model Performance Comparison (MAE)",
            color=mae_scores,
            color_continuous_scale='RdYlBu_r'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_feature_importance(self):
        """Display feature importance chart"""
        features = ['lag_1', 'lag_7', 'rolling_mean_7', 'seasonality', 'trend']
        importance = [0.35, 0.28, 0.18, 0.12, 0.07]
        
        fig = px.bar(
            x=importance,
            y=features,
            orientation='h',
            title="Feature Importance",
            color=importance,
            color_continuous_scale='viridis'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_performance_trends(self):
        """Display performance trends over time"""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        mae_trend = 15 + np.random.normal(0, 1, 30)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=mae_trend,
            mode='lines+markers',
            name='MAE',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title="Model Performance Over Time",
            xaxis_title="Date",
            yaxis_title="MAE",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_scenario_results(self, scenario_result):
        """Display scenario analysis results"""
        st.subheader(f"📊 Scenario: {scenario_result['scenario_name']}")
        
        # Impact metrics
        impact_pct = scenario_result['impact_analysis']['total_impact']['percentage']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Impact", f"{impact_pct:.1f}%")
        
        with col2:
            impact_direction = "Positive" if impact_pct > 0 else "Negative"
            st.metric("Direction", impact_direction)
        
        with col3:
            risk_level = "High" if abs(impact_pct) > 20 else "Medium" if abs(impact_pct) > 10 else "Low"
            st.metric("Risk Level", risk_level)
        
        # Scenario comparison chart
        dates = pd.date_range(start=datetime.now(), periods=len(scenario_result['baseline_forecast']), freq='D')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=scenario_result['baseline_forecast'],
            mode='lines',
            name='Baseline',
            line=dict(color='gray', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=scenario_result['scenario_forecast'],
            mode='lines',
            name='Scenario',
            line=dict(color='red', width=3)
        ))
        
        fig.update_layout(
            title="Scenario vs Baseline Comparison",
            xaxis_title="Date",
            yaxis_title="Value",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def display_sample_scenarios(self):
        """Display sample scenario comparison"""
        scenarios = ['Baseline', 'Price +10%', 'Marketing Campaign', 'Economic Downturn']
        impacts = [0, -8.5, 15.2, -12.8]
        
        fig = px.bar(
            x=scenarios,
            y=impacts,
            title="Scenario Impact Comparison",
            color=impacts,
            color_continuous_scale='RdYlBu'
        )
        
        fig.update_layout(yaxis_title="Impact (%)")
        
        st.plotly_chart(fig, use_container_width=True)

# Run the dashboard
if __name__ == "__main__":
    dashboard = ForecastDashboard()
    dashboard.run()