import pandas as pd
import os
import streamlit as st

def clean_vietnamese_stock_data(filepath):
    """Utility function to read and clean Vietnamese stock data from Simplize exports."""
    if not os.path.exists(filepath):
        st.error(f"Critical Error: File not found at {filepath}")
        return None
        
    try:
        # Simplize CSVs usually have 4 lines of metadata. Skip them.
        df = pd.read_csv(filepath, skiprows=4)
        
        # Clean column names (remove spaces)
        df.columns = df.columns.str.strip()
        
        # Mapping Vietnamese headers to standard Financial English OHLCV
        rename_map = {
            'NGÀY': 'date',
            'GIÁ MỞ CỬA': 'open',
            'GIÁ CAO NHẤT': 'high',
            'GIÁ THẤP NHẤT': 'low',
            'GIÁ ĐÓNG CỬA': 'close',
            'KHỐI LƯỢNG': 'volume'
        }
        df = df.rename(columns=rename_map)
        
        # 1. Date Processing
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
        df = df.dropna(subset=['date']) # Remove watermark/footer rows
        df.set_index('date', inplace=True)
        
        # 2. Robust Numeric Cleaning
        cols_to_clean = ['open', 'high', 'low', 'close', 'volume']
        for col in cols_to_clean:
            if col in df.columns:
                # Remove commas and convert to numeric
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        
        # 3. Final Polish
        df = df.sort_index(ascending=True)
        
        # Remove any remaining NaN values in critical price columns
        df = df.dropna(subset=['close'])
        
        return df

    except Exception as e:
        st.error(f"Error parsing {filepath}: {e}")
        return None

@st.cache_data
def load_market(filepath="vn30_quant_app/data/market/VNINDEX.csv"):
    """Loads and caches VNINDEX benchmark data."""
    df = clean_vietnamese_stock_data(filepath)
    if df is not None:
        # Rename for specific reference in calculations
        df = df.rename(columns={'close': 'market_close'}).copy()
    return df

@st.cache_data
def load_stock(ticker, base_dir="vn30_quant_app/data/stocks"):
    """Loads and caches individual stock data based on ticker name."""
    filepath = f"{base_dir}/{ticker}.csv"
    df = clean_vietnamese_stock_data(filepath)
    if df is not None:
        # Rename for specific reference in calculations
        df = df.rename(columns={'close': 'stock_close'}).copy()
    return df

@st.cache_data
def get_aligned_data(ticker):
    """Aligns stock and market data on the same time index for accurate Quant metrics."""
    market_df = load_market()
    stock_df = load_stock(ticker)
    
    if stock_df is None or market_df is None:
        return None
        
    # Isolate benchmark close to avoid column overlap during join
    market_close_only = market_df[['market_close']]
    
    # Inner join: Keep only dates present in BOTH datasets (trading days)
    aligned_df = market_close_only.join(stock_df, how='inner')
    
    # Quantitative safety: Forward fill missing gaps (if any), then backward fill
    aligned_df = aligned_df.ffill().bfill()
    
    return aligned_df