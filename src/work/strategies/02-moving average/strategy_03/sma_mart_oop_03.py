import datetime
import MetaTrader5 as mt5
import pandas as pd
import plotly.express as px
import numpy as np

from datetime import datetime
from IPython.display import display

# get historical data from MetaTrader5
class Data:
    def __init__(self):
        self.get_bars()
        
    @classmethod
    def get_bars(self, symbol, timeframe, start_pos, num_bars):
        # connect to MetaTrader5 as mt5
        mt5.initialize()

        # Requesting historical data from MetaTrader 5
        bars = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, num_bars)

        # Converting bars we got from MetaTrader5 into dataframe
        candles = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close', 'spread']]

        #  Re-factoring time format into human readable
        candles['time'] = pd.to_datetime(candles['time'], unit='s')

        return candles

tickers = Data.get_bars(symbol = 'EURUSD', 
                                timeframe=mt5.TIMEFRAME_H4, 
                                start_pos=0, 
                                num_bars = 6500)

class BackTester:
    def __init__(self, data, initial_capital=10000):
        self.data = data
        self.capital = initial_capital
        self.positions = pd.DataFrame(columns=['Entry Price', 'Position Size', 'Exit Price', 'Profit'])

    def calculate_MA(self, window):
        return self.data['close'].rolling(window=window).mean()

    def generate_signals(self, ma_fast, ma_slow):
        self.data['MA_Fast'] = self.calculate_MA(ma_fast)
        self.data['MA_Slow'] = self.calculate_MA(ma_slow)
        self.data['Signal'] = 0
        self.data.loc[self.data['MA_Fast'] > self.data['MA_Slow'], 'Signal'] = 1  # Buy
        self.data.loc[self.data['MA_Fast'] < self.data['MA_Slow'], 'Signal'] = -1  # Sell

    def execute_trades(self, take_profit, stop_loss, martingale=True):
        position = 0
        multiplier = 1  # Martingale multiplier
        for i in range(len(self.data)):
            signal = self.data.loc[i, 'Signal']
            price = self.data.loc[i, 'close']

            if signal == 1 and position == 0:  # Buy
                position = self.capital / price * multiplier
                self.capital -= position * price
                self.positions.loc[i] = [price, position, None, None]
            elif signal == -1 and position > 0:  # Sell
                exit_price = price
                profit = (exit_price - self.positions.loc[i, 'Entry Price']) * position
                self.capital += exit_price * position + profit
                self.positions.loc[i, 'Exit Price'] = exit_price
                self.positions.loc[i, 'Profit'] = profit
                position = 0
                multiplier = 1
            elif signal == -1 and position < 0:  # Cover short
                exit_price = price
                profit = (self.positions.loc[i, 'Entry Price'] - exit_price) * position
                self.capital += exit_price * position + profit
                self.positions.loc[i, 'Exit Price'] = exit_price
                self.positions.loc[i, 'Profit'] = profit
                position = 0
                multiplier = 1

            # Trail stop loss
            if position != 0:
                highest_profit = max(self.positions.loc[i:, 'Profit'])
                if highest_profit >= take_profit:
                    self.execute_trades(take_profit, stop_loss, martingale=False)  # Exit at take profit
                elif highest_profit >= stop_loss:
                    stop_loss = highest_profit  # Adjust stop loss

            # Martingale (if enabled)
            if martingale and self.positions.iloc[-1, -1] < 0:
                multiplier *= 2

    def calculate_performance(self):
        total_profit = self.positions['Profit'].sum()
        ROI = total_profit / self.capital * 100
        return pd.Series({'Total Profit': total_profit, 'ROI': ROI})

# Load your data here
data = tickers

# Nested loop for testing parameters
results = pd.DataFrame()
for ma_fast in [10, 20, 50]:
    for ma_slow in [20, 50, 100]:
        for take_profit in [0.05, 0.1]:
            for stop_loss in [0.02, 0.03]:
                backTester = BackTester(data.copy())
                backTester.generate_signals(ma_fast, ma_slow)
                backTester.execute_trades(take_profit, stop_loss)
                performance = backTester.calculate_performance()
                print(performance)