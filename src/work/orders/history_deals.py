import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

# get the number of deals in history
def num_of_history_deals(from_date, to_date):
    deals=mt5.history_deals_total(from_date, to_date)
    if deals>0:
        print("Total deals = ",deals)
    else:
        print("Deals not found in history")
    return deals

# get the list of deals in history
def list_of_history_deals(from_date, to_date):
    deals=mt5.history_deals_get(from_date, to_date)
    if deals == None or not deals:
        print("No history deals, error code = {}".format(mt5.last_error()))
    elif len(deals) > 0:
        print("num of history deals from date({}), to date ({}) = {}".format(from_date, to_date, len(deals)))
        print(deals)
    return deals

# get the num of deals in history by currency
def num_of_history_deals_by_currency(from_date, to_date, group):
    deals=mt5.history_deals_get(from_date, to_date, group=group)
    if deals == None or not deals:
        print("No history deals with group = {}, error code = {}".format(group, mt5.last_error()))
    elif len(deals) > 0:
        print("history deals from date({}), to date ({}), of group = ({}) = {}".format(from_date, to_date, group, len(deals)))
        print(deals)
    return deals