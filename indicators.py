# indicators.py
import pandas as pd
import pandas_ta as ta

class IndicatorCalculator:
    """
    專門用於計算各種技術指標的類別。
    """
    @staticmethod
    def add_indicators(df: pd.DataFrame, sma_windows: list = None) -> pd.DataFrame:
        """
        在給定的 DataFrame 中加入 MA, RSI, 和 KD 技術指標。

        :param df: 包含 'high', 'low', 'close' 欄位的 DataFrame。
        :param sma_windows: 一個包含要計算的SMA週期的列表，例如 [10, 30, 200]。
        :return: 附加了指標欄位的 DataFrame。
        """
        print(f"開始計算技術指標...")
        
        # 計算移動平均線 (MA)
        if sma_windows:
            print(f"  計算移動平均線 (SMA): {sma_windows}")
            for window in sma_windows:
                df.ta.sma(length=window, append=True)

        # 計算相對強弱指數 (RSI)
        print(f"  計算相對強弱指數 (RSI): 14")
        df.ta.rsi(length=14, append=True)

        # 計算KD指標 (Stochastic Oscillator)
        print(f"  計算KD指標 (Stoch): k=14, d=3, smooth_k=3")
        df.ta.stoch(k=14, d=3, smooth_k=3, append=True)

        # 處理計算指標後產生的 NaN 值
        df.dropna(inplace=True)
        print("技術指標計算完成，並已移除包含NaN的行。")
        return df
