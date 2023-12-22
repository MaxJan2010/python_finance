import MetaTrader5 as mt5
import pandas as pd

# get open positions on symbol
def get_open_positions_symbol(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        print(f"No positions on " + symbol + " & error code={}".format(mt5.last_error()))
    elif len(positions) > 0:
        print("Total positions on " + symbol + " = " + str(len(positions)))
        # display all open positions
        for position in positions:
            print(position)

# get the list of positions on symbol whose names contain "*USD*"
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


def calc_total_profit_symbol(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    profit = float(df["profit"].sum())
    print("Total Profit of " + symbol + " is = " + str(profit))
    return profit

def calc_total_buy_profit_symbol(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    df = df.loc[df.type == 0]
    profit = float(df["profit"].sum())
    print("Total BUY Profit of " + symbol + " is = " + str(profit))
    return profit

def calc_total_sell_profit_symbol(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    df = df.loc[df.type == 1]
    profit = float(df["profit"].sum())
    print("Total SELL Profit of " + symbol + " is = " + str(profit))
    return profit

def calc_total_volume_symbol(symbol):
    positions = mt5.positions_get(symbol=symbol)
    df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    volume = float(df["volume"].sum())
    print("Total Volume of " + symbol + " is = " + str(volume))
    return volume

def calc_total_buy_margin_symbol(symbol):
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

def calc_total_sell_margin_symbol(symbol):
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

def calc_total_percentage_profit_symbol(symbol):
    total_profit_symbol = calc_total_profit_symbol(symbol)
    buy_margin = calc_total_buy_margin_symbol(symbol)
    sell_margin = calc_total_sell_margin_symbol(symbol)
    total_margin = buy_margin + sell_margin
    percentage_profit = (total_profit_symbol / total_margin) * 100
    print("Total total_margin of " + symbol + " is = " + str(total_margin))
    print("Total percentage_profit of " + symbol + " is = " + str(percentage_profit))
    return percentage_profit

def close_position(position):
    tick = mt5.symbol_info_tick(position.symbol)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "position": position.ticket,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
        "price": tick.ask if position.type == 1 else tick.bid,
        # "sl": price - 100 * point,
        # "tp": price + 100 * point,
        "deviation": 20,
        "magic": 100,
        "comment": "python script close ",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    result = mt5.order_send(request)
    return result


def close_all_positions_symbol(symbol):
    positions = mt5.positions_get(symbol=symbol)
    for position in positions:
        close_position(position)
    
    my_positions = mt5.positions_get(symbol=symbol)

    if not my_positions:
        print(f"No positions on " + symbol + " & error code={}".format(mt5.last_error()))
        print("Closed All Open Position Successfully for The Symbol = " + symbol)
    elif len(my_positions) > 0:
        print("Total positions on " + symbol + " = " + str(len(my_positions)))
        # display all open positions
        for my_position in my_positions:
            print(my_position)
        print("Closed All Open Position ERROR for The Symbol = " + symbol)
        print("PLEASE TRY AGAIN")

    


