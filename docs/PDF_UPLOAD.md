# PDF Sales Data Upload Feature

## Overview

Upload sales data from PDF files and automatically generate forecasts based on the uploaded data.

## Features

- **PDF Parsing**: Extracts date and sales data from PDF files
- **Multiple Formats**: Supports various date and data formats
- **Validation**: Ensures data quality before forecasting
- **Auto-Forecast**: Generates predictions based on uploaded data
- **Seamless Integration**: Works with existing dashboard and reports

## Supported PDF Formats

### Format 1: Table Format
```
Date       | Sales
2024-01-01 | 1200
2024-01-02 | 1350
2024-01-03 | 1180
```

### Format 2: Colon-Separated
```
2024-01-01: 1200
2024-01-02: 1350
2024-01-03: 1180
```

### Format 3: Multi-Line
```
2024-01-01
1200

2024-01-02
1350
```

## Supported Date Formats

- `YYYY-MM-DD` (2024-01-15)
- `DD/MM/YYYY` (15/01/2024)
- `MM/DD/YYYY` (01/15/2024)
- `DD-MM-YYYY` (15-01-2024)
- `MM-DD-YYYY` (01-15-2024)

## Usage

### 1. Dashboard Upload

1. Open the dashboard: `streamlit run src/dashboard/enterprise_dashboard.py`
2. In the sidebar, find **"📄 Upload Sales PDF"**
3. Click **"Browse files"** and select your PDF
4. Click **"📊 Parse & Forecast"**
5. View the forecast generated from your data

### 2. Programmatic Usage

```python
from src.data_ingestion.pdf_parser import PDFSalesParser

# Initialize parser
parser = PDFSalesParser()

# Parse PDF file
with open('sales_data.pdf', 'rb') as f:
    sales_data = parser.parse_pdf(f)

# Validate data
valid, message = parser.validate_data(sales_data)

if valid:
    print(f"Parsed {len(sales_data)} records")
    print(sales_data.head())
else:
    print(f"Validation failed: {message}")
```

## Data Requirements

- **Minimum Records**: 10 data points
- **Required Columns**: date, sales
- **Data Quality**: No missing values, no negative sales
- **Date Range**: Continuous or near-continuous dates

## Validation Rules

✅ **Pass Conditions:**
- At least 10 data points
- Both date and sales columns present
- No missing sales values
- All sales values are non-negative

❌ **Fail Conditions:**
- Less than 10 data points
- Missing required columns
- Missing or null sales values
- Negative sales values

## Generate Sample PDF

Create a test PDF with sample sales data:

```bash
python generate_sample_sales_pdf.py
```

This creates `sample_sales_data.pdf` with 90 days of sales data.

## How It Works

### 1. PDF Upload
User uploads PDF file through dashboard sidebar

### 2. Text Extraction
PyPDF2 extracts text from all pages

### 3. Pattern Matching
Regex patterns identify date-sales pairs:
- Table format (date | sales)
- Colon format (date: sales)
- Multi-line format

### 4. Data Parsing
Dates converted to datetime, sales to float

### 5. Validation
Checks data quality and completeness

### 6. Forecasting
If valid, data is used for forecast generation

### 7. Visualization
Charts and reports use uploaded data

## Error Handling

### "No sales data found in PDF"
- PDF doesn't contain recognizable date-sales patterns
- Try different PDF format or check data structure

### "Insufficient data points"
- Less than 10 records found
- Upload PDF with more historical data

### "Missing sales values"
- Some dates have no corresponding sales values
- Ensure all dates have sales data

### "Negative sales values found"
- Sales data contains negative numbers
- Check source data for errors

## Integration with Reports

When PDF data is uploaded, all reports automatically use the uploaded data:

- **Forecast Report**: Uses uploaded historical data
- **Performance Report**: Evaluates models on uploaded data
- **Inventory Report**: Calculates based on uploaded sales

## API Reference

### PDFSalesParser

```python
class PDFSalesParser:
    def parse_pdf(self, pdf_file):
        """
        Extract sales data from PDF
        
        Args:
            pdf_file: File object or bytes
            
        Returns:
            pd.DataFrame: Sales data with date and sales columns
        """
    
    def validate_data(self, df):
        """
        Validate parsed sales data
        
        Args:
            df (pd.DataFrame): Sales data
            
        Returns:
            tuple: (is_valid: bool, message: str)
        """
```

## Example Workflow

```python
# 1. Generate sample PDF
from generate_sample_sales_pdf import generate_sample_sales_pdf
generate_sample_sales_pdf("my_sales.pdf")

# 2. Parse PDF
from src.data_ingestion.pdf_parser import PDFSalesParser
parser = PDFSalesParser()

with open("my_sales.pdf", "rb") as f:
    sales_data = parser.parse_pdf(f)

# 3. Validate
valid, msg = parser.validate_data(sales_data)
print(f"Valid: {valid}, Message: {msg}")

# 4. Use in forecasting
if valid:
    # Data is now ready for forecasting
    print(f"Ready to forecast with {len(sales_data)} records")
```

## Troubleshooting

### PDF not parsing correctly
- Ensure PDF contains text (not scanned images)
- Check date and sales format matches supported patterns
- Try generating sample PDF to test

### Upload button not working
- Check file size (max 200MB)
- Ensure file extension is .pdf
- Try different browser

### Forecast not updating
- Click "Parse & Forecast" button after upload
- Check for error messages in sidebar
- Verify data validation passed

## Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] Excel file upload (.xlsx, .csv)
- [ ] Multiple product columns
- [ ] Custom date format specification
- [ ] Data preview before parsing
- [ ] Batch PDF upload
- [ ] Historical data comparison

## Dependencies

```bash
pip install PyPDF2>=3.0.0
```

---

**ForecastEngine**: Upload your data, get instant forecasts.
