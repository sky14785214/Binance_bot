# config.py

from binance.client import Client

# 強制重新下載數據，即使檔案已存在
FORCE_DOWNLOAD = False

# 市場類型: 'spot' 或 'futures'
MARKET_TYPE = 'futures'

# 交易對
SYMBOL = 'BTCUSDT'
# K線時間間隔
INTERVAL = Client.KLINE_INTERVAL_1MINUTE
# 輸出檔案名稱
OUTPUT_FILENAME = 'btc_futures_price_3_years.npz'
# 資料起始時間（幾年前）
YEARS_AGO = 3
