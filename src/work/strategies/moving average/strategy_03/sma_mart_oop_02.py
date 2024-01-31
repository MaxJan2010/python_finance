import datetime
import MetaTrader5 as mt5
import pandas as pd
import plotly.express as px
import numpy as np

from datetime import datetime
from IPython.display import display


# pd.set_option('display.max_colwidth', None)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

# connect to MetaTrader5 as mt5
mt5.initialize()

class Data:
    def __init__(self):
        self.get_bars()
        
    @classmethod
    def get_bars(self, symbol, timeframe, start_pos, num_bars):
        # Requesting historical data from MetaTrader 5
        bars = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, num_bars)

        # Converting bars we got from MetaTrader5 into dataframe
        candles = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close', 'spread']]

        #  Re-factoring time format into human readable
        candles['time'] = pd.to_datetime(candles['time'], unit='s')

        return candles


class BackTester:
    def __init__(self, data, initial_capital, commission):
        self.data = data
        self.capital = initial_capital
        self.commission = commission
        self.positions = pd.DataFrame(columns=['EntryPrice', 'Quantity', 'TP', 'SL'])

    def calculate_MA(self, window):
        return self.data['close'].rolling(window=window).mean()

    def generate_signals(self, ma_fast, ma_slow):
        self.data['Signal'] = 0
        self.data.loc[self.calculate_MA(ma_fast) > self.calculate_MA(ma_slow), 'Signal'] = 1  # Buy
        self.data.loc[self.calculate_MA(ma_fast) < self.calculate_MA(ma_slow), 'Signal'] = -1  # Sell

    def execute_trades(self, signal, price, tp, sl):
        if signal == 1 and self.positions.any():  # Buy
            quantity = int(self.capital / price)
            self.positions = pd.DataFrame({'EntryPrice': price, 'Quantity': quantity, 'TP': tp, 'SL': sl}, index=[0])
        elif signal == -1 and not len(self.positions)<0:  # Sell
            exit_price = price - self.commission
            profit = (exit_price - self.positions['EntryPrice'].values[0]) * self.positions['Quantity'].values[0]
            self.capital += profit - self.commission
            self.positions = pd.DataFrame()  # Clear positions

    def martingale(self, price, tp, sl):
        if len(self.positions)>0:
            if price >= self.positions['TP'].values[0]:
                exit_price = tp - self.commission
                profit = (exit_price - self.positions['EntryPrice'].values[0]) * self.positions['Quantity'].values[0]
                self.capital += profit - self.commission
                self.positions = pd.DataFrame()
            elif price <= self.positions['SL'].values[0]:
                exit_price = sl + self.commission
                profit = (exit_price - self.positions['EntryPrice'].values[0]) * self.positions['Quantity'].values[0]
                self.capital += profit - self.commission
                self.positions = pd.DataFrame()
                self.martingale(price, tp * 2, sl * 2)  # Double TP and SL for next trade

    def backtest(self):
        results = pd.DataFrame()
        for ma_fast in [10, 20, 50]:
            for ma_slow in [20, 50, 100]:
                for tp in [0.05, 0.1]:
                    for sl in [0.03, 0.05]:
                        self.capital = 10000  # Reset capital for each loop
                        self.generate_signals(ma_fast, ma_slow)
                        for i in range(1, len(self.data)):
                            # self.execute_trades(self.data['Signal'].iloc[i], self.data['close'].iloc[i], tp, sl)
                            self.martingale(self.data['close'].iloc[i], tp, sl)
                        roi = (self.capital - 10000) / 10000
                        result = pd.DataFrame({'MA_Fast': ma_fast, 'MA_Slow': ma_slow, 'TP': tp, 'SL': sl, 'ROI': roi, 'Total_Profit': self.capital - 10000}, index=[0])
                        results = results.append(result)
        return results

# Example usage
data = Data.get_bars(symbol = 'EURUSD', 
                                timeframe=mt5.TIMEFRAME_H1, 
                                start_pos=0, 
                                num_bars = 1000)
backTester = BackTester(data, 10000, 0.001)
results = backTester.backtest()

print(results)



# # Nested loop over different parameter combinations
# results_df = df = pd.DataFrame(columns= [
#     'take_profit',
#     'stop_loss',
#     'fast_sma',
#     'slow_sma',
#     'buy_signals',
#     'sell_signals',
#     ])
