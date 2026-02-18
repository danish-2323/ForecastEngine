# PDF Report Generation System

## Overview

Enterprise-grade PDF report generation for ForecastEngine that produces professional, executive-level reports with charts, tables, and AI-driven recommendations.

## Features

### Three Report Types

1. **Forecast Report** - Demand predictions and strategic recommendations
2. **Performance Report** - Model accuracy and reliability analysis
3. **Inventory Report** - Stock optimization and restocking strategy

### Professional Layout

- Company header with ForecastEngine branding
- Generated timestamp
- Page numbers
- Executive summaries
- Embedded charts with confidence intervals
- Professional tables with color coding
- Risk analysis sections
- AI-driven recommendations

## Installation

```bash
pip install reportlab matplotlib
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Standalone Usage

```python
from src.reports.pdf_generator import PDFReportGenerator
import pandas as pd
from datetime import datetime, timedelta

# Initialize generator
pdf_gen = PDFReportGenerator(output_dir="reports")

# Prepare data
data = pd.DataFrame({
    'date': pd.date_range(end=datetime.now(), periods=60, freq='D'),
    'sales': [100, 105, 110, ...]  # Historical sales
})

forecast_data = pd.DataFrame({
    'date': pd.date_range(start=datetime.now() + timedelta(days=1), periods=30, freq='D'),
    'forecast': [115, 120, 125, ...],
    'lower_bound': [105, 110, 115, ...],
    'upper_bound': [125, 130, 135, ...]
})

products_forecast = pd.DataFrame({
    'product': ['Product A', 'Product B', ...],
    'current_demand': [1200, 1400, ...],
    'forecast_demand': [1400, 1650, ...],
    'growth_pct': [16.7, 17.9, ...],
    'confidence': [0.92, 0.88, ...]
})

# Generate Forecast Report
pdf_path = pdf_gen.generate_forecast_report(data, forecast_data, products_forecast)
print(f"Report saved: {pdf_path}")
```

### 2. Dashboard Integration

The PDF generator is integrated into the Streamlit dashboard. Navigate to **Reports** page and click **Generate PDF** buttons.

### 3. Demo Script

Run the demo to generate all three reports:

```bash
python demo_pdf_reports.py
```

## Report Details

### 1. Forecast Report

**Purpose:** Predict future demand and recommend strategic actions

**Sections:**
- Executive Summary (trend, growth %, confidence)
- Forecast Chart (historical + forecast + confidence intervals)
- Product Forecast Table (current, forecast, growth, risk)
- AI Recommendations: Products to Increase Inventory
- AI Recommendations: Products to Reduce Production
- Risk Analysis (volatility, stockout probability)
- Strategic Recommendations (restocking, production planning)

**Key Insights:**
- Products with >10% growth → Increase inventory by 20-30%
- Products with <-5% decline → Reduce production by 15-25%
- Risk levels: High (>15% change), Medium (5-15%), Low (<5%)

**Input Data:**
```python
products_forecast = pd.DataFrame({
    'product': str,           # Product name
    'current_demand': float,  # Current demand
    'forecast_demand': float, # Predicted demand
    'growth_pct': float,      # Growth percentage
    'confidence': float       # Confidence (0-1)
})
```

### 2. Performance Report

**Purpose:** Evaluate model performance and forecasting reliability

**Sections:**
- Model Performance Summary (MAE, RMSE, MAPE, Accuracy)
- Key Performance Indicators Table
- Model Comparison Analysis (ARIMA, Random Forest, Linear, Ensemble)
- Forecast Reliability Analysis
- Model Recommendation

**Key Metrics:**
- MAE (Mean Absolute Error) - Lower is better
- RMSE (Root Mean Squared Error) - Lower is better
- MAPE (Mean Absolute Percentage Error) - Lower is better
- Accuracy % - Higher is better

**Input Data:**
```python
metrics = {
    'mae': float,   # Mean Absolute Error
    'rmse': float,  # Root Mean Squared Error
    'mape': float   # Mean Absolute Percentage Error (0-1)
}

model_comparison = pd.DataFrame({
    'model': str,      # Model name
    'mae': float,      # MAE for this model
    'rmse': float,     # RMSE for this model
    'accuracy': float  # Accuracy percentage
})
```

### 3. Inventory Report

**Purpose:** Provide inventory optimization and restocking strategy

**Sections:**
- Inventory Status Summary (total stock, demand, coverage)
- Current Inventory Analysis Table
- Stockout Risk Analysis (critical, medium, low risk products)
- Restocking Recommendations (immediate, safe, overstock)
- Optimal Restocking Schedule
- Cost Optimization Insights

**Key Thresholds:**
- Critical: <10 days coverage (High stockout risk >80%)
- Low: 10-20 days coverage (Medium stockout risk 40-60%)
- Safe: >30 days coverage
- Overstock: >60 days coverage

**Input Data:**
```python
inventory_data = pd.DataFrame({
    'product': str,           # Product name
    'current_stock': float,   # Current inventory
    'forecast_demand': float, # Expected demand
    'coverage_days': float    # Days of stock coverage
})

restock_schedule = pd.DataFrame({
    'product': str,        # Product name
    'restock_date': str,   # Recommended restock date
    'quantity': float,     # Restock quantity
    'priority': str        # Priority (Critical, High, Medium, Low)
})
```

## Visual Elements

### Charts
- Forecast chart with historical data, predictions, and confidence intervals
- Embedded as high-resolution PNG images (150 DPI)
- Professional color scheme (blue for historical, green for forecast)

### Tables
- Professional styling with alternating row colors
- Color-coded headers (dark gray background, white text)
- Centered alignment for numeric data
- Grid borders for clarity

### Color Scheme
- Headers: #1f2937 (dark gray)
- Success/Growth: #10b981 (green)
- Warning/Risk: #ef4444 (red)
- Info: #3b82f6 (blue)
- Background: #fafafa (light gray)

## File Output

Reports are saved to the `reports/` directory:

```
reports/
├── forecast_report.pdf
├── performance_report.pdf
├── inventory_report.pdf
└── forecast_chart.png (temporary chart file)
```

## API Reference

### PDFReportGenerator

```python
class PDFReportGenerator:
    def __init__(self, output_dir="reports"):
        """
        Initialize PDF report generator
        
        Args:
            output_dir (str): Directory to save PDF reports
        """
    
    def generate_forecast_report(self, data, forecast_data, products_forecast):
        """
        Generate Forecast Report PDF
        
        Args:
            data (pd.DataFrame): Historical data with 'date' and 'sales' columns
            forecast_data (pd.DataFrame): Forecast with 'date', 'forecast', 'lower_bound', 'upper_bound'
            products_forecast (pd.DataFrame): Product forecasts with required columns
        
        Returns:
            str: Path to generated PDF file
        """
    
    def generate_performance_report(self, metrics, model_comparison):
        """
        Generate Performance Report PDF
        
        Args:
            metrics (dict): Performance metrics (mae, rmse, mape)
            model_comparison (pd.DataFrame): Model comparison data
        
        Returns:
            str: Path to generated PDF file
        """
    
    def generate_inventory_report(self, inventory_data, forecast_data, restock_schedule):
        """
        Generate Inventory Report PDF
        
        Args:
            inventory_data (pd.DataFrame): Current inventory status
            forecast_data (pd.DataFrame): Forecast data for context
            restock_schedule (pd.DataFrame): Recommended restocking schedule
        
        Returns:
            str: Path to generated PDF file
        """
```

## Business Value

### Executive Decision Support
- Clear, actionable insights for non-technical stakeholders
- Visual representations of complex forecasting data
- Risk-aware recommendations for inventory management

### Strategic Planning
- Identify high-growth products for investment
- Detect declining products for cost reduction
- Optimize inventory to minimize stockouts and overstock

### Cost Optimization
- Reduce inventory carrying costs
- Minimize lost sales from stockouts
- Improve resource allocation efficiency

### Compliance & Audit
- Professional documentation for board meetings
- Audit trail of forecasting decisions
- Standardized reporting format

## Customization

### Modify Styles

Edit `_setup_custom_styles()` method to change fonts, colors, and spacing:

```python
self.styles.add(ParagraphStyle(
    name='CustomTitle',
    fontSize=24,
    textColor=colors.HexColor('#1f2937'),
    fontName='Helvetica-Bold'
))
```

### Add New Sections

Extend report generation methods to add custom sections:

```python
story.append(Paragraph("New Section", self.styles['SectionHeader']))
story.append(Paragraph("Custom content here", self.styles['Normal']))
```

### Change Chart Appearance

Modify `_create_chart()` method to customize chart styling:

```python
ax.plot(data['date'], data['sales'], 
        label='Historical', 
        color='#3b82f6',  # Change color
        linewidth=2)       # Change line width
```

## Troubleshooting

### Issue: "No module named 'reportlab'"
**Solution:** Install reportlab: `pip install reportlab`

### Issue: Charts not appearing in PDF
**Solution:** Ensure matplotlib backend is set to 'Agg': `matplotlib.use('Agg')`

### Issue: PDF file is empty or corrupted
**Solution:** Check that all required data columns are present in input DataFrames

### Issue: Font errors
**Solution:** ReportLab uses standard fonts (Helvetica, Times). No additional font installation needed.

## Performance

- Forecast Report: ~2-3 seconds
- Performance Report: ~1-2 seconds
- Inventory Report: ~2-3 seconds
- File sizes: 200-500 KB per report

## Future Enhancements

- [ ] Multi-page reports for large datasets
- [ ] Custom branding (logo upload)
- [ ] Email delivery integration
- [ ] Scheduled report generation
- [ ] Interactive PDF forms
- [ ] Multi-language support
- [ ] Custom chart types (bar, pie, heatmap)
- [ ] Comparison reports (month-over-month)

## License

Part of ForecastEngine AI Platform

---

**ForecastEngine**: Where AI meets business intelligence for superior forecasting outcomes.
