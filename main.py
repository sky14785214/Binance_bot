# main.py
import os
import pandas as pd
from datetime import datetime, timedelta
import config
from data_loader import DataLoader
from indicators import IndicatorCalculator
from visualizer import Visualizer
from strategies import MaCrossStrategy
from backtester import Backtester

def resample_data(df: pd.DataFrame, timeframe: str = '1H') -> pd.DataFrame:
    """
    將 DataFrame 重採樣到指定的時間週期。
    """
    print(f"正在將數據重採樣為 {timeframe} 週期...")
    
    resample_rules = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    
    resampled_df = df.resample(timeframe).apply(resample_rules)
    resampled_df.dropna(inplace=True) # 移除沒有數據的間隔
    
    print("重採樣完成。")
    return resampled_df

def main():
    """
    Main function to orchestrate the full pipeline:
    Data Loading -> Resampling -> Indicator Calculation -> Strategy -> Backtesting
    """
    output_filename = config.OUTPUT_FILENAME
    
    # --- 1. 數據準備 ---
    if not os.path.exists(output_filename):
        print(f"錯誤：數據檔案 '{output_filename}' 不存在。請先執行一次數據下載。")
        return
    
    # 載入 1 分鐘數據
    df_1m = DataLoader.load_npz_to_dataframe(output_filename)
    if df_1m.empty:
        print("數據載入失敗或為空，程式終止。")
        return

    # --- 2. 重採樣到 1 小時週期 ---
    df_1h = resample_data(df_1m, '1h')

    # --- 3. 計算技術指標 ---
    df_with_indicators = IndicatorCalculator.add_indicators(df_1h)
    
    # --- 4. 產生交易策略信號 ---
    strategy = MaCrossStrategy(df_with_indicators, short_window=10, long_window=30)
    df_with_signals = strategy.generate_signals()

    # --- 5. 執行回測 ---
    backtester = Backtester(df_with_signals, initial_cash=100000, commission=0.001)
    results = backtester.run()
    
    print("\n回測流程完成。")


if __name__ == '__main__':
    main()