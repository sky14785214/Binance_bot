# data_processor.py

import pandas as pd
from typing import List

class DataProcessor:
    """
    This class is responsible for processing the raw market data.
    Its single responsibility is to transform data into a clean, usable format.
    """
    @staticmethod
    def process_klines_to_dataframe(klines: List[list]) -> pd.DataFrame:
        """
        Converts the raw k-line list from the API into a structured pandas DataFrame.
        """
        if not klines:
            return pd.DataFrame()

        df = pd.DataFrame(klines, columns=[
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 
            'Close time', 'Quote asset volume', 'Number of trades', 
            'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'
        ])
        
        # Convert timestamp to datetime objects
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
        
        # Select and return only the columns of interest
        return df[['Open time', 'High', 'Low']].copy()
