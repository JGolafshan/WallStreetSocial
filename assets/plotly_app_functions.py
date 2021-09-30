import yfinance as yf
from pprint import pprint
import math
import pandas as pd
from iexfinance.stocks import Stock


def millify(n):
    millnames = ['', ' K', ' M', ' B', ' T']
    n = float(n)
    if n == 0:
        return 0
    else:
        millidx = max(0, min(len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
        return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])


symbol = "AAPL"
ticker = yf.ticker.Ticker(ticker=symbol)

from iexfinance import account

api_keys = [
    "pk_294d45992fbb4e8aa325cae768f6468b",
    "pk_f74c2c3a28b04fb6b756bb029766860b"
]

# select stock ticker and create AV objects
symbol = "TSLA"
stock = Stock(symbol, token="pk_294d45992fbb4e8aa325cae768f6468b", output_format="json")

this = "change"

ticker_info = ticker.info
pprint(ticker_info)
change = round(ticker_info.get('regularMarketPrice') - ticker_info.get('regularMarketPreviousClose'), 3)
change_percentage = round((change / ticker_info.get('regularMarketPreviousClose')) * 100, 2)