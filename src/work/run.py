import MetaTrader5 as mt5
import pandas as pd

from credential.mt5_credential import *
from orders.limit_orders import *
from orders.market_order import *
from orders.get_open_positions import *

# Connect To MetaTrader5
mt5.initialize()

#  Login To MetaTrader5
mt5.login(login=login, password=password, server=server)

# buy_limit("EURUSD", 0.01, 1.0650)
# sell_limit("EURUSD", 0.01, 1.0950)
market_order("EURUSD", 0.01, 'buy')
market_order("EURUSD", 0.05, 'sell')
# market_order("GBPUSD", 0.03, 'buy')
# get_open_positions_pair('EURUSD')
# get_open_positions_currency("*CAD*")

# calc_total_profit_pair('EURUSD')
# calc_total_profit_pair('GBPUSD')
# calc_total_volume_pair("EURUSD")
# calc_total_volume_pair("GBPUSD")

# calc_total_buy_profit_pair('EURUSD')
# calc_total_sell_profit_pair('EURUSD')

# calc_total_buy_margin_pair('EURUSD')
# calc_total_sell_margin_pair('EURUSD')

calc_total_percentage_profit_pair('EURUSD')