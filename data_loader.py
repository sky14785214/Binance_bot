# data_loader.py
import numpy as np
import pandas as pd
import os

class DataLoader:
    """
    專門用於從檔案載入數據的類別。
    """
    @staticmethod
    def load_npz_to_dataframe(file_path: str) -> pd.DataFrame:
        """
        從 .npz 檔案載入數據並轉換為 Pandas DataFrame。
        
        :param file_path: .npz 檔案的路徑。
        :return: 包含市場數據的 DataFrame。
        """
        if not os.path.exists(file_path):
            print(f"錯誤：找不到數據檔案 '{file_path}'。")
            return pd.DataFrame()
            
        print(f"從 '{file_path}' 載入數據...")
        try:
            with np.load(file_path) as data:
                # 將 timestamp 轉回 datetime
                df = pd.DataFrame({
                    'Open time': pd.to_datetime(data['open_time'], unit='s')
                })

                # 載入所有其他 array
                for key in data.files:
                    if key != 'open_time':
                        # 將 'high' -> 'High', 'open_time' -> 'Open time'
                        col_name = ' '.join(word.capitalize() for word in key.split('_'))
                        df[col_name] = data[key]
                
                # 為了與 pandas-ta 兼容，需要標準的 OHLCV 欄位名稱
                df.rename(columns={
                    'High': 'high',
                    'Low': 'low',
                    'Open': 'open',
                    'Close': 'close',
                    'Volume': 'volume'
                }, inplace=True)

            print("數據載入完成。")
            return df
        except Exception as e:
            print(f"載入 .npz 檔案時發生錯誤: {e}")
            return pd.DataFrame()

