import MetaTrader5 as mt5
import pandas as pd

# get open positions on Symbol
def get_open_positions_pair(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions == None:
        print(f"No positions on " + symbol + "error code={}".format(mt5.last_error()))
    elif len(positions) > 0:
        print("Total positions on " + symbol + " = " + str(len(positions)))
        # display all open positions
        for position in positions:
            print(position)

# get the list of positions on symbols whose names contain "*USD*"
usd_positions = mt5.positions_get(group="*USD*")
if usd_positions == None:
    print("No positions with group=\"*USD*\", error code={}".format(mt5.last_error()))
elif len(usd_positions) > 0:
    print("positions_get(group=\"*USD*\")={}".format(len(usd_positions)))
    # display these positions as a table using pandas.DataFrame
    df = pd.DataFrame(list(usd_positions), columns=usd_positions[0]._asdict().keys())
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
    print(df)