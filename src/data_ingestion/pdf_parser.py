"""
PDF Sales Data Parser
Extracts multi-product sales data from PDF files
"""

import re
import pandas as pd
from datetime import datetime
import PyPDF2
import io

class PDFSalesParser:
    """Parse multi-product sales data from PDF files"""
    
    def __init__(self):
        self.supported_formats = ['table', 'text', 'structured']
        self.product_keywords = ['Product', 'Model', 'Item', 'Name', 'Device', 'SKU', 'Product Name', 'Model Name']
        self.product_pattern = r'(?:Product|Model|Item|Name|Device|SKU|Product Name|Model Name)\s*[:|]\s*([A-Za-z0-9\s]+?)\s*[|,\t:]'
        self.column_aliases = {
            'model': 'product',
            'item': 'product',
            'name': 'product',
            'device': 'product',
            'sku': 'product',
            'product name': 'product',
            'model name': 'product'
        }
    
    def parse_pdf(self, pdf_file):
        """
        Extract multi-product sales data from PDF file
        
        Args:
            pdf_file: File object or bytes
            
        Returns:
            pd.DataFrame: Sales data with date, product, and sales columns
        """
        try:
            # Read PDF
            if isinstance(pdf_file, bytes):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
            else:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Parse sales data
            sales_data = self._extract_multi_product_data(text)
            
            if sales_data.empty:
                raise ValueError("No sales data found in PDF")
            
            # Ensure required columns exist
            if 'product' not in sales_data.columns:
                if 'model' in sales_data.columns:
                    sales_data['product'] = sales_data['model']
                elif 'item' in sales_data.columns:
                    sales_data['product'] = sales_data['item']
                elif 'name' in sales_data.columns:
                    sales_data['product'] = sales_data['name']
                elif 'device' in sales_data.columns:
                    sales_data['product'] = sales_data['device']
                elif 'sku' in sales_data.columns:
                    sales_data['product'] = sales_data['sku']
                else:
                    raise ValueError("No product column found in parsed data")
            
            # Ensure only required columns
            sales_data = sales_data[['date', 'product', 'sales']]
            
            return sales_data
            
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    def _extract_multi_product_data(self, text):
        """Extract multi-product sales data from text"""
        data = []
        
        # Pattern for: Date: YYYY-MM-DD Model: Product Name Sales: Number
        pattern = r'Date:\s*(\d{4}-\d{2}-\d{2})\s+(?:Model|Product|Item|Device|SKU|Name):\s*(.+?)\s+Sales:\s*(\d+)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for match in matches:
            try:
                date_str = match[0].strip()
                product_str = match[1].strip()
                sales_str = match[2].strip()
                
                date = self._parse_date(date_str)
                sales = float(sales_str)
                
                if product_str and sales > 0:
                    data.append({'date': date, 'product': product_str, 'sales': sales})
            except Exception as e:
                continue
        
        if not data:
            return pd.DataFrame(columns=['date', 'product', 'sales'])
        
        df = pd.DataFrame(data)
        df = df.drop_duplicates(subset=['date', 'product'])
        df = df.sort_values(['product', 'date'])
        df['date'] = pd.to_datetime(df['date'])
        
        return df[['date', 'product', 'sales']]
    
    def _parse_date(self, date_str):
        """Parse date string to datetime"""
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        raise ValueError(f"Cannot parse date: {date_str}")
    
    def validate_data(self, df):
        """Validate parsed sales data"""
        if df.empty:
            return False, "No data found"
        
        if 'date' not in df.columns or 'product' not in df.columns or 'sales' not in df.columns:
            return False, "Missing required columns (date, product, sales)"
        
        if len(df) < 10:
            return False, f"Insufficient data points ({len(df)}). Need at least 10."
        
        if df['sales'].isna().any():
            return False, "Missing sales values"
        
        if (df['sales'] < 0).any():
            return False, "Negative sales values found"
        
        # Check each product has minimum data
        products = df['product'].unique()
        for product in products:
            product_data = df[df['product'] == product]
            if len(product_data) < 5:
                return False, f"Product '{product}' has insufficient data ({len(product_data)} records)"
        
        return True, f"Data valid: {len(products)} products, {len(df)} records"
