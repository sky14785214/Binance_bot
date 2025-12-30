# data_saver.py

import pandas as pd
from abc import ABC, abstractmethod
import numpy as np

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

class NpzDataSaver(DataSaver):
    """
    A concrete implementation for saving data to a compressed NPZ file.
    """
    def save(self, data: pd.DataFrame, file_path: str):
        """
        Converts the DataFrame to a dictionary of NumPy arrays and saves it 
        as a compressed .npz file.
        """
        try:
            # Convert timestamp to unix epoch seconds for efficient storage
            data_to_save = {
                'open_time': data['Open time'].astype('int64') // 10**9
            }
            # Add other columns
            for col in data.columns:
                if col != 'Open time':
                    data_to_save[col.lower().replace(' ', '_')] = data[col].to_numpy(dtype=np.float64)

            np.savez_compressed(file_path, **data_to_save)
            print(f"數據已成功儲存至 '{file_path}'")
        except Exception as e:
            print(f"儲存為 .npz 檔案時發生錯誤: {e}")
