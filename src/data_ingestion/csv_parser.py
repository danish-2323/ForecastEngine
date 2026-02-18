"""
CSV Sales Data Parser with Automatic Column Mapping
Converts various CSV formats to ForecastEngine internal format
"""

import pandas as pd
from typing import Tuple

class CSVSalesParser:
    """Parse CSV files with automatic column mapping to ForecastEngine format"""
    
    COLUMN_ALIASES = {
        "date": ["date", "sale_date", "order_date", "transaction_date", "timestamp"],
        "product": ["product", "product_id", "product_name", "model", "item", "sku"],
        "sales": ["sales", "quantity", "units", "revenue", "amount", "qty"]
    }
    
    def __init__(self):
        pass
    
    def _find_column(self, df: pd.DataFrame, target: str) -> str:
        """Find matching column from aliases"""
        df_cols_lower = {col.lower().strip(): col for col in df.columns}
        
        for alias in self.COLUMN_ALIASES[target]:
            if alias.lower() in df_cols_lower:
                return df_cols_lower[alias.lower()]
        
        raise ValueError(f"No column found for '{target}'. Expected one of: {self.COLUMN_ALIASES[target]}")
    
    def parse_csv(self, file_path) -> pd.DataFrame:
        """Parse CSV and convert to ForecastEngine format"""
        df = pd.read_csv(file_path)
        
        # Find matching columns
        date_col = self._find_column(df, "date")
        product_col = self._find_column(df, "product")
        sales_col = self._find_column(df, "sales")
        
        # Create mapping
        column_mapping = {
            date_col: "date",
            product_col: "product",
            sales_col: "sales"
        }
        
        # Rename and select only required columns
        df = df.rename(columns=column_mapping)
        df = df[["date", "product", "sales"]]
        
        # Convert data types
        df["date"] = pd.to_datetime(df["date"])
        df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
        
        # Remove rows with invalid sales values
        df = df.dropna(subset=["sales"])
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate parsed data"""
        if df.empty:
            return False, "CSV file is empty"
        
        if len(df) < 10:
            return False, f"Insufficient data: {len(df)} records (minimum 10 required)"
        
        if (df["sales"] < 0).any():
            return False, "Negative sales values detected"
        
        return True, f"Successfully parsed {len(df)} records"
