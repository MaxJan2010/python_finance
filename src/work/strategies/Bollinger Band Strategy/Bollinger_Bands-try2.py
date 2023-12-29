# This strategy based on the followings:
# Indicators : Bollinger Bands
# If close price under lower bands open buy order
# If close price above upper bands open sell order

#  Import Libraries
import MetaTrader5 as mt5
import pandas as pd
import numpy as np

import time

from datetime import datetime, timedelta

from src.work.credential.mt5_credential import *
from src.work.orders.market_order import *

# Connect To MetaTrader5
mt5.initialize()

mt5_login()


def bollinger_bands(symbol):

    # Getting OHLC Data from MT5 of Symbol
    bars = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_D1, 
                                datetime(2020, 1, 1), datetime.now())

    # Convert bars to DataFrame
    df = pd.DataFrame(bars)

    # Convert time to datetime
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # calculate bollinger bands

    # calculate sma
    df['sma'] = df['close'].rolling(20).mean()

    # calculate standard deviation
    df['sd'] = df['close'].rolling(20).std()

    # calculate lower band
    df['lower_band'] = df['sma'] - 2 * df['sd']

    # calculate upper band
    df['upper_band'] = df['sma'] + 2 * df['sd']

    df.dropna(inplace=True)

    return df

def create_signal(close, lower_band, upper_band):
    # Finding Signal
    if close < lower_band:
        return 'buy'
    elif close > upper_band:
        return 'sell'

# Get Bollinger Bands DataFrame
df = bollinger_bands(symbol = "GBPUSD")

# GAdd the Signal Column to DataFrame
df['signal'] = np.vectorize(create_signal)(df['close'], df['lower_band'], df['upper_band'])

print (df)

# Get Last Price Values
last_signal = df.iloc[-1]['signal']
pre_last_signal = df.iloc[-1]['signal']

print(last_signal)
print(pre_last_signal)

# Strategy Logic
if last_signal == None:
    if pre_last_signal == None:
        print("Both are NONE")
        market_order("GBPUSD", 0.03, 'buy')
else:
    print("NO Signal Buy")
