import datetime
import MetaTrader5 as mt5
import pandas as pd
import plotly.express as px
import numpy as np

from datetime import datetime
from IPython.display import display


# pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

# variables
deposit = 1000
decimal_factor = 10000
price_safety = 0.97
min_lot = 0.1
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
                                timeframe=mt5.TIMEFRAME_H4, 
                                start_pos=0, 
                                num_bars = 6500)

class BackTester:
    def __init__(self, data, initial_capital, decimal_factor, min_lot, martingale_multiplier, commission):
        self.data = data
        self.initial_capital = initial_capital
        self.decimal_factor = decimal_factor
        self.min_lot = min_lot
        self.martingale_multiplier = martingale_multiplier
        self.commission = commission
        self.positions = pd.DataFrame(columns=['EntryPrice', 'Quantity', 'TP', 'SL'])

    def calc_indicator_ma(self, window):
        return self.data['close'].rolling(window=window).mean()

    def create_signals(self, ma_fast, ma_slow):
        self.data['signal'] = None
        self.data.loc[self.calc_indicator_ma(ma_fast) > self.calc_indicator_ma(ma_slow), 'signal'] = 'buy'  # Buy
        self.data.loc[self.calc_indicator_ma(ma_fast) < self.calc_indicator_ma(ma_slow), 'signal'] = 'sell'  # Sell
        self.data['signal'] = self.data['signal'].shift(1)
        self.data.dropna(inplace=True)
        return self.data
    
    def create_ohlcv(self):
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
        deals['max_tp_points'] = np.where(deals['signal'] == 'buy', (deals['highest'] - deals['open_price']), 
                                    (deals['open_price'] - deals['lowest']) ) * self.decimal_factor
        deals['max_sl_points'] = np.where(deals['signal'] == 'buy', (deals['open_price'] - deals['lowest']) , 
                                    (deals['highest'] - deals['open_price'])) * self.decimal_factor
        return deals
    
    # def calc_close_price(self, tp, sl):
    #     deals = self.calc_max_tp_sl()
        
    #     self.tp = tp * decimal_factor
    #     self.sl = sl * decimal_factor
        
    #     deals['take_profit'] = self.tp
    #     deals['stop_loss'] = self.sl
    #     # if deals['signal'] == 'buy':
    #     return deals
    
    def apply_profit_dots(self):
        # deals = self.calc_close_price(tp=0, sl=0)
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
        deals['pnl_value'] = deals['profit'].cumsum() + self.initial_capital
        return deals
    
    def calc_equity(self):
        deals = self.calc_pnl()
        i = deals.pnl_value.lt(0).idxmax() + 1
        l = len(deals)
        negative_value = deals.loc[i - 1, 'pnl_value']
        deals.loc[i:l,'equity'] = 0
        deals['equity'] = deals['equity'].fillna(deals.pnl_value)
        return deals
    
    def calc_result(self):
        deals = self.calc_equity()
        
        # find balance
        equity = round(deals['equity'].iloc[-1], 2)
        print('equity = ', equity)
        
        # find balance
        balance = round(deals['pnl_value'].iloc[-1], 2)
        print('balance = ', balance)

        # find total net profit
        total_net_profit = round(deals['profit'].sum(), 2)  # Use in backtest Factors
        print('total net profit = ', total_net_profit)

        # find gross profit
        gross_profit = round(sum(deals[deals['type']=='win']['profit']), 2)
        print('gross profit = ', gross_profit)

        # find gross loss
        gross_loss = round(sum(deals[deals['type']=='loss']['profit']), 2)
        print('gross loss = ', gross_loss)
        
        # find maximum martingale multiplier factor
        max_martingale = round(deals['martingale'].max(), 2)
        print('maximum martingale = ', max_martingale)

        # find profit factor
        profit_factor = abs(round((gross_profit / gross_loss), 2))
        print('profit factor = ', profit_factor)
        
        # find largest profit trade
        largest_profit_trade = round(deals['profit'].max(), 2)
        print('largest profit trade = ', largest_profit_trade)
        
        # find largest profit trade
        df2=deals.loc[deals['profit'] == deals['profit'].max(), 'open_time'].item()
        print('largest profit trade open time = ', df2)

        # find largest loss trade
        largest_loss_trade = round(deals['profit'].min(), 2)
        print('largest loss trade = ', largest_loss_trade)

        # find total trades
        total_trades = len(deals)
        print('total trades = ', total_trades)

        # find total count of SELL trades
        count_sell_trades = deals['signal'].value_counts()['sell']
        print('count SELL trades = ', count_sell_trades)

        # find total count of BUY trades
        count_buy_trades = deals['signal'].value_counts()['buy']
        print('count BUY trades = ', count_buy_trades)

        # find total count of WIN trades
        count_win_trades = deals['type'].value_counts()['win']
        print('count WIN trades = ', count_win_trades)
        
        # find total count of LOSS trades
        count_loss_trades = deals['type'].value_counts()['loss']
        print('count LOSS trades = ', count_loss_trades)

        # select rows by value
        # avg_win = deals_group.loc[deals_group['profit_type'] == 'win']
        # print('avg_win' , avg_win)

        # find average value of WIN Trades
        ave_win_value = round(deals.loc[deals['type'] == 'win']['profit'].mean() , 2)
        print('ave_win_value = ' , ave_win_value)

        # find average value of LOSS Trades
        ave_loss_value = round(deals.loc[deals['type'] == 'loss']['profit'].mean(), 2)
        print('ave_loss_value = ' , ave_loss_value)
        
        # find max take profit points
        max_tp_points = round(deals['max_tp_points'].max(), 2)
        print('max take profit points = ', max_tp_points)
    
        # find average take profit points
        avg_tp_points = round(deals['max_tp_points'].mean(), 2)
        print('average take profit points = ', avg_tp_points)   
        
        # find min take profit points
        min_tp_points = round(deals['max_tp_points'].min(), 2)
        print('min take profit points = ', min_tp_points)   
        
        # find max stop loss points
        max_sl_points = round(deals['max_sl_points'].max(), 2)
        print('max stop loss points = ', max_sl_points)
        
        # find average stop loss points
        avg_sl_points = round(deals['max_sl_points'].mean(), 2)
        print('average stop loss points = ', avg_sl_points) 
        
        # find min stop loss points
        min_sl_points = round(deals['max_sl_points'].min(), 2)
        print('min stop loss points = ', min_sl_points)
        
        # find max take profit points open time
        df3=deals.loc[deals['max_tp_points'] == deals['max_tp_points'].max(), 'open_time'].item()
        print('max take profit points open time = ', df3)
        
        # find max stop loss points open time
        df4=deals.loc[deals['max_sl_points'] == deals['max_sl_points'].max(), 'open_time'].item()
        print('max stop loss points open time = ', df4)
        
        # Collect consecutive Profit / Loss (Factors)

        # find consecutive Profit / Loss
        positions_group = deals.groupby((deals.type != deals.type.shift()).cumsum()).agg(
        type = ('type', 'first'),
        grand_profit = ('profit', 'sum'),
        grand_points = ('points', 'sum'),
        count = ('type', 'count')
        ).reset_index(drop=True)

        print('count trades groups = ')
        print(positions_group)

        # find largest consecutive WIN trade
        largest_cons_win = round(positions_group['grand_profit'].max(), 2)
        print('largest consecutive WIN trade = ', largest_cons_win)

        # find largest consecutive WIN trade (count)
        count_largest_win = positions_group.loc[positions_group['grand_profit'].idxmax(), 'count']
        print('largest consecutive WIN trade (count) = ', count_largest_win)

        # find largest consecutive LOSS trade
        largest_cons_loss = round(positions_group['grand_profit'].min(), 2)
        print('largest consecutive LOSS trade = ', largest_cons_loss)

        # find largest consecutive LOSS trade (count)
        count_largest_loss = positions_group.loc[positions_group['grand_profit'].idxmin(), 'count']
        print('largest consecutive LOSS trade (count) = ', count_largest_loss)
        
        result = {
            # 'fast_sma': [fast_sma_period], # fast SMA
            # 'slow_sma': [slow_sma_period], # slow SMA
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
    
    def calc_collection(self):
        collection = pd.DataFrame(columns = [
                # 'fast_sma': [fast_sma_period], # fast SMA
                # 'slow_sma': [slow_sma_period], # slow SMA
                'equity',
                'deposit', # deposit
                'balance', # balance
                'pnl',
                'gross_profit',
                'gross_loss',
                'profit_factor',
                'max_martingale',
                'max_win',
                'max_loss',
                'total_trades',
                'count_sell',
                'count_buy',
                'count_win',
                'count_loss',
                'ave_win',
                'ave_loss',
                'max_tp_points',
                'avg_tp_points',
                'min_tp_points',
                'max_sl_points',
                'avg_sl_points',
                'min_sl_points',
                'max_cons_win',
                'count_max_cons_win',
                'max_cons_loss',
                'count_max_cons_loss',
        ])
        return collection
    
    def backtest(self):
        results = self.calc_collection()
        for ma_fast in [10, 20, 50]:
            for ma_slow in [20, 50, 100]:
                # for tp in [0.05, 0.1]:
                #     for sl in [0.03, 0.05]:
                        self.capital = deposit  # Reset capital for each loop
                        self.create_signals(ma_fast, ma_slow)
                        # for i in range(1, len(self.data)):
                        #     self.calc_result()
                            # self.execute_trades(self.data['Signal'].iloc[i], self.data['close'].iloc[i], tp, sl)
                            # self.martingale(self.data['close'].iloc[i], tp, sl)
                        # roi = (self.capital - 10000) / 10000
                        # result = pd.DataFrame({'MA_Fast': ma_fast, 'MA_Slow': ma_slow, 'TP': tp, 'SL': sl, 'ROI': roi, 'Total_Profit': self.capital - 10000}, index=[0])
                        result = self.calc_result()
                        results = results.append(result)
        return results
    
    # def run(self):
    #     self.create_signals(ma_fast=5, ma_slow=100)
    #     self.create_ohlcv()
    #     self.apply_profit_dots()
    #     self.calculate_martingale()



backTester = BackTester(data=tickers, initial_capital=deposit, decimal_factor=decimal_factor, min_lot=0.1, martingale_multiplier=2, commission=0.001)
# signals = backTester.create_signals(ma_fast=50, ma_slow=200)
# deals = backTester.calc_equity()
# result = backTester.calc_result()

# collection = pd.concat([collection, result],ignore_index = True)


# titles_deals = deals.columns
# titles_results = result.columns

# print(deals)

results = backTester.backtest()

print('find the result')
print(results)

# for title in titles_deals:
#     print(title)
    
# for title in titles_results:
#     print(title)
#     def backtest(self):
#         results = pd.DataFrame()
#         for ma_fast in [10, 20, 50]:
#             for ma_slow in [20, 50, 100]:
#                 for tp in [0.05, 0.1]:
#                     for sl in [0.03, 0.05]:
#                         self.capital = 10000  # Reset capital for each loop
#                         self.generate_signals(ma_fast, ma_slow)
#                         for i in range(1, len(self.data)):
#                             # self.execute_trades(self.data['Signal'].iloc[i], self.data['close'].iloc[i], tp, sl)
#                             self.martingale(self.data['close'].iloc[i], tp, sl)
#                         roi = (self.capital - 10000) / 10000
#                         result = pd.DataFrame({'MA_Fast': ma_fast, 'MA_Slow': ma_slow, 'TP': tp, 'SL': sl, 'ROI': roi, 'Total_Profit': self.capital - 10000}, index=[0])
#                         results = results.append(result)
#         return results

# # Example usage

# backTester = BackTester(data, 10000, 0.001)
# results = backTester.backtest()

# print(results)



# # Nested loop over different parameter combinations
# results_df = df = pd.DataFrame(columns= [
#     'take_profit',
#     'stop_loss',
#     'fast_sma',
#     'slow_sma',
#     'buy_signals',
#     'sell_signals',
#     ])


