# visualizer.py
import pandas as pd
import mplfinance as mpf

class Visualizer:
    """
    專門用於數據可視化的類別。
    """
    @staticmethod
    def plot_ohlc_with_indicators(df: pd.DataFrame, num_records: int = 200, filename: str = 'chart.png'):
        """
        繪製包含技術指標的K線圖，並將其儲存為檔案。

        :param df: 包含 OHLC 和指標欄位的 DataFrame。
        :param num_records: 要繪製的最新數據點數量。
        :param filename: 儲存圖表的檔案名稱。
        """
        if df.empty or len(df) < num_records:
            print("數據不足，無法繪製圖表。")
            return

        print(f"開始繪製最近 {num_records} 筆數據的圖表...")

        # 取得最新的數據子集
        plot_df = df.tail(num_records).copy()
        
        # mplfinance 需要以 datetime 作為索引
        if 'Open time' in plot_df.columns:
            plot_df.set_index('Open time', inplace=True)

        # 定義要額外繪製的指標面板
        # RSI 和 KD 指標通常繪製在主圖下方
        added_plots = [
            # RSI 指標
            mpf.make_addplot(plot_df['RSI_14'], panel=1, color='orange', title='RSI'),
            # KD 指標 (K線 和 D線)
            mpf.make_addplot(plot_df['STOCHk_14_3_3'], panel=2, color='blue', title='KD'),
            mpf.make_addplot(plot_df['STOCHd_14_3_3'], panel=2, color='red')
        ]
        
        # 繪製 K線圖，並加入移動平均線(mav)和額外面板
        try:
            mpf.plot(
                plot_df,
                type='candle',
                style='yahoo',
                title='BTC/USDT Futures with Indicators',
                ylabel='Price ($)',
                mav=(10, 30),  # 直接從欄位繪製 SMA_10 和 SMA_30
                addplot=added_plots,
                panel_ratios=(3, 1, 1), # 主圖、RSI、KD 的面板比例
                volume=True,  # 在主圖下方顯示成交量
                ylabel_lower='Volume',
                savefig=filename  # 儲存圖表到檔案
            )
            print(f"圖表已成功儲存至 '{filename}'")
        except Exception as e:
            print(f"繪製圖表時發生錯誤: {e}")

