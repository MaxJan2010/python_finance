import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

# get the number of orders in history
def num_of_history_orders(from_date, to_date):
    from_date=datetime(2020,1,1)
    to_date=datetime.now()
    num_history_orders=mt5.history_orders_total(from_date, to_date)

    if num_history_orders is None:
        num_history_orders = 0

    if num_history_orders > 0:
        print("Total history orders =",num_history_orders)
    else:
        print("Orders not found in history")
    
    return num_history_orders


# get the number of orders in history by currency
def num_of_history_orders_by_currency(from_date, to_date, group):
    history_orders=mt5.history_orders_get(from_date, to_date, group=group)
    if history_orders == None or not history_orders:
        print("No history orders with group = {}, error code = {}".format(group, mt5.last_error()))
    elif len(history_orders) > 0:
        print("history orders from date({}), to date ({}), of group = ({}) = {}".format(from_date, to_date, group, len(history_orders)))
    return history_orders
