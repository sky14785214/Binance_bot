# data_saver.py

import pandas as pd
from abc import ABC, abstractmethod

class DataSaver(ABC):
    """
    Abstract base class for saving data.
    This follows the Open/Closed Principle. We can create new savers (e.g., JsonSaver, ParquetSaver)
    by inheriting from this class without modifying existing code.
    """
    @abstractmethod
    def save(self, data: pd.DataFrame, file_path: str):
        """Saves the given DataFrame to a file."""
        pass

class CsvDataSaver(DataSaver):
    """
    A concrete implementation for saving data to a CSV file.
    """
    def save(self, data: pd.DataFrame, file_path: str):
        """
        Saves the DataFrame to a CSV file with UTF-8 encoding.
        """
        try:
            data.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"數據已成功儲存至 '{file_path}'")
        except Exception as e:
            print(f"儲存檔案時發生錯誤: {e}")
