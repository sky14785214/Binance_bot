# visualizer.py
import pandas as pd
import mplfinance as mpf
import os

class Visualizer:
    """
    專門用於數據可視化的類別。
    """
    @staticmethod
    def plot_ohlc_with_indicators(df: pd.DataFrame, num_records: int = 200, filepath: str = 'chart.png'):
        """
        繪製包含技術指標的K線圖，並將其儲存為檔案。

        :param df: 包含 OHLC 和指標欄位的 DataFrame。
        :param num_records: 要繪製的最新數據點數量。
        :param filepath: 儲存圖表的完整檔案路徑 (包含目錄和檔案名稱)。
        """
        if df.empty or len(df) < num_records:
            print("數據不足，無法繪製圖表。")
            return

        print(f"開始繪製最近 {num_records} 筆數據的圖表並儲存至 '{filepath}'...")

        # 取得最新的數據子集
        plot_df = df.tail(num_records).copy()
        
        # mplfinance 需要以 datetime 作為索引
        if 'Open time' in plot_df.columns:
            plot_df.set_index('Open time', inplace=True)

        # 定義要額外繪製的指標面板
        added_plots = [
            mpf.make_addplot(plot_df['RSI_14'], panel=1, color='orange', title='RSI'),
            mpf.make_addplot(plot_df['STOCHk_14_3_3'], panel=2, color='blue', title='KD %K'), # 修正title
            mpf.make_addplot(plot_df['STOCHd_14_3_3'], panel=2, color='red', title='KD %D')  # 修正title
        ]
        
        # 繪製 K線圖，並加入移動平均線(mav)和額外面板
        try:
            mpf.plot(
                plot_df,
                type='candle',
                style='yahoo',
                title=f"BTC/USDT Futures - {os.path.basename(filepath).split('.')[0]}", # 使用動態標題
                ylabel='Price ($)',
                mav=(10, 30, 200),  # 直接從欄位繪製 SMA_10, SMA_30, SMA_200
                addplot=added_plots,
                panel_ratios=(3, 1, 1), # 主圖、RSI、KD 的面板比例
                volume=True,  # 在主圖下方顯示成交量
                ylabel_lower='Volume',
                savefig=dict(fname=filepath, dpi=300, bbox_inches="tight")  # 儲存圖表到檔案，增加DPI和邊界設置
            )
            print(f"圖表已成功儲存至 '{filepath}'")
        except Exception as e:
            print(f"繪製圖表時發生錯誤: {e}")

