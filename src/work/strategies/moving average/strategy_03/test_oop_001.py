import datetime
import MetaTrader5 as mt5
import pandas as pd
import plotly.express as px
import numpy as np

from datetime import datetime
from IPython.display import display


class BackTester:
    def __init__(self, data, initial_capital, martingale_multiplier):
        self.data = data
        self.initial_capital = initial_capital
        self.martingale_multiplier = martingale_multiplier

    def calc_indicator_ma(self, window):
        return self.data['close'].rolling(window=window).mean()

    def create_signals(self, ma_fast, ma_slow):
        self.data['signal'] = None
        self.data.loc[self.calc_indicator_ma(ma_fast) > self.calc_indicator_ma(ma_slow), 'signal'] = 'buy'  # Buy
        self.data.loc[self.calc_indicator_ma(ma_fast) < self.calc_indicator_ma(ma_slow), 'signal'] = 'sell'  # Sell
        self.data['signal'] = self.data['signal'].shift(1)
        self.data.dropna(inplace=True)
        return self.data
    
    def create_ohlcv(self):
        #  group each 'buy' and 'sell' signal to create the signal
        deals = self.data.groupby((self.data.signal != self.data.signal.shift()).cumsum(), as_index= False).agg(
            open_time = ('time', 'first'), # get the open position time
            signal = ('signal', 'first'), # get the signal
            open_price = ('open', 'first'), # get the open price
            highest = ('high', 'max'), # get the maximum available price during the signal
            lowest = ('low', 'min') # get the lowest available price during the signal
        )
        
        deals.dropna(inplace=True)
        
        return deals
    
# Load your data here
data = pd.read_csv("feeds.csv")
for ma_fast in [10, 20, 50]:
    for ma_slow in [20, 50, 100]:
        # for take_profit in [0.05, 0.1]:
        #     for stop_loss in [0.02, 0.03]:
        facts = data.copy()  # Reset data for each loop
        fund = 10000 # Reset capital for each loop
        backTester = BackTester(data=facts, initial_capital=fund, martingale_multiplier=2)
        backTester.create_signals(ma_fast, ma_slow)
        out = backTester.create_ohlcv()
        print(out)