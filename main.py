# main.py
import os
import pandas as pd
from datetime import datetime, timedelta
import config
from data_loader import DataLoader
from indicators import IndicatorCalculator
from visualizer import Visualizer
from strategies import MaCrossStrategy, MaCrossStrategyWithTrendFilter
from backtester import Backtester

def generate_filename(strategy_name, timeframe, params, file_type):
    """根據策略名稱、時間框架和參數生成動態檔案名稱。"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    param_str = "_".join(f"{k}{v}" for k, v in params.items())
    return f"{timestamp}_{strategy_name}_{timeframe}_{param_str}.{file_type}"

def main():
    """
    Main function to orchestrate the full pipeline:
    Data Loading -> Indicator Calculation -> Strategy -> Backtesting -> (Visualization)
    """
    output_filename = config.OUTPUT_FILENAME
    
    # 確保輸出目錄存在
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # --- 1. 數據準備 ---
    if not os.path.exists(output_filename):
        print(f"錯誤：數據檔案 '{output_filename}' 不存在。請先執行一次數據下載。")
        return
    
    # 載入 1 分鐘數據
    df_1m = DataLoader.load_npz_to_dataframe(output_filename)
    if df_1m.empty:
        print("數據載入失敗或為空，程式終止。")
        return

    # --- 驗證測試專用：截取部分數據進行快速運行 ---
    TEST_DATA_POINTS = 1000 # 運行最近 1000 筆 1小時數據
    
    # 重採樣到 1 小時週期
    print(f"正在將數據重採樣為 1 小時週期...")
    df_1h = df_1m.resample('1h').apply({
        'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
    }).dropna()
    print("重採樣完成。")

    # 選擇最近的 N 筆數據進行測試
    df_test = df_1h.tail(TEST_DATA_POINTS).copy()
    print(f"將對最近 {TEST_DATA_POINTS} 筆數據 (1小時週期) 進行回測和驗證。")


    # --- 2. 計算技術指標 ---
    df_with_indicators = IndicatorCalculator.add_indicators(df_test)
    
    # --- 3. 產生交易策略信號 ---
    # 使用帶有趨勢過濾的策略
    strategy_params = {'short_window': 10, 'long_window': 30, 'trend_window': 200}
    strategy_name = "MaCrossWithTrend"
    strategy = MaCrossStrategyWithTrendFilter(df_with_indicators, **strategy_params)
    df_with_signals = strategy.generate_signals()

    # --- 4. 執行回測 ---
    backtester = Backtester(df_with_signals, initial_cash=100000, commission=0.001)
    results = backtester.run() # results現在包含詳細的交易日誌

    # --- 5. 儲存回測摘要與圖表 ---
    # 生成動態檔案名稱
    params_for_filename = {
        's': strategy_params['short_window'], 
        'l': strategy_params['long_window'], 
        't': strategy_params['trend_window']
    }
    summary_filename = generate_filename(strategy_name, '1h', params_for_filename, 'csv')
    chart_filename = generate_filename(strategy_name, '1h', params_for_filename, 'png')

    # 儲存回測績效摘要
    summary_path = os.path.join(config.OUTPUT_DIR, summary_filename)
    # 這裡我們只保存Backtester的結果總結
    summary_data = {
        'Initial Cash': [backtester.initial_cash],
        'Final Cash': [backtester.results['total'].iloc[-1]],
        'Total Return (%)': [(backtester.results['total'].iloc[-1] - backtester.initial_cash) / backtester.initial_cash * 100],
        'Buy & Hold Return (%)': [(df_with_indicators['close'].iloc[-1] - df_with_indicators['close'].iloc[0]) / df_with_indicators['close'].iloc[0] * 100],
        'Total Trades': [(backtester.results['trades'] != 0).sum()]
    }
    pd.DataFrame(summary_data).to_csv(summary_path, index=False)
    print(f"回測績效摘要已儲存至 '{summary_path}'")

    # 可視化數據
    chart_path = os.path.join(config.OUTPUT_DIR, chart_filename)
    Visualizer.plot_ohlc_with_indicators(df_with_indicators, num_records=TEST_DATA_POINTS, filepath=chart_path)
    
    print("\n驗證流程完成。")


if __name__ == '__main__':
    main()