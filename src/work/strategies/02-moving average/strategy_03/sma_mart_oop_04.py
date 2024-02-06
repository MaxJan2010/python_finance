import datetime
import MetaTrader5 as mt5
import pandas as pd
import plotly.express as px
import numpy as np

from datetime import datetime
from IPython.display import display


# pd.set_option('display.max_colwidth', None)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

# variables
deposit = 1000
decimal_factor = 10000
price_safety = 0.97
min_lot = 0.01
volume = 10

# get historical data from MetaTrader5
class Data:
    def __init__(self):
        self.get_bars()
        
    @classmethod
    def get_bars(self, symbol, timeframe, start_pos, num_bars):
        # connect to MetaTrader5 as mt5
        mt5.initialize()

        # Requesting historical data from MetaTrader 5
        bars = mt5.copy_rates_from_pos(symbol, timeframe, start_pos, num_bars)

        # Converting bars we got from MetaTrader5 into dataframe
        candles = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close', 'spread']]

        #  Re-factoring time format into human readable
        candles['time'] = pd.to_datetime(candles['time'], unit='s')

        return candles

tickers = Data.get_bars(symbol = 'EURUSD', 
                                timeframe=mt5.TIMEFRAME_H1, 
                                start_pos=0, 
                                num_bars = 6500)

# export dataframe to excel file

# create file name based on current date and time
filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S.csv')

# export dataframe to excel file
tickers.to_csv('feeds.csv', index = False)  

class BackTester:
    def __init__(self, data, decimal_factor, min_lot, martingale_multiplier):
        self.data = data
        # self.initial_capital = initial_capital
        self.decimal_factor = decimal_factor
        self.min_lot = min_lot
        self.martingale_multiplier = martingale_multiplier
        
    def indicator_sma(self, ma_fast, ma_slow):
        self.data['fast_sma'] = self.data['close'].rolling(ma_fast).mean()
        self.data['slow_sma'] = self.data['close'].rolling(ma_slow).mean()

        self.data.dropna(inplace=True)
        return self.data
    
    def create_signals(self):
        self.data = self.indicator_sma(ma_fast, ma_slow)
        conditions_signal = [
            self.data['fast_sma'].gt(self.data['slow_sma']), # up signal
            self.data['fast_sma'].lt(self.data['slow_sma']), # down signal
        ]

        choices_signal = [
            'buy', 
            'sell'
            ]

        self.data['signal'] = np.select(conditions_signal, choices_signal, default=None)
        self.data['signal'] = self.data['signal'].shift(1)
        return self.data


    # def calc_indicator_ma(self, window):
    #     return self.data['close'].rolling(window=window).mean()

    # def create_signals(self, ma_fast, ma_slow):
    #     self.data['signal'] = None
    #     self.data.loc[self.calc_indicator_ma(ma_fast) > self.calc_indicator_ma(ma_slow), 'signal'] = 'buy'  # Buy
    #     self.data.loc[self.calc_indicator_ma(ma_fast) < self.calc_indicator_ma(ma_slow), 'signal'] = 'sell'  # Sell
    #     self.data['signal'] = self.data['signal'].shift(1)
    #     self.data.dropna(inplace=True)
    #     return self.data
    
    def create_ohlcv(self):
        self.data = self.create_signals()
        deals = self.data.groupby((self.data.signal != self.data.signal.shift()).cumsum(), as_index= False).agg(
            open_time = ('time', 'first'),
            signal = ('signal', 'first'),
            open_price = ('open', 'first'),
            highest = ('high', 'max'),
            lowest = ('low', 'min')
        )

        deals['open_price'] = round(deals['open_price'] * price_safety, 5)
        deals['close_price'] = deals['open_price'].shift(-1)
        deals['close_price'].replace(r'\s+|^$', self.data['close'].iloc[-1], regex=True)
        
        deals.dropna(inplace=True)
        
        return deals
    
    def calc_max_tp_sl(self):
        deals = self.create_ohlcv()
        deals['max_tp_points'] = np.where(deals['signal'] == 'buy', (deals['highest'] - deals['open_price']) * decimal_factor, 
                                       (deals['open_price'] - deals['lowest']) * decimal_factor)
        deals['max_sl_points'] = np.where(deals['signal'] == 'buy', (deals['open_price'] - deals['lowest'])  * decimal_factor, 
                                       (deals['highest'] - deals['open_price']) * decimal_factor)
        return deals
        
    def apply_profit_dots(self):
        deals = self.calc_max_tp_sl()
        deals['dots'] = np.where(deals['signal'] == 'buy', deals['close_price'] - deals['open_price'], deals['open_price'] - deals['close_price'])
        deals['points'] = deals['dots'] * self.decimal_factor
        deals['type'] = np.where(deals['dots'] > 0, 'win', 'loss')
        deals.reset_index(drop=True, inplace=True)
        return deals
    
    def calc_martingale(self):
        deals = self.apply_profit_dots()
        deals["martingale"] = 1
        for i in range(1, len(deals)):
            if deals.loc[i - 1, "type"] == "win":
                deals.loc[i, "martingale"] = 1
            else:
                deals.loc[i, "martingale"] = deals.loc[i - 1, "martingale"] * self.martingale_multiplier
        return deals
    
    def calc_pnl(self):
        deals = self.calc_martingale()
        deals['lot'] = deals['martingale'] * self.min_lot
        deals['profit'] = deals['points'] * deals['lot'] * volume
        deals['pnl_points'] = deals['points'].cumsum()
        deals['pnl_value'] = deals['profit'].cumsum() + deposit
        return deals
    
    def calc_equity(self):
        deals = self.calc_pnl()
        i = deals.pnl_value.lt(0).idxmax()
        if i != 0:
            i = i + 1
            l = len(deals)
            negative_value = deals.loc[i - 1, 'pnl_value']
            deals.loc[i:l,'equity'] = 0
            deals['equity'] = deals['equity'].fillna(deals.pnl_value)
        else:
            deals['equity'] = deals['pnl_value']
        
        return deals
    
    def calc_result(self, ma_fast, ma_slow):
        deals = self.calc_equity()
        
        # find gross equity if pnl containing a value less than zero
        equity = round(deals['equity'].iloc[-1], 2)
        
        # find balance
        balance = round(deals['pnl_value'].iloc[-1], 2)

        # find total net profit
        total_net_profit = round(deals['profit'].sum(), 2)  # Use in backtest Factors

        # find gross profit
        gross_profit = round(sum(deals[deals['type']=='win']['profit']), 2)

        # find gross loss
        gross_loss = round(sum(deals[deals['type']=='loss']['profit']), 2)
        
        # find maximum martingale multiplier factor
        max_martingale = round(deals['martingale'].max(), 2)

        # find profit factor
        profit_factor = abs(round((gross_profit / gross_loss), 2))
        
        # find largest profit trade
        largest_profit_trade = round(deals['profit'].max(), 2)
        
        # find largest profit trade
        df2=deals.loc[deals['profit'] == deals['profit'].max(), 'open_time'].item()

        # find largest loss trade
        largest_loss_trade = round(deals['profit'].min(), 2)

        # find total trades
        total_trades = len(deals)

        # find total count of SELL trades
        count_sell_trades = deals['signal'].value_counts()['sell']

        # find total count of BUY trades
        count_buy_trades = deals['signal'].value_counts()['buy']

        # find total count of WIN trades
        count_win_trades = deals['type'].value_counts()['win']
        
        # find total count of LOSS trades
        count_loss_trades = deals['type'].value_counts()['loss']

        # select rows by value
        # avg_win = deals_group.loc[deals_group['profit_type'] == 'win']

        # find average value of WIN Trades
        ave_win_value = round(deals.loc[deals['type'] == 'win']['profit'].mean() , 2)

        # find average value of LOSS Trades
        ave_loss_value = round(deals.loc[deals['type'] == 'loss']['profit'].mean(), 2)
        
        # find max take profit points
        max_tp_points = round(deals['max_tp_points'].max(), 2)
    
        # find average take profit points
        avg_tp_points = round(deals['max_tp_points'].mean(), 2)
        
        # find min take profit points
        min_tp_points = round(deals['max_tp_points'].min(), 2)
        
        # find max stop loss points
        max_sl_points = round(deals['max_sl_points'].max(), 2)
        
        # find average stop loss points
        avg_sl_points = round(deals['max_sl_points'].mean(), 2)
        
        # find min stop loss points
        min_sl_points = round(deals['max_sl_points'].min(), 2)
        
        # # find max take profit points open time
        # df3=deals.loc[deals['max_tp_points'] == deals['max_tp_points'].max(), 'open_time'].item()
        
        # # find max stop loss points open time
        # df4=deals.loc[deals['max_sl_points'] == deals['max_sl_points'].max(), 'open_time'].item()
        
        # Collect consecutive Profit / Loss (Factors)

        # find consecutive Profit / Loss
        positions_group = deals.groupby((deals.type != deals.type.shift()).cumsum()).agg(
        type = ('type', 'first'),
        grand_profit = ('profit', 'sum'),
        grand_points = ('points', 'sum'),
        count = ('type', 'count')
        ).reset_index(drop=True)

        # find largest consecutive WIN trade
        largest_cons_win = round(positions_group['grand_profit'].max(), 2)
        # find largest consecutive WIN trade (count)
        count_largest_win = positions_group.loc[positions_group['grand_profit'].idxmax(), 'count']

        # find largest consecutive LOSS trade
        largest_cons_loss = round(positions_group['grand_profit'].min(), 2)

        # find largest consecutive LOSS trade (count)
        count_largest_loss = positions_group.loc[positions_group['grand_profit'].idxmin(), 'count']
        
        result = {
            'fast_sma': [ma_fast], # fast SMA
            'slow_sma': [ma_slow], # slow SMA
            'equity': [equity],
            'deposit': [deposit], # deposit
            'balance': [balance], # balance
            'pnl': [total_net_profit],
            'gross_profit': [gross_profit],
            'gross_loss': [gross_loss],
            'profit_factor': [profit_factor],
            'max_martingale': [max_martingale],
            'max_win': [largest_profit_trade],
            'max_loss': [largest_loss_trade],
            'total_trades': [total_trades],
            'count_sell': [count_sell_trades],
            'count_buy': [count_buy_trades],
            'count_win': [count_win_trades],
            'count_loss': [count_loss_trades],
            'ave_win': [ave_win_value],
            'ave_loss': [ave_loss_value],
            'max_tp_points': [max_tp_points],
            'avg_tp_points': [avg_tp_points],
            'min_tp_points': [min_tp_points],
            'max_sl_points': [max_sl_points],
            'avg_sl_points': [avg_sl_points],
            'min_sl_points': [min_sl_points],
            'max_cons_win': [largest_cons_win],
            'count_max_cons_win': [count_largest_win],
            'max_cons_loss': [largest_cons_loss],
            'count_max_cons_loss': [count_largest_loss],
        }
        result_df = pd.DataFrame.from_dict(result)
        return result_df

# Nested loop for testing parameters
results = pd.DataFrame()
for ma_fast in np.arange(5, 50, 5):
    for ma_slow in np.arange(50, 210, 10):
        facts = tickers.copy()  # Reset data for each loop
        fund = deposit # Reset capital for each loop
        backTester = BackTester(data=facts, decimal_factor=decimal_factor, min_lot=min_lot, martingale_multiplier=2)
        backTester.indicator_sma(ma_fast, ma_slow)
        result = backTester.calc_result(ma_fast, ma_slow)
        equity = backTester.calc_equity()
        # filename = ('ma_fast_' + str(ma_fast) + ' ' + 'ma_slow_' + str(ma_slow) + '.xlsx')
        # equity.to_excel(filename)  
        results = results.append(result)


results = results[results['equity'] > 0].reset_index(drop=True)
results = results[results['max_martingale'] <= 128].reset_index(drop=True)
# export dataframe to excel file

# create file name based on current date and time
filename = datetime.now().strftime('%Y-%m-%d-%H-%M-%S.xlsx')

# export dataframe to excel file
results.to_excel(filename)  


print(results)
