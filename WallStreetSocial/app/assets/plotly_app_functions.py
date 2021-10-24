import yfinance as yf
import math


def millify(n):
    millnames = ['', ' K', ' M', ' B', ' T']
    n = float(n)
    if n == 0:
        return 0
    else:
        millidx = max(0, min(len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
        return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])


def verifyStockInput(symbol):
    ticker = yf.Ticker(symbol)
    if ticker.calendar is None:
        return False
    return True


def tickerResults(symbol):
    ticker = yf.Ticker(ticker=symbol)
    ticker_info = ticker.info
    change = round(ticker_info.get('regularMarketPrice') - ticker_info.get('regularMarketPreviousClose'), 3)
    change_percentage = round((change / ticker_info.get('regularMarketPreviousClose')) * 100, 2)

    return change, change_percentage, ticker_info

