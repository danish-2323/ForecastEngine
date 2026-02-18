"""
Generate Sample Multi-Product Sales PDF for Testing
Creates a PDF with sales data for multiple products
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_sales_pdf(output_path="sample_sales_data.pdf"):
    """Generate a sample multi-product sales PDF with test data"""
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("<b>Multi-Product Sales Report - Historical Data</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # Generate sample data for multiple products
    start_date = datetime.now() - timedelta(days=60)
    dates = pd.date_range(start=start_date, periods=60, freq='D')
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    
    # Format: Table with Date | Product | Sales
    story.append(Paragraph("<b>Daily Sales Data by Product</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    table_data = [['Date', 'Product', 'Sales (₹)']]
    
    for date in dates:
        for product in products:
            base_sales = {'Product A': 1000, 'Product B': 1500, 'Product C': 800, 'Product D': 1200, 'Product E': 2000}
            sales = base_sales[product] + np.random.randn() * 100
            table_data.append([date.strftime('%Y-%m-%d'), product, f'{sales:.2f}'])
    
    table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    story.append(table)
    
    # Build PDF
    doc.build(story)
    print(f"✅ Sample multi-product sales PDF generated: {output_path}")
    print(f"  - Products: {len(products)}")
    print(f"  - Date range: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
    print(f"  - Total records: {len(dates) * len(products)}")
    print(f"\n📦 Products: {', '.join(products)}")

if __name__ == "__main__":
    generate_sample_sales_pdf()
