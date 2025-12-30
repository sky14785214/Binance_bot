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

class MaCrossStrategyWithTrendFilter(Strategy):
    """
    帶有長期趨勢過濾的移動平均線交叉策略。
    - 買入條件:
        1. 短期 MA > 長期 MA (黃金交叉)
        2. 短期 MA > 趨勢過濾 MA (處於上升趨勢中)
    - 賣出條件:
        1. 短期 MA < 長期 MA (死亡交叉)
    """
    def __init__(self, data: pd.DataFrame, short_window: int = 10, long_window: int = 30, trend_window: int = 200):
        super().__init__(data)
        self.short_window_col = f'SMA_{short_window}'
        self.long_window_col = f'SMA_{long_window}'
        self.trend_window_col = f'SMA_{trend_window}'

    def generate_signals(self) -> pd.DataFrame:
        """
        產生帶有趨勢過濾的 MA 交叉策略信號。
        """
        print("正在產生帶趨勢過濾的 MA 交叉策略信號...")
        
        required_cols = [self.short_window_col, self.long_window_col, self.trend_window_col]
        if not all(col in self.df.columns for col in required_cols):
            raise ValueError(f"數據中缺少 MA 欄位: {required_cols}")

        self.df['signal'] = 0
        
        # 條件 1: 短期MA > 中期MA
        condition1 = self.df[self.short_window_col] > self.df[self.long_window_col]
        # 條件 2: 中期MA > 長期趨勢MA
        condition2 = self.df[self.long_window_col] > self.df[self.trend_window_col]
        
        # 當兩個條件都滿足時，我們希望處於持有多頭部位 (position = 1)
        self.df['position'] = 0
        self.df.loc[condition1 & condition2, 'position'] = 1

        # 計算 position 的變化來決定實際的買賣點
        self.df['signal'] = self.df['position'].diff()
        
        self.df.drop(columns=['position'], inplace=True)
        
        print("帶趨勢過濾的信號產生完畢。")
        return self.df

