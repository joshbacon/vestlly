"""
    This file handles all things snaptrade related
"""

from snaptrade_client import SnapTrade

client_id = os.getenv("CLIENT_ID")
secret = os.getenv("SECRET")
account_id = os.getenv("ACCOUNT_ID")
user_id = os.getenv("USER_ID")
user_secret = os.getenv("USER_SECRET")

snaptrade = SnapTrade(
    client_id=client_id,
    consumer_key=secret
)


# Gets a list of currently open orders for a given account
# Returns list of account objects
def get_orders(account: str) -> list[dict]:
    orders = snaptrade.account_information.get_user_account_orders(
        account_id=account,
        user_id=user_id,
        user_secret=user_secret
    )
    # print(orders.body)
    # print(orders.status)
    return orders.body


# Cancels a given order under a given account
# Returns the reponse status
def cancel_order(account: str, trade_id: str) -> int:
    response = snaptrade.trading.cancel_order(
        account_id=account,
        user_id=user_id,
        user_secret=user_secret,
        brokerage_order_id=trade_id
    )
    # print(response.body)
    # print(f"canceled ?= {response.status == True}")
    return response.status


# Submits an order to buy as many shares as $X can buy at the current market value
# Returns the reponse status
def submit_buy_order(account: str, ticker: str):
    response = snaptrade.trading.place_force_order(
        user_id=user_id,
        user_secret=user_secret,
        account_id=account,
        action="BUY",
        symbol=ticker,
        order_type="Market",
        time_in_force="Day",
        trading_session="REGULAR",
        notional_value=get_buy_amount()
    )
    # print(response.body)
    return response.status

# Submits an order to sell an entire stake of an asset at the current market value
# Returns the reponse status
def submit_sell_order(account: str, ticker: str):
    response = snaptrade.trading.place_force_order(
        user_id=user_id,
        user_secret=user_secret,
        account_id=account,
        action="SELL",
        symbol=ticker,
        order_type="Market",
        time_in_force="Day",
        trading_session="REGULAR"
    )
    # print(response.body)
    return response.status


# Calculates the amount of money to allocate to a trade
#      =   10% of total portfolio value 
# Returns the notional value to use in trade
def get_buy_amount(account: str) -> float:
    cash = snaptrade.account_information.get_user_account_balance(
        account_id=account,
        user_id=user_id,
        user_secret=user_secret
    ).body[0]["cash"]
    # print(f"CASH::: {cash}")

    balance = snaptrade.account_information.get_user_account_details(
        account_id=account,
        user_id=user_id,
        user_secret=user_secret
    ).body["balance"]["total"]["amount"]
    # print(balance)

    amount = balance * 0.1;
    if cash < amount:
        amount = cash
    return "{:.2f}".format(amount)


