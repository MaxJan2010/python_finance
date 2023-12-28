import MetaTrader5 as mt5
import pandas as pd

from broker.broker_data import *
from credential.mt5_credential import *
from orders.limit_orders import *
from orders.market_order import *
from orders.get_open_positions import *
from orders.open_orders import *
from orders.history_orders import *
from orders.history_deals import *


# Connect To MetaTrader5
mt5.initialize()

mt5_login()

# get_broker_data()
# symbol_data("EURUSD")

# market_order("EURUSD", 0.01, 'buy')
# market_order("EURUSD", 0.05, 'sell')
# market_order("GBPUSD", 0.03, 'buy')

# get_total_QTY_open_positions()

# get_open_positions_symbol('EURUSD')
# get_open_positions_currency("*CAD*")

# calc_total_profit_symbol('EURUSD')
# calc_total_profit_symbol('GBPUSD')
# calc_total_volume_symbol("EURUSD")
# calc_total_volume_symbol("GBPUSD")

# calc_total_buy_profit_symbol('EURUSD')
# calc_total_sell_profit_symbol('EURUSD')

# calc_total_buy_margin_symbol('EURUSD')
# calc_total_sell_margin_symbol('EURUSD')

# calc_total_percentage_profit_symbol('EURUSD')

# close_all_positions_symbol('EURUSD')

# buy_limit("EURUSD", 0.01, 1.0650)
# sell_limit("EURUSD", 0.01, 1.0950)
# get_Total_QTY_open_orders()
# get_list_open_orders()

# num_of_history_orders(from_date=datetime(2020,1,1), to_date=datetime.now())
# num_of_history_orders_by_currency(from_date=datetime(2020,1,1), to_date=datetime.now(), group="*JPY*")

# num_of_history_deals(from_date=datetime(2020,1,1), to_date=datetime.now())
# list_of_history_deals(from_date=datetime(2020,1,1), to_date=datetime.now())
# num_of_history_deals_by_currency(from_date=datetime(2020,1,1), to_date=datetime.now(), group="*GBP*")