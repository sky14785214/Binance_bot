# data_fetcher.py

import os
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from binance.client import Client
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import config

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
    def __init__(self):
        api_key, api_secret = self._load_api_keys()
        self._client = Client(api_key, api_secret)

    def _load_api_keys(self):
        """Loads API keys from .env file."""
        load_dotenv()
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        if not api_key or not api_secret:
            print("警告：找不到 BINANCE_API_KEY 或 BINANCE_API_SECRET。將以無驗證狀態進行。")
            print("請確認您已經將 .env.example 複製為 .env 並填入您的金鑰。")
        return api_key, api_secret

    def fetch_data(self, symbol: str, interval: str, start_date: datetime, end_date: datetime) -> list:
        """
        Fetches historical k-line data from Binance in monthly chunks.
        It can fetch from either Spot or USDT-M Futures market based on config.
        """
        all_klines = []
        current_start = start_date
        
        market_type = config.MARKET_TYPE
        print(f"開始從幣安 {market_type.upper()} 市場下載數據...")

        while current_start < end_date:
            current_end = current_start + relativedelta(months=1)
            if current_end > end_date:
                current_end = end_date

            print(f"正在獲取 {current_start.strftime('%Y-%m-%d')} 到 {current_end.strftime('%Y-%m-%d')} 的數據...")
            
            try:
                if market_type == 'futures':
                    klines = self._client.futures_historical_klines(
                        symbol=symbol,
                        interval=interval,
                        start_str=current_start.strftime("%Y-%m-%d %H:%M:%S"),
                        end_str=current_end.strftime("%Y-%m-%d %H:%M:%S")
                    )
                else: # Default to spot
                    klines = self._client.get_historical_klines(
                        symbol=symbol,
                        interval=interval,
                        start_str=current_start.strftime("%Y-%m-%d %H:%M:%S"),
                        end_str=current_end.strftime("%Y-%m-%d %H:%M:%S")
                    )
                
                if klines:
                    all_klines.extend(klines)
                else:
                    print(f"在 {current_start.strftime('%Y-%m-%d')} 到 {current_end.strftime('%Y-%m-%d')} 之間沒有找到數據。")

            except Exception as e:
                print(f"獲取數據時發生錯誤: {e}")

            current_start = current_end
            # Binance API has rate limits, a short sleep is prudent.
            # For historical data, it's 1200 per minute, so 1s is very safe.
            time.sleep(1)

        return all_klines

