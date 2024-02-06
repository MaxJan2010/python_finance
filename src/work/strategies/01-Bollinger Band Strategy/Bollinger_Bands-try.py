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

symbol= 'EURUSD' # Trading Pair
Time_Frame = mt5.TIMEFRAME_D1 # Time Frame
volume = 0.1 # Trade Volume
deviation = 20 # Deviation for Order Slippage
Magic = 100 # Magic Number
SMA_Period = 20  # SMA Period for Bollinger Bands
Standard_Deviation = 2 # Number of Deviations for Bollinger Bands
TP_SD = 2 # Number of Deviations for Take Profit
SL_SD = 3 # Number of Deviations for Stop Loss

# def market_order(symbol, volume, order_type, deviation, magic, 
# # take_profit, 
# # stop_loss
# ):
#     tick = mt5.symbol_info_tick(symbol)
#     order_dict = {'buy': 0, 'sell': 1}
#     price_dict = {'buy': tick.ask, 'sell': tick.bid}
#     point = mt5.symbol_info(symbol).point
#     request = {
#         "action": mt5.TRADE_ACTION_DEAL,
#         "symbol": symbol,
#         "volume": volume,
#         "type": order_dict[order_type],
#         "price": price_dict[order_type],
#         # "sl": stop_loss,
#         # "tp": take_profit,
#         "deviation": deviation,
#         "magic": magic,
#         "comment": "python script open",
#         "type_time": mt5.ORDER_TIME_GTC,
#         "type_filling": mt5.ORDER_FILLING_IOC,
#         # "type_filling": mt5.ORDER_FILLING_FOK,
#     }
#     order_result = mt5.order_send(request)
#     print(order_result)

    # return order_result

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

def get_signal():
    # Get Last Price Values
    last_signal = df.iloc[-1]['signal']
    pre_last_signal = df.iloc[-1]['signal']

    print(last_signal)
    print(pre_last_signal)

    # Strategy Logic
    if last_signal == None:
        if pre_last_signal == None:
            market_order("GBPUSD", 0.03, 'buy')
            # market_order(
            #     symbol="GBPUSD", 
            #     volume=0.1, 
            #     order_type="buy", 
            #     deviation=20, 
            #     magic=100, 
            #     # take_profit = tick.ask + 100 * point,
            #     # stop_loss = tick.ask - 100 * point
            # )
        else:
            print("NO Signal Buy")
    elif last_signal == 'sell':
        if pre_last_signal == None:
            # market_order(
            #     symbol="EURCAD", 
            #     volume=0.1, 
            #     order_type="sell", 
            #     deviation=20, 
            #     magic=100, 
            #     take_profit = tick.bid + 100 * point,
            #     stop_loss = tick.bid - 100 * point
            # )
            print("Sell Signal")
        else:
            print("NO Signal Sell")

get_signal()

# # Strategy Loop
# while True:
#     # Strategy Logic Function
#     get_signal()
    
#     # check for signal every 60 second
#     time.sleep(60)
