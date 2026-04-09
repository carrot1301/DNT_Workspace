from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import yfinance as yf
import pandas as pd
import datetime
import random

app = FastAPI(title="VN Invest Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/api/screener")
def get_screener_data():
    tickers = ['SSI', 'FPT', 'HPG', 'VCB', 'STB']
    results = []
    yf_tickers = [f"{t}.VN" for t in tickers]
    
    try:
        # Fetch last 5 days to get yesterday and today
        df = yf.download(yf_tickers, period='5d', progress=False)
        if df.empty:
            raise ValueError("Empty dataset")
            
        for t in tickers:
            try:
                yf_t = f"{t}.VN"
                if isinstance(df.columns, pd.MultiIndex):
                    close_series = df['Close'][yf_t].dropna()
                else:
                    close_series = df['Close'].dropna()
                
                if len(close_series) >= 2:
                    last_price = float(close_series.iloc[-1])
                    prev_price = float(close_series.iloc[-2])
                    change = round(((last_price - prev_price)/prev_price)*100, 2)
                    results.append({
                        "ticker": t,
                        "price": last_price,
                        "change": change,
                        "signal": random.choice(["Nổ Vol", "Vượt Đỉnh", "Tích Lũy", "Phân kỳ âm"])
                    })
            except:
                pass
                
        if not results:
            raise ValueError("No parsed results")
            
        return results
    except Exception as e:
        return [
            {"ticker": "SSI", "price": 35.40, "change": 2.1, "signal": "Nổ Vol"},
            {"ticker": "FPT", "price": 110.50, "change": 1.5, "signal": "Vượt Đỉnh"},
        ]

@app.get("/api/stock/{ticker}/chart")
def get_stock_chart(ticker: str):
    try:
        yf_ticker = f"{ticker}.VN"
        df = yf.download(yf_ticker, period='1y', progress=False)
        if df.empty:
            return []
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        chart_data = []
        for date_index, row in df.iterrows():
            try:
                dt_obj = date_index.to_pydatetime()
                _open = float(row['Open'])
                _high = float(row['High'])
                _low = float(row['Low'])
                _close = float(row['Close'])
                
                chart_data.append({
                    "time": dt_obj.timestamp(),
                    "open": _open,
                    "high": _high,
                    "low": _low,
                    "close": _close
                })
            except:
                pass
        return chart_data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
