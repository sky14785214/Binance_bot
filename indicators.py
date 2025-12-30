# indicators.py
import pandas as pd
import pandas_ta as ta

class IndicatorCalculator:
    """
    專門用於計算各種技術指標的類別。
    """
    @staticmethod
    def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        在給定的 DataFrame 中加入 MA, RSI, 和 KD 技術指標。

        :param df: 包含 'high', 'low', 'close' 欄位的 DataFrame。
        :return: 附加了指標欄位的 DataFrame。
        """
        print("開始計算技術指標 (MA, RSI, KD)...")
        
        # 計算移動平均線 (MA)
        df.ta.sma(length=10, append=True)  # 短期
        df.ta.sma(length=30, append=True)  # 中期
        df.ta.sma(length=200, append=True) # 長期趨勢濾網

        # 計算相對強弱指數 (RSI)
        df.ta.rsi(length=14, append=True) # 14日RSI

        # 計算KD指標 (Stochastic Oscillator)
        # pandas-ta 的 stoch 會產生 STOCHk_14_3_3 和 STOCHd_14_3_3
        df.ta.stoch(k=14, d=3, smooth_k=3, append=True)

        print("技術指標計算完成。")
        return df
