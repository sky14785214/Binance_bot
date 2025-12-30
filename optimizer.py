# optimizer.py
import pandas as pd
import os
import itertools

from data_loader import DataLoader
from indicators import IndicatorCalculator
from strategies import MaCrossStrategyWithTrendFilter
from backtester import Backtester
import config

def run_optimizer():
    """
    執行策略優化，測試多組參數。
    """
    # --- 1. 參數網格定義 ---
    param_grid = {
        'timeframe': ['30m', '1h', '4h'],
        'short_window': [10, 20],
        'long_window': [40, 60],
        'trend_window': [150, 200]
    }
    # 從網格中生成所有參數組合
    keys, values = zip(*param_grid.items())
    experiments = [dict(zip(keys, v)) for v in itertools.product(*values)]

    print(f"將要執行 {len(experiments)} 次回測實驗...")

    # --- 2. 數據載入 ---
    df_1m = DataLoader.load_npz_to_dataframe(config.OUTPUT_FILENAME)
    if df_1m.empty:
        print("數據載入失敗，優化器終止。")
        return

    all_results = []
    
    # --- 3. 遍歷執行所有實驗 ---
    for i, params in enumerate(experiments):
        print(f"\n--- 實驗 {i+1}/{len(experiments)}: {params} ---")
        
        try:
            # 3.1 重採樣數據
            tf = params['timeframe']
            resample_rules = {'open':'first', 'high':'max', 'low':'min', 'close':'last', 'volume':'sum'}
            df_resampled = df_1m.resample(tf).apply(resample_rules).dropna()

            # 3.2 計算所需指標
            sma_windows = [params['short_window'], params['long_window'], params['trend_window']]
            df_with_indicators = IndicatorCalculator.add_indicators(df_resampled, sma_windows=sma_windows)
            
            if len(df_with_indicators) < params['trend_window']:
                print("數據不足以進行此參數的回測，跳過。")
                continue

            # 3.3 產生信號
            strategy = MaCrossStrategyWithTrendFilter(
                df_with_indicators, 
                short_window=params['short_window'], 
                long_window=params['long_window'], 
                trend_window=params['trend_window']
            )
            df_with_signals = strategy.generate_signals()

            # 3.4 執行回測
            backtester = Backtester(df_with_signals, initial_cash=100000, commission=0.001)
            _, summary = backtester.run()

            # 3.5 記錄結果
            # 將 params 字典和 summary 字典合併
            full_summary = {**params, **summary}
            all_results.append(full_summary)

        except Exception as e:
            print(f"實驗 {params} 發生錯誤: {e}")

    # --- 4. 處理與儲存結果 ---
    if not all_results:
        print("沒有任何實驗成功，無法生成報告。")
        return
        
    results_df = pd.DataFrame(all_results)
    
    # 轉換百分比欄位為數值以便排序
    results_df['Total Return (%)'] = pd.to_numeric(results_df['Total Return (%)'])
    
    # 根據總報酬率排序
    results_df = results_df.sort_values(by='Total Return (%)', ascending=False)
    
    # 儲存所有結果到CSV
    summary_filepath = os.path.join(config.OUTPUT_DIR, 'backtest_results_summary.csv')
    results_df.to_csv(summary_filepath, index=False)
    print(f"\n所有回測結果已儲存至: {summary_filepath}")

    # --- 5. 打印最佳結果 ---
    print("\n--- 最佳 5 個策略 ---")
    print(results_df.head(5).to_string())
    
    # --- 6. 繪製總結圖表 ---
    plot_optimizer_results(summary_filepath)


def plot_optimizer_results(csv_filepath):
    """
    從CSV檔案讀取優化結果並繪製總結圖表。
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.ticker import MaxNLocator
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式後端，避免在服務器上出錯
        plt.style.use('seaborn-v0_8-darkgrid') # 使用推薦的樣式

        print(f"開始從 {csv_filepath} 繪製總結圖表...")
        
        df = pd.read_csv(csv_filepath)
        
        # 確保數據是從低到高排序，這樣在 hbar 中最高的回報會在頂部
        df = df.sort_values(by='Total Return (%)', ascending=True)

        # 創建一個簡潔的標籤給Y軸
        labels = df.apply(
            lambda row: f"TF:{row['timeframe']} S:{row['short_window']} L:{row['long_window']} T:{row['trend_window']}",
            axis=1
        )
        
        plt.figure(figsize=(12, 8))
        
        # 創建水平條形圖
        bars = plt.barh(labels, df['Total Return (%)'], color='skyblue')
        
        # 在條形圖上添加數值標籤
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width + 0.1 if width > 0 else 0.1
            plt.text(label_x_pos, bar.get_y() + bar.get_height()/2., f'{width:.2f}%', 
                     va='center', ha='left')

        plt.title('Optimization Results: Total Return by Strategy Parameters', fontsize=16)
        plt.xlabel('Total Return (%)', fontsize=12)
        plt.ylabel('Strategy Parameters (Timeframe, Short, Long, Trend)', fontsize=12)
        
        # 讓Y軸標籤更清晰
        plt.tick_params(axis='y', labelsize=8)
        plt.tight_layout()
        
        # 確保X軸是整數
        ax = plt.gca()
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        # 儲存圖表
        chart_filepath = csv_filepath.replace('.csv', '_summary.png')
        plt.savefig(chart_filepath, dpi=300)
        
        print(f"總結圖表已儲存至: {chart_filepath}")

    except Exception as e:
        print(f"繪製總結圖表時發生錯誤: {e}")
