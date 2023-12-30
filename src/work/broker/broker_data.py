import MetaTrader5 as mt5
import pandas as pd
import plotly.express as px
from datetime import datetime


def get_broker_data():
    # Get QTY of Symbols Available within the Broker
    symbol_qty = mt5.symbols_total()
    print("symbol_qty = ", symbol_qty)

    # Get Lit of all available symbols
    symbols = mt5.symbols_get()
    print("symbols = ", symbols)


def symbol_data(symbol):
    # Get Specific Symbol Specifications
    symbol_info = mt5.symbol_info(symbol)._asdict()
    print("symbol_info = ", symbol_info)

    # Get Specific Symbol price
    symbol_price = mt5.symbol_info_tick(symbol)._asdict()
    print("symbol_price = ", symbol_price)

    # Get Specific Symbol ohlc
    ohlc_data = pd.DataFrame(mt5.copy_rates_range((symbol),
                             mt5.TIMEFRAME_D1,
                             datetime(2021, 1, 1),
                             datetime.now()))
    ohlc_data['time'] = pd.to_datetime(ohlc_data['time'], unit='s')
    print(ohlc_data)
    # Plot Specific Symbol Chart (Time VS Close)
    # figure = px.line(ohlc_data, x=ohlc_data['time'], y=ohlc_data['close'])
    # figure.show()

    # Get Specific Symbol Tick Data
    tick_data = pd.DataFrame(mt5.copy_ticks_range((symbol),
                             datetime(2021, 1, 1),
                             datetime.now(),
                             mt5.COPY_TICKS_ALL))
    tick_data['time'] = pd.to_datetime(tick_data['time'], unit='s')
    print(tick_data)
    # Plot Specific Symbol Chart (Time VS Close)
    figure = px.line(tick_data, x=tick_data['time'], y=[tick_data['bid'], tick_data['ask']])
    figure.show()

