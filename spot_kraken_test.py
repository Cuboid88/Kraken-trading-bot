import os
import requests
from kraken.spot import Market, Trade, User
from dotenv import load_dotenv

# Endpoint for Fear and Greed Index
FNG_URL = "https://api.alternative.me/fng/?limit=1"
FNG_SELL_THRESHOLD = 80
FNG_BUY_THRESHOLD = 30
DAILY_BUY_AMOUNT_USD = 10

load_dotenv()


# Load environment variables from .env file
API = os.getenv("API")
SECRET = os.getenv("SECRET")

# Set up logging configuration
user = User(key=API, secret=SECRET)
trade = Trade(key=API, secret=SECRET)
market = Market()

def get_balance(user: User, asset: str):
    resp = user.get_balance(currency=asset)
    return float(resp["balance"])

def get_BTC_price():


    # 2. Fetch ticker info for BTC/USD (Kraken uses "XBT" for Bitcoin)
    ticker = market.get_ticker(pair="XBTUSD")

    # 3. Extract the last trade price
    #    Kraken’s internal code for BTC/USD is "XXBTZUSD"
    pair_code = "XXBTZUSD"
    # cast to float here!
    return float(ticker[pair_code]["c"][0])

def fetch_fng_data():
    """
    Fetches Fear and Greed Index data from the Alternative.me API.
    Returns a sorted list of FNG data points with timestamps.
    """
    response = requests.get(FNG_URL)
    if response.status_code != 200:
        raise Exception(f"Error fetching FNG data: {response.status_code}")
    
    data = response.json()

    return int(data["data"][0]["value"])


def execute_buy_order():

    current_price = get_BTC_price()
    amount_to_buy = DAILY_BUY_AMOUNT_USD / current_price
    print(f"Buying BTC worth {DAILY_BUY_AMOUNT_USD} USD at price {current_price} USD")

    response = trade.create_order(
    ordertype="market",
    side="buy",
    pair="XBTUSD",
    volume=amount_to_buy,
    validate=False
    )

    print(f"Order response: {response}")

def execute_sell_order():
    
    amount_to_sell = get_balance(user, "XBT")
    print(f"Selling BTC worth {amount_to_sell} XBT")

    response = trade.create_order(
    ordertype="market",
    side="sell",
    pair="XBTUSD",
    volume=amount_to_sell,
    validate=False
    )

    print(f"Order response: {response}")

def check_fng_data():
    fng_value = fetch_fng_data()
    if fng_value <= FNG_BUY_THRESHOLD:
        print("Fear and Greed Index is below 25. Consider buying BTC.")
        execute_buy_order()
    elif fng_value >= FNG_SELL_THRESHOLD:
        print("Fear and Greed Index is above 80. Consider selling BTC.")
        execute_sell_order()
    else:
        print("Fear and Greed Index is neutral.")
    

if __name__ == "__main__":
    print(f"BTC/USD last trade price: {get_BTC_price()}")
    print(f"Current Fear and Greed Index: {fetch_fng_data()}")
    print(f"Current BTC balance: {get_balance(user, 'XBT')}")
    print(f"Current USD balance: {get_balance(user, 'USD')}$")
    check_fng_data()
    