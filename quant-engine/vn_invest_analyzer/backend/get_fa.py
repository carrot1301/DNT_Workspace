import sys
sys.stdout.reconfigure(encoding='utf-8')
from vnstock3 import Vnstock
import json

try:
    stock = Vnstock().stock(symbol='HPG', source='VCI')
    # Get basic metrics
    df = stock.finance.ratio(period='year', limit=1)
    records = df.to_dict('records')
    print(json.dumps(records))
except Exception as e:
    print(json.dumps({"error": str(e)}))
