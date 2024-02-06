import datetime
import MetaTrader5 as mt5
import pandas as pd
import plotly.express as px
import numpy as np

from datetime import datetime
from IPython.display import display

import pandas as pd

class BackTester:
    def __init__(self, data):
        self.data = data
        self.positions = []  # List to track open positions

    def calculate_moving_averages(self, ma_fast, ma_slow):
        self.data['ma_fast'] = self.data['close'].rolling(window=ma_fast).mean()
        self.data['ma_slow'] = self.data['close'].rolling(window=ma_slow).mean()

    def generate_signals(self):
        self.data['signal'] = 0
        self.data.loc[self.data['ma_fast'] > self.data['ma_slow'], 'signal'] = 1  # Buy signal
        self.data.loc[self.data['ma_fast'] < self.data['ma_slow'], 'signal'] = -1  # Sell signal

    def calculate_position_highs_lows(self):
        for i in range(len(self.data)):
            if self.data.loc[i, 'signal'] == 1:  # New buy position
                self.positions.append({'entry_price': self.data.loc[i, 'close'], 'high': self.data.loc[i, 'close'], 'low': self.data.loc[i, 'close']})
            elif self.data.loc[i, 'signal'] == -1 and self.positions:  # Close sell position
                current_position = self.positions.pop()
                current_position['high'] = max(self.data.loc[i:, 'high'])
                current_position['low'] = min(self.data.loc[i:, 'low'])


    def martingale_logic(self, loss_multiplier):
        pass  # Implement your Martingale logic here

    def apply_take_profit_stop_loss(self, take_profit, stop_loss):
        pass  # Implement your take profit and stop loss logic here

    def run_backtest(self, ma_fast_values, ma_slow_values, take_profit_values, stop_loss_values):
        results_df = pd.DataFrame()
        for ma_fast in ma_fast_values:
            for ma_slow in ma_slow_values:
                # for take_profit in take_profit_values:
                #     for stop_loss in stop_loss_values:
                        self.calculate_moving_averages(ma_fast, ma_slow)
                        self.generate_signals()
                        self.calculate_position_highs_lows()
                        # self.martingale_logic(2)  # Example Martingale factor
                        # self.apply_take_profit_stop_loss(take_profit, stop_loss)
                        # Calculate performance metrics
                        total_profit = sum(position['high'] - position['entry_price'] for position in self.positions)
                        roi = total_profit / initial_capital * 100
                        # Append results to dataframe
                        results_df = results_df.append({
                            'ma_fast': ma_fast,
                            'ma_slow': ma_slow,
                            # 'take_profit': take_profit,
                            # 'stop_loss': stop_loss,
                            'total_profit': total_profit,
                            'roi': roi
                        }, ignore_index=True)
        return results_df

# Example usage
data = pd.read_csv('feeds.csv')  # Load your data
initial_capital = 10000
tester = BackTester(data)
results = tester.run_backtest([5, 10], [20, 30], [0.05, 0.1], [0.02, 0.03])
print(results)
