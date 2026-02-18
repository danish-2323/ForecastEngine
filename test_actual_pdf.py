"""
Test actual PDF parsing
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'src'))

from data_ingestion.pdf_parser import PDFSalesParser

# Test with your PDF
parser = PDFSalesParser()

pdf_path = "apple_multi_model_sales_forecastengine_parser.pdf"

try:
    with open(pdf_path, 'rb') as f:
        # First, let's see what text is extracted
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(f)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        print("="*60)
        print("EXTRACTED TEXT (first 500 chars):")
        print("="*60)
        print(text[:500])
        print("\n" + "="*60)
        
        # Now parse
        f.seek(0)
        sales_data = parser.parse_pdf(f)
        
        print("\nPARSED DATA:")
        print("="*60)
        print(f"Columns: {list(sales_data.columns)}")
        print(f"Shape: {sales_data.shape}")
        print(f"\nFirst 5 rows:")
        print(sales_data.head())
        
        valid, msg = parser.validate_data(sales_data)
        print(f"\nValidation: {valid}")
        print(f"Message: {msg}")
        
except FileNotFoundError:
    print(f"ERROR: {pdf_path} not found")
    print("Please place the PDF in the same directory as this script")
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
