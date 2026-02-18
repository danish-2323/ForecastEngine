"""
Demo script to test PDF report generation
Generates all three enterprise reports
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent / 'src'))

from reports.pdf_generator import PDFReportGenerator

def main():
    print("=" * 60)
    print("ForecastEngine - PDF Report Generation Demo")
    print("=" * 60)
    
    # Initialize PDF generator
    pdf_gen = PDFReportGenerator(output_dir="reports")
    print("\n✓ PDF Generator initialized")
    
    # Generate sample data
    print("\n📊 Generating sample data...")
    
    # Historical data
    hist_dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
    hist_values = 100 + np.cumsum(np.random.randn(60) * 2)
    data = pd.DataFrame({'date': hist_dates, 'sales': hist_values})
    
    # Forecast data
    forecast_dates = pd.date_range(start=datetime.now() + timedelta(days=1), periods=30, freq='D')
    forecast_values = hist_values[-1] + np.cumsum(np.random.randn(30) * 1.5)
    forecast_data = pd.DataFrame({
        'date': forecast_dates,
        'forecast': forecast_values,
        'lower_bound': forecast_values - 10,
        'upper_bound': forecast_values + 10
    })
    
    # Product forecast data
    products_forecast = pd.DataFrame({
        'product': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'current_demand': [1200, 1400, 1600, 1800, 2000],
        'forecast_demand': [1400, 1650, 1680, 1620, 2250],
        'growth_pct': [16.7, 17.9, 5.0, -10.0, 12.5],
        'confidence': [0.92, 0.88, 0.85, 0.78, 0.90]
    })
    
    # Performance metrics
    metrics = {
        'mae': 12.45,
        'rmse': 18.67,
        'mape': 0.089
    }
    
    # Model comparison
    model_comparison = pd.DataFrame({
        'model': ['Ensemble', 'Random Forest', 'ARIMA', 'Linear'],
        'mae': [12.45, 13.21, 15.67, 16.89],
        'rmse': [18.67, 19.45, 22.34, 24.12],
        'accuracy': [87.3, 85.4, 82.1, 79.8]
    })
    
    # Inventory data
    inventory_data = pd.DataFrame({
        'product': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'current_stock': [1200, 850, 2100, 450, 1650],
        'forecast_demand': [1400, 1650, 1680, 1620, 2250],
        'coverage_days': [25, 15, 38, 8, 22]
    })
    
    # Restock schedule
    restock_schedule = pd.DataFrame({
        'product': ['Product D', 'Product B', 'Product E'],
        'restock_date': ['2024-03-15', '2024-03-20', '2024-03-25'],
        'quantity': [1200, 800, 600],
        'priority': ['Critical', 'High', 'Medium']
    })
    
    print("✓ Sample data generated")
    
    # Generate reports
    print("\n" + "=" * 60)
    print("Generating PDF Reports...")
    print("=" * 60)
    
    # 1. Forecast Report
    print("\n1️⃣  Generating Forecast Report...")
    forecast_path = pdf_gen.generate_forecast_report(data, forecast_data, products_forecast)
    print(f"   ✓ Forecast Report saved: {forecast_path}")
    
    # 2. Performance Report
    print("\n2️⃣  Generating Performance Report...")
    performance_path = pdf_gen.generate_performance_report(metrics, model_comparison)
    print(f"   ✓ Performance Report saved: {performance_path}")
    
    # 3. Inventory Report
    print("\n3️⃣  Generating Inventory Report...")
    inventory_path = pdf_gen.generate_inventory_report(inventory_data, forecast_data, restock_schedule)
    print(f"   ✓ Inventory Report saved: {inventory_path}")
    
    print("\n" + "=" * 60)
    print("✅ All Reports Generated Successfully!")
    print("=" * 60)
    print(f"\n📁 Reports saved in: {pdf_gen.output_dir}/")
    print("\nGenerated files:")
    print("  • forecast_report.pdf")
    print("  • performance_report.pdf")
    print("  • inventory_report.pdf")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
