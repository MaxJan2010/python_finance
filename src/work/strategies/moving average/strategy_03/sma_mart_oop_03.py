import datetime
import MetaTrader5 as mt5
import pandas as pd
import plotly.express as px
import numpy as np

from datetime import datetime
from IPython.display import display


# pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

# variables
deposit = 1000

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
                                timeframe=mt5.TIMEFRAME_H1, 
                                start_pos=0, 
                                num_bars = 6500)

class BackTester:
    def __init__(self, data, initial_capital, commission):
        self.data = data
        self.capital = initial_capital
        self.commission = commission
        self.positions = pd.DataFrame(columns=['EntryPrice', 'Quantity', 'TP', 'SL'])

    def calc_indicator_ma(self, window):
        return self.data['close'].rolling(window=window).mean()

    def create_signals(self, ma_fast, ma_slow):
        self.data['signal'] = 0
        self.data.loc[self.calc_indicator_ma(ma_fast) > self.calc_indicator_ma(ma_slow), 'signal'] = 'buy'  # Buy
        self.data.loc[self.calc_indicator_ma(ma_fast) < self.calc_indicator_ma(ma_slow), 'signal'] = 'sell'  # Sell
        self.data['signal'] = self.data['signal'].shift(1)
        self.data.dropna(inplace=True)
        return self.data
    
    def create_ohlcv(self):
        deals = self.data.groupby((self.data.signal != self.data.signal.shift()).cumsum(), as_index= False).agg(
            open_time = ('time', 'first'),
            signal = ('signal', 'first'),
            open_price = ('open', 'first'),
            highest = ('high', 'max'),
            lowest = ('low', 'min')
        )

        safety = 0.97
        deals['open_price'] = round(deals['open_price'] * safety, 5)
        deals['close_price'] = deals['open_price'].shift(-1)
        deals['close_price'].fillna(value=self.data['close'].iloc[-2], inplace=True)
        
        deals.dropna(inplace=True)
        
        return deals


backTester = BackTester(data=tickers, initial_capital=deposit, commission=0.001)
signals = backTester.create_signals(ma_fast=5, ma_slow=100)
deals = backTester.create_ohlcv()
print(deals)

#     def execute_trades(self, signal, price, tp, sl):
#         if signal == 1 and self.positions.any():  # Buy
#             quantity = int(self.capital / price)
#             self.positions = pd.DataFrame({'EntryPrice': price, 'Quantity': quantity, 'TP': tp, 'SL': sl}, index=[0])
#         elif signal == -1 and not len(self.positions)<0:  # Sell
#             exit_price = price - self.commission
#             profit = (exit_price - self.positions['EntryPrice'].values[0]) * self.positions['Quantity'].values[0]
#             self.capital += profit - self.commission
#             self.positions = pd.DataFrame()  # Clear positions

#     def martingale(self, price, tp, sl):
#         if len(self.positions)>0:
#             if price >= self.positions['TP'].values[0]:
#                 exit_price = tp - self.commission
#                 profit = (exit_price - self.positions['EntryPrice'].values[0]) * self.positions['Quantity'].values[0]
#                 self.capital += profit - self.commission
#                 self.positions = pd.DataFrame()
#             elif price <= self.positions['SL'].values[0]:
#                 exit_price = sl + self.commission
#                 profit = (exit_price - self.positions['EntryPrice'].values[0]) * self.positions['Quantity'].values[0]
#                 self.capital += profit - self.commission
#                 self.positions = pd.DataFrame()
#                 self.martingale(price, tp * 2, sl * 2)  # Double TP and SL for next trade

#     def backtest(self):
#         results = pd.DataFrame()
#         for ma_fast in [10, 20, 50]:
#             for ma_slow in [20, 50, 100]:
#                 for tp in [0.05, 0.1]:
#                     for sl in [0.03, 0.05]:
#                         self.capital = 10000  # Reset capital for each loop
#                         self.generate_signals(ma_fast, ma_slow)
#                         for i in range(1, len(self.data)):
#                             # self.execute_trades(self.data['Signal'].iloc[i], self.data['close'].iloc[i], tp, sl)
#                             self.martingale(self.data['close'].iloc[i], tp, sl)
#                         roi = (self.capital - 10000) / 10000
#                         result = pd.DataFrame({'MA_Fast': ma_fast, 'MA_Slow': ma_slow, 'TP': tp, 'SL': sl, 'ROI': roi, 'Total_Profit': self.capital - 10000}, index=[0])
#                         results = results.append(result)
#         return results

# # Example usage

# backTester = BackTester(data, 10000, 0.001)
# results = backTester.backtest()

# print(results)



# # # Nested loop over different parameter combinations
# # results_df = df = pd.DataFrame(columns= [
# #     'take_profit',
# #     'stop_loss',
# #     'fast_sma',
# #     'slow_sma',
# #     'buy_signals',
# #     'sell_signals',
# #     ])
