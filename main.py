# main.py
import os
import pandas as pd
from datetime import datetime, timedelta
import config
from data_fetcher import BinanceDataFetcher
from data_processor import DataProcessor
from data_saver import NpzDataSaver
from data_loader import DataLoader
from indicators import IndicatorCalculator
from visualizer import Visualizer

def main():
    """
    Main function to orchestrate the data fetching, loading, processing, and analysis.
    """
    output_filename = config.OUTPUT_FILENAME
    
    # 檢查本地數據是否存在或是否需要強制下載
    if not os.path.exists(output_filename) or config.FORCE_DOWNLOAD:
        print("本地數據不存在或已設定強制下載，開始從 API 獲取...")
        # 1. Configuration
        symbol = config.SYMBOL
        interval = config.INTERVAL
        
        # Define date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * config.YEARS_AGO)

        # 2. Initialization of components for download
        fetcher = BinanceDataFetcher()
        processor = DataProcessor()
        saver = NpzDataSaver()

        # 3. Execution flow for download
        raw_klines = fetcher.fetch_data(symbol, interval, start_date, end_date)

        if raw_klines:
            processed_data = processor.process_klines_to_dataframe(raw_klines)
            if not processed_data.empty:
                saver.save(processed_data, output_filename)
                print(f"\n總共獲取了 {len(processed_data)} 分鐘的數據。")
            else:
                print("數據處理後為空，沒有儲存任何內容。")
                return # Exit if no data was saved
        else:
            print("沒有獲取到任何數據。")
            return # Exit if no data was fetched
    
    # 4. 載入數據並計算指標
    df = DataLoader.load_npz_to_dataframe(output_filename)

    if df.empty:
        print("數據載入失敗或為空，程式終止。")
        return

    # 5. 計算技術指標
    df_with_indicators = IndicatorCalculator.add_indicators(df)
    
    # 為了方便觀察，設定 pandas 顯示較多欄位
    pd.set_option('display.max_columns', None)
    
    # 6. 顯示結果
    print("\n包含技術指標的數據 (後5筆):")
    print(df_with_indicators.tail())

    # 7. 可視化數據
    Visualizer.plot_ohlc_with_indicators(df_with_indicators, num_records=300, filename='btc_chart.png')


if __name__ == '__main__':
    main()