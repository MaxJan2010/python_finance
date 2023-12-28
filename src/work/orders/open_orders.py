import MetaTrader5 as mt5
import pandas as pd

# Get Total QTY of open orders
def get_Total_QTY_open_orders():
    orders = mt5.orders_total()
    print(orders)

# Get List of open orders
def get_list_open_orders():
    orders = mt5.orders_get()
    print(orders)