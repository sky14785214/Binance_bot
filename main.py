# main.py

from datetime import datetime, timedelta
import config
from data_fetcher import BinanceDataFetcher
from data_processor import DataProcessor
from data_saver import NpzDataSaver

def main():
    """
    Main function to orchestrate the data fetching, processing, and saving.
    This function demonstrates the Dependency Inversion Principle, as it depends on
    abstractions (not yet explicitly defined via interfaces here, but the separated classes
    serve that purpose) rather than concrete implementations directly in its logic.
    """
    # 1. Configuration
    symbol = config.SYMBOL
    interval = config.INTERVAL
    output_filename = config.OUTPUT_FILENAME
    
    # Define date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * config.YEARS_AGO)

    # 2. Initialization of components
    # We instantiate the concrete classes here. In a larger application,
    # this could be handled by a dependency injection container.
    fetcher = BinanceDataFetcher()
    processor = DataProcessor()
    saver = NpzDataSaver()

    # 3. Execution flow
    # Fetch raw data
    raw_klines = fetcher.fetch_data(symbol, interval, start_date, end_date)

    # Process data
    if raw_klines:
        # The raw klines now include more columns from the futures endpoint
        # Let's update the processor to handle this if needed, for now we assume
        # the first few columns are the same (timestamp, O, H, L, C, V)
        processed_data = processor.process_klines_to_dataframe(raw_klines)
        
        if not processed_data.empty:
            # Save data
            saver.save(processed_data, output_filename)
            print(f"\n總共獲取了 {len(processed_data)} 分鐘的數據。")
        else:
            print("數據處理後為空，沒有儲存任何內容。")
    else:
        print("沒有獲取到任何數據。")

if __name__ == '__main__':
    main()