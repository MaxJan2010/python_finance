import MetaTrader5 as mt5
import pandas as pd

# get open positions on Symbol
def get_open_positions_pair(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        print(f"No positions on " + symbol + " & error code={}".format(mt5.last_error()))
    elif len(positions) > 0:
        print("Total positions on " + symbol + " = " + str(len(positions)))
        # display all open positions
        for position in positions:
            print(position)

# get the list of positions on symbols whose names contain "*USD*"
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