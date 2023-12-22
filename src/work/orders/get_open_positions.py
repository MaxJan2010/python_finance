import MetaTrader5 as mt5
import pandas as pd

# get open positions on pair
def get_open_positions_pair(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        print(f"No positions on " + symbol + " & error code={}".format(mt5.last_error()))
    elif len(positions) > 0:
        print("Total positions on " + symbol + " = " + str(len(positions)))
        # display all open positions
        for position in positions:
            print(position)

# get the list of positions on pair whose names contain "*USD*"
def get_open_positions_currency(currency):
    currency_positions = mt5.positions_get(group=currency)
    if not currency_positions:
        print("No positions with group = " + currency + " & error code={}".format(mt5.last_error()))
    elif len(currency_positions) > 0:
        print("positions_get group = " + currency+ ") = {}".format(len(currency_positions)))
        # display these positions as a table using pandas.DataFrame
        df = pd.DataFrame(list(currency_positions), columns=currency_positions[0]._asdict().keys())
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
        print(df)


def calc_total_profit_pair(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    profit = float(df["profit"].sum())
    print("Total Profit of " + symbol + " is = " + str(profit))
    return profit

def calc_total_buy_profit_pair(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    df = df.loc[df.type == 0]
    profit = float(df["profit"].sum())
    print("Total BUY Profit of " + symbol + " is = " + str(profit))
    return profit

def calc_total_sell_profit_pair(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    df = df.loc[df.type == 1]
    profit = float(df["profit"].sum())
    print("Total SELL Profit of " + symbol + " is = " + str(profit))
    return profit

def calc_total_volume_pair(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    volume = float(df["volume"].sum())
    print("Total Volume of " + symbol + " is = " + str(volume))
    return volume

def calc_total_buy_margin_pair(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    df = df.loc[df.type == 0]

    sum = 0
    for i in df.index:
        volume = df.volume[i]
        open_price = df.price_open[i]
        margin=mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, symbol, volume, open_price)
        sum+=margin

    print("Total BUY Margin of " + symbol + " is = " + str(sum))
    return sum

def calc_total_sell_margin_pair(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    df = df.loc[df.type == 1]

    sum = 0
    for i in df.index:
        volume = df.volume[i]
        open_price = df.price_open[i]
        margin=mt5.order_calc_margin(mt5.ORDER_TYPE_SELL, symbol, volume, open_price)
        sum+=margin

    print("Total SELL Margin of " + symbol + " is = " + str(sum))
    return sum

def calc_total_percentage_profit_pair(symbol):
    total_profit_pair = calc_total_profit_pair(symbol)
    buy_margin = calc_total_buy_margin_pair(symbol)
    sell_margin = calc_total_sell_margin_pair(symbol)
    total_margin = buy_margin + sell_margin
    percentage_profit = (total_profit_pair / total_margin) * 100
    print("Total total_margin of " + symbol + " is = " + str(total_margin))
    print("Total percentage_profit of " + symbol + " is = " + str(percentage_profit))
    return percentage_profit
