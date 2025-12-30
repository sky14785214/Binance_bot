# config.py

from binance.client import Client

# 交易對
SYMBOL = 'BTCUSDT'
# K線時間間隔
INTERVAL = Client.KLINE_INTERVAL_1MINUTE
# 輸出檔案名稱
OUTPUT_FILENAME = 'btc_price_1_year.csv'
# 資料起始時間（幾年前）
YEARS_AGO = 1
