# data_fetcher.py

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from binance.client import Client
from abc import ABC, abstractmethod

class MarketDataFetcher(ABC):
    """
    Abstract base class for fetching market data.
    This defines the interface for any data fetcher, adhering to the Dependency Inversion Principle.
    """
    @abstractmethod
    def fetch_data(self, symbol: str, interval: str, start_date: datetime, end_date: datetime) -> list:
        """Fetches historical market data."""
        pass

class BinanceDataFetcher(MarketDataFetcher):
    """
    A concrete implementation for fetching data from Binance.
    This class has a single responsibility: to get data from the Binance API.
    """
    def __init__(self, api_key: str = "", api_secret: str = ""):
        self._client = Client(api_key, api_secret)

    def fetch_data(self, symbol: str, interval: str, start_date: datetime, end_date: datetime) -> list:
        """
        Fetches historical k-line data from Binance in monthly chunks.
        """
        all_klines = []
        current_start = start_date
        
        print("開始從幣安下載數據...")
        
        while current_start < end_date:
            current_end = current_start + relativedelta(months=1)
            if current_end > end_date:
                current_end = end_date

            print(f"正在獲取 {current_start.strftime('%Y-%m-%d')} 到 {current_end.strftime('%Y-%m-%d')} 的數據...")
            
            try:
                klines = self._client.get_historical_klines(
                    symbol, 
                    interval, 
                    current_start.strftime("%Y-%m-%d %H:%M:%S"),
                    current_end.strftime("%Y-%m-%d %H:%M:%S")
                )
                
                if klines:
                    all_klines.extend(klines)
                else:
                    print(f"在 {current_start.strftime('%Y-%m-%d')} 到 {current_end.strftime('%Y-%m-%d')} 之間沒有找到數據。")

            except Exception as e:
                print(f"獲取數據時發生錯誤: {e}")

            current_start = current_end
            time.sleep(1)  # Sleep to avoid hitting API rate limits

        return all_klines
