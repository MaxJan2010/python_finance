import MetaTrader5 as mt5

# MetaTrader5 Authentication Credential
login = 67171729
server = "ForexTimeFXTM-Demo02"
password = "lotbosu8"
visitor = "cyjiin5u"
email = "alkorsanpepsi@hotmail.com"

def mt5_login():
    #  Login To MetaTrader5
    mt5.login(login=login, password=password, server=server)

    # Get Account Info
    account_info = mt5.account_info()
    print("account_info = ", account_info)

    # Get Specific Account Data
    account_login_ID = account_info.login
    account_balance = account_info.balance
    account_equity = account_info.equity

    print("account_login_ID = ", account_login_ID)
    print("account_balance = ", account_balance)
    print("account_equity = ", account_equity)