import MetaTrader5 as mt5

def buy_limit(symbol, volume, price):
    request = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "price": price,
            # "sl": price - 100 * point,
            # "tp": price + 100 * point,
            "deviation": 20,
            "magic": 100,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
    )

def sell_limit(symbol, volume, price):
    request = mt5.order_send(
        {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "price": price,
            # "sl": price - 100 * point,
            # "tp": price + 100 * point,
            "deviation": 20,
            "magic": 100,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
    )