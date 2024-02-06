# This strategy based on the followings:
# Indicators : Bollinger Bands
# If close price under lower bands open buy order
# If close price above upper bands open sell order

#  Import Libraries
import MetaTrader5 as mt5
import pandas as pd

import time

from datetime import datetime, timedelta

from src.work.credential.mt5_credential import *
# from src.work.orders.market_order import *




symbol= 'EURUSD' # Trading Pair
Time_Frame = mt5.TIMEFRAME_D1 # Time Frame
volume = 0.1 # Trade Volume
deviation = 20 # Deviation for Order Slippage
Magic = 100 # Magic Number
SMA_Period = 20  # SMA Period for Bollinger Bands
Standard_Deviation = 2 # Number of Deviations for Bollinger Bands
TP_SD = 2 # Number of Deviations for Take Profit
SL_SD = 3 # Number of Deviations for Stop Loss

def market_order(symbol, volume, order_type, deviation, magic, take_profit, stop_loss):
    tick = mt5.symbol_info_tick(symbol)
    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": deviation,
        "magic": magic,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
        # "type_filling": mt5.ORDER_FILLING_FOK,
    }
    order_result = mt5.order_send(request)
    print(order_result)

    return order_result

def get_signal():
    # Getting OHLC Data from MT5 GBPUSD
    bars = mt5.copy_rates_range(symbol, Time_Frame, 1, SMA_Period)

    # Convert bars to DataFrame
    df = pd.DataFrame(bars)

    # Convert time to datetime
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # calculate bollinger bands

    # calculate sma
    sma = df['close'].mean()
    print("sma = ", sma)

    # calculate standard deviation
    sd = df['close'].std(ddof=0)
    print("sd = ", sd)

    # calculate lower band
    lower_band = sma - Standard_Deviation * sd

    # calculate upper band
    upper_band = sma + Standard_Deviation * sd

    # Get Last Close Price
    last_close_price = df.iloc[-1]['close']

    # Finding Signal

    #  Buy Signal
    if last_close_price < lower_band:
        return 'buy', sd
    
    # Sell Signal
    elif last_close_price > upper_band:
        return 'sell', sd

    # None Signal
    else:
        return [None, None]


# Connect To MetaTrader5
mt5.initialize()


mt5_login()

# Strategy Loop
while True:
    # Strategy Logic

    # If no Positions are Open
    if mt5.positions_total() == 0:
        signal, Standard_Deviation = get_signal()
        print(signal, Standard_Deviation)

        tick = mt5.symbol_info_tick(symbol)
        if signal == 'buy':
            market_order(symbol=symbol,
            volume=0.1, 
            order_type='buy', 
            deviation=deviation, 
            magic=100, 
            take_profit = tick.bid * TP_SD * Standard_Deviation, 
            stop_loss = tick.bid * SL_SD * Standard_Deviation)

        elif signal == 'sell':
            market_order(symbol=symbol,
            volume=0.1, 
            order_type='sell', 
            deviation=deviation, 
            magic=100, 
            take_profit = tick.bid * TP_SD * Standard_Deviation, 
            stop_loss = tick.bid * SL_SD * Standard_Deviation)

            # check for signal every 1 second
            time.sleep(1)

