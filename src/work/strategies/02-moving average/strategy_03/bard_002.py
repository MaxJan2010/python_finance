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

    def calculate_ma(self, ma_fast, ma_slow):
        self.data['ma_fast'] = self.data['close'].rolling(window=ma_fast).mean()
        self.data['ma_slow'] = self.data['close'].rolling(window=ma_slow).mean()

    def generate_signals(self):
        self.data['signal'] = 0
        self.data.loc[(self.data['ma_fast'] > self.data['ma_slow']) & (self.data['signal'].shift(1) != 1), 'signal'] = 1  # Buy
        self.data.loc[(self.data['ma_fast'] < self.data['ma_slow']) & (self.data['signal'].shift(1) != -1), 'signal'] = -1  # Sell

    # def calculate_extremes(self):
    #     self.data = self.generate_signals()
    #     self.data['max_price'] = self.data.groupby('signal')['high'].transform('max')
    #     self.data['min_price'] = self.data.groupby('signal')['low'].transform('min')


    def backtest(self, take_profit, stop_loss, ma_fast, ma_slow):
        self.calculate_ma(ma_fast, ma_slow)
        # self.calculate_extremes()

        # Perform trading logic, calculate P&L, and store results in a DataFrame

data = pd.read_csv("feeds.csv")
results = pd.DataFrame()
for take_profit in [x * 0.01 for x in range(10, 21)]:
    for stop_loss in [x * 0.01 for x in range(5, 16)]:
        for ma_fast in range(10, 21):
            for ma_slow in range(20, 41):
                if ma_fast < ma_slow:
                    tester = BackTester(data.copy())  # Use a copy of data for each iteration
                    result = tester.backtest(take_profit, stop_loss, ma_fast, ma_slow)
                    # result['take_profit'] = take_profit
                    # result['stop_loss'] = stop_loss
                    result['ma_fast'] = ma_fast
                    result['ma_slow'] = ma_slow
                    results = results.append(result, ignore_index=True)

# Calculate final performance metrics
results['ROI'] = results['total_profit'] / results['initial_capital'] * 100

print(results)
