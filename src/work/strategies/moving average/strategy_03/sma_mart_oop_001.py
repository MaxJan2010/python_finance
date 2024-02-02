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

        return bars

class StockTrader:
    def __init__(self, data, take_profit, stop_loss, fast_sma, slow_sma):
        self.data = data
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.fast_sma = fast_sma
        self.slow_sma = slow_sma

    def calculate_signals(self):
        close = self.data["close"]
        fast_sma = close.rolling(window=self.fast_sma).mean()
        slow_sma = close.rolling(window=self.slow_sma).mean()

        buy_signals = pd.Series(0, index=self.data.index)
        sell_signals = pd.Series(0, index=self.data.index)

        for i in range(len(self.data)):
            if close[i] > fast_sma[i] and close[i] > slow_sma[i]:
                buy_signals.iloc[i] = 1
            elif close[i] < fast_sma[i] or close[i] < slow_sma[i]:
                sell_signals.iloc[i] = 1

        return buy_signals, sell_signals

# Example usage
bars = pd.DataFrame(Data.get_bars(symbol = 'EURUSD', 
                                timeframe=mt5.TIMEFRAME_H1, 
                                start_pos=0, 
                                num_bars = 1000))[['time', 'open', 'high', 'low', 'close', 'spread']]
        
# Converting bars we got from MetaTrader5 into dataframe
data = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close', 'spread']]

#  Re-factoring time format into human readable
data['time'] = pd.to_datetime(data['time'], unit='s')
print(data)



# Nested loop over different parameter combinations
results_df = df = pd.DataFrame(columns= [
    'take_profit',
    'stop_loss',
    'fast_sma',
    'slow_sma',
    'buy_signals',
    'sell_signals',
    ])

results = []
for take_profit in [0.05, 0.1]:
    for stop_loss in [-0.02, -0.05]:
        for fast_sma in [5, 10]:
            for slow_sma in [20, 30]:
                trader = StockTrader(data.copy(), take_profit, stop_loss, fast_sma, slow_sma)
                buy_signals, sell_signals = trader.calculate_signals()
                results.append(
                    {
                        "take_profit": take_profit,
                        "stop_loss": stop_loss,
                        "fast_sma": fast_sma,
                        "slow_sma": slow_sma,
                        "buy_signals": buy_signals,
                        "sell_signals": sell_signals,
                    }
                )
                
# append the new rows to the DataFrame
results_df = results_df.append(results, ignore_index=True)

# export dataframe to excel file

# create file name based on current date and time
filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S.xlsx')

# export dataframe to excel file
results_df.to_excel(filename)  

print(results_df)

# # Print the results
# for result in results:
#     print(f"Results for take_profit={result['take_profit']}, stop_loss={result['stop_loss']}, fast_sma={result['fast_sma']}, slow_sma={result['slow_sma']}")
#     print(f"Buy signals:\n{result['buy_signals']}")
#     print(f"Sell signals:\n{result['sell_signals']}")
#     print("---")
