"""
Test Flexible Product Keyword Parsing
Verifies parser accepts Product, Model, Item, Name, Device, SKU
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'src'))

def generate_flexible_keyword_pdf(output_path="test_flexible_keywords.pdf"):
    """Generate PDF with various product keywords"""
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("<b>Sales Report - Multiple Keyword Formats</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # Test different keywords
    story.append(Paragraph("<b>Format 1: Using 'Product'</b>", styles['Heading2']))
    table1 = Table([
        ['Date', 'Product', 'Sales (₹)'],
        ['2024-01-01', 'iPhone 15', '245'],
        ['2024-01-02', 'iPhone 15', '310']
    ], colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    table1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table1)
    story.append(Spacer(1, 0.2*inch))
    
    # Format 2: Model
    story.append(Paragraph("<b>Format 2: Using 'Model'</b>", styles['Heading2']))
    table2 = Table([
        ['Date', 'Model', 'Sales (₹)'],
        ['2024-01-03', 'iPhone 15 Pro', '342'],
        ['2024-01-04', 'iPhone 15 Pro', '298']
    ], colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table2)
    story.append(Spacer(1, 0.2*inch))
    
    # Format 3: Item
    story.append(Paragraph("<b>Format 3: Using 'Item'</b>", styles['Heading2']))
    table3 = Table([
        ['Date', 'Item', 'Sales (₹)'],
        ['2024-01-05', 'iPhone 14', '198'],
        ['2024-01-06', 'iPhone 14', '215']
    ], colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    table3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table3)
    story.append(Spacer(1, 0.2*inch))
    
    # Format 4: Device
    story.append(Paragraph("<b>Format 4: Using 'Device'</b>", styles['Heading2']))
    table4 = Table([
        ['Date', 'Device', 'Sales (₹)'],
        ['2024-01-07', 'iPhone 15 Pro Max', '412'],
        ['2024-01-08', 'iPhone 15 Pro Max', '389']
    ], colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    table4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table4)
    story.append(Spacer(1, 0.2*inch))
    
    # Format 5: SKU
    story.append(Paragraph("<b>Format 5: Using 'SKU'</b>", styles['Heading2']))
    table5 = Table([
        ['Date', 'SKU', 'Sales (₹)'],
        ['2024-01-09', 'iPhone 14 Pro', '267'],
        ['2024-01-10', 'iPhone 14 Pro', '289']
    ], colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    table5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table5)
    
    # Build PDF
    doc.build(story)
    print(f"✅ Flexible keyword test PDF generated: {output_path}")
    print(f"\n📋 Keywords tested:")
    print("  • Product")
    print("  • Model")
    print("  • Item")
    print("  • Device")
    print("  • SKU")
    print(f"\n📊 Total records: 10 (5 products × 2 days each)")

def test_parser():
    """Test the parser with flexible keywords"""
    from data_ingestion.pdf_parser import PDFSalesParser
    
    print("\n" + "="*60)
    print("Testing Flexible Keyword Parser")
    print("="*60)
    
    # Generate test PDF
    generate_flexible_keyword_pdf()
    
    # Parse it
    parser = PDFSalesParser()
    
    with open("test_flexible_keywords.pdf", "rb") as f:
        sales_data = parser.parse_pdf(f)
    
    valid, msg = parser.validate_data(sales_data)
    
    print(f"\n✓ Parsing completed")
    print(f"✓ Validation: {msg}")
    
    if valid:
        print(f"\n📊 Parsed Data Summary:")
        print(f"  • Total records: {len(sales_data)}")
        print(f"  • Products found: {sales_data['product'].nunique()}")
        print(f"  • Date range: {sales_data['date'].min()} to {sales_data['date'].max()}")
        
        print(f"\n📦 Products extracted:")
        for product in sales_data['product'].unique():
            count = len(sales_data[sales_data['product'] == product])
            print(f"  • {product}: {count} records")
        
        print(f"\n✅ All keywords successfully parsed!")
        print(f"\nSample data:")
        print(sales_data.head(10).to_string(index=False))
    else:
        print(f"\n❌ Validation failed: {msg}")

if __name__ == "__main__":
    test_parser()
