# backtester.py
import pandas as pd
import numpy as np

class Backtester:
    """
    一個簡單的向量化回測引擎。
    """
    def __init__(self, data: pd.DataFrame, initial_cash: float = 100000.0, commission: float = 0.001):
        """
        :param data: 包含 OHLCV 和 'signal' 欄位的 DataFrame。
        :param initial_cash: 初始資金。
        :param commission: 交易手續費率 (例如 0.001 代表 0.1%)。
        """
        self.data = data
        self.initial_cash = initial_cash
        self.commission = commission
        self.results = None

    def run(self):
        """
        執行向量化回測。
        """
        print("開始執行向量化回測...")
        
        if 'signal' not in self.data.columns:
            raise ValueError("數據中缺少 'signal' 欄位。請先產生信號。 இருப்பதாக")
            
        # --- 模擬交易和投資組合 ---
        # `positions` 代表在每個時間點，我們希望持有的部位狀態 (1: 持有多頭, 0: 空手)
        # 買入信號(1)後，我們希望持有部位；賣出信號(-1)後，我們希望空手。
        # ffill() 會用前一個非空值填充NaN，模擬持有狀態的持續
        positions = self.data['signal'].replace(-1, 0).ffill().fillna(0)
        
        # `trades` 代表實際的交易動作 (1: 買入, -1: 賣出, 0: 無動作)
        trades = positions.diff().fillna(0)

        # --- 計算投資組合價值 ---
        # 假設每次交易都用掉全部現金買入，或賣出全部部位
        # 建立一個 cash 數組
        cash = pd.Series(index=self.data.index, dtype=float).fillna(0)
        cash.iloc[0] = self.initial_cash
        
        # 建立一個 holdings 數組 (持有資產的價值)
        holdings = pd.Series(index=self.data.index, dtype=float).fillna(0)

        # 遍歷所有時間點來模擬現金和持倉變化
        # (注意：這部分為了簡化用了迴圈，但在純向量化中可以進一步優化)
        for i in range(1, len(self.data)):
            # 先繼承前一天的狀態
            cash.iloc[i] = cash.iloc[i-1]
            holdings.iloc[i] = holdings.iloc[i-1] * (self.data['close'].iloc[i] / self.data['close'].iloc[i-1])

            if trades.iloc[i] == 1:  # 買入
                buy_price = self.data['close'].iloc[i]
                quantity = (cash.iloc[i] * (1 - self.commission)) / buy_price
                holdings.iloc[i] = quantity * buy_price
                cash.iloc[i] = 0
            elif trades.iloc[i] == -1:  # 賣出
                sell_price = self.data['close'].iloc[i]
                cash.iloc[i] += holdings.iloc[i] * (1 - self.commission)
                holdings.iloc[i] = 0

        # 計算總資產
        portfolio_value = cash + holdings
        
        # --- 儲存結果 ---
        self.results = pd.DataFrame({
            'cash': cash,
            'holdings': holdings,
            'total': portfolio_value,
            'trades': trades
        })
        
        print("回測執行完畢。")
        self._print_summary(portfolio_value)
        
        return self.results

    def _print_summary(self, portfolio_value: pd.Series):
        """
        打印回測的績效摘要。
        """
        print("\n--- 回測績效摘要 ---")
        
        start_value = self.initial_cash
        end_value = portfolio_value.iloc[-1]
        total_return = (end_value - start_value) / start_value * 100
        
        buy_and_hold_return = (self.data['close'].iloc[-1] - self.data['close'].iloc[0]) / self.data['close'].iloc[0] * 100
        
        num_trades = (self.results['trades'] != 0).sum()

        print(f"初始資產: {start_value:,.2f}")
        print(f"最終資產: {end_value:,.2f}")
        print(f"總報酬率: {total_return:.2f}%")
        print(f"買入並持有策略報酬率: {buy_and_hold_return:.2f}%")
        print(f"總交易次數: {num_trades}")
        
        if total_return > buy_and_hold_return:
            print("策略表現優於買入並持有。 இருப்பதாக")
        else:
            print("策略表現劣於買入並持有。 இருப்பதாக")
