import MetaTrader5 as mt5


def market_order(symbol, volume, order_type):
    tick = mt5.symbol_info_tick(symbol)
    order_dict = {'buy': 0, 'sell': 1}
    price_dict = {'buy': tick.ask, 'sell': tick.bid}
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_dict[order_type],
        "price": price_dict[order_type],
        "sl": 0.00,
        "tp": 0.00,
        "deviation": 20,
        "magic": 100,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
        # "type_filling": mt5.ORDER_FILLING_FOK,
    }
    order_result = mt5.order_send(request)

    return order_result