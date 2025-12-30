# strategies.py
import pandas as pd
from abc import ABC, abstractmethod

class Strategy(ABC):
    """
    策略的抽象基底類別 (ABC)。
    所有具體的策略都應該繼承自這個類別並實現 generate_signals 方法。
    """
    def __init__(self, data: pd.DataFrame):
        self.df = data

    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """
        根據策略邏輯產生交易信號。
        :return: 包含 'signal' 欄位的 DataFrame。
                 'signal' 的值可以是 1 (買入), -1 (賣出), 0 (無動作)。
        """
        pass

class MaCrossStrategy(Strategy):
    """
    移動平均線 (MA) 交叉策略。
    - 當短期 MA 向上穿越長期 MA 時，買入。
    - 當短期 MA 向下穿越長期 MA 時，賣出。
    """
    def __init__(self, data: pd.DataFrame, short_window: int = 10, long_window: int = 30):
        super().__init__(data)
        self.short_window_col = f'SMA_{short_window}'
        self.long_window_col = f'SMA_{long_window}'

    def generate_signals(self) -> pd.DataFrame:
        """
        產生 MA 交叉策略的交易信號。
        """
        print("正在產生 MA 交叉策略信號...")
        
        if self.short_window_col not in self.df.columns or self.long_window_col not in self.df.columns:
            raise ValueError(f"數據中缺少 MA 欄位: {self.short_window_col} 或 {self.long_window_col}")

        # 建立一個新的 'signal' 欄位，預設為 0 (無動作)
        self.df['signal'] = 0

        # 當短期MA > 長期MA，設定為 1 (潛在買入狀態)
        self.df['position'] = 0
        self.df.loc[self.df[self.short_window_col] > self.df[self.long_window_col], 'position'] = 1

        # 計算 position 的變化，前一天是0，當天是1，代表黃金交叉，產生買入信號 (1)
        # 前一天是1，當天是0，代表死亡交叉，產生賣出信號 (-1)
        self.df['signal'] = self.df['position'].diff()
        
        # 移除 position 輔助欄位
        self.df.drop(columns=['position'], inplace=True)
        
        print("信號產生完畢。")
        return self.df

