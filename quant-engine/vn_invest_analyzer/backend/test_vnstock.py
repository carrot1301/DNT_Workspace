from vnstock3 import Vnstock
import datetime

start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

try:
    stock = Vnstock().stock(symbol='SSI', source='VCI')
    df = stock.quote.history(start=start_date, end=end_date)
    print('VCI Columns:', df.columns)
    print(df.head(2))
except Exception as e:
    print('VCI Error:', e)

try:
    stock = Vnstock().stock(symbol='SSI', source='SSI')
    df = stock.quote.history(start=start_date, end=end_date)
    print('SSI Columns:', df.columns)
    print(df.head(2))
except Exception as e:
    print('SSI Error:', e)
