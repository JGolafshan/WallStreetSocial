from iexfinance.stocks import get_historical_data
from database import Database as db
from iexfinance.stocks import Stock
from pprint import pprint
import datetime as dt
import pandas as pd
import re
from database import Database

class TickerPipe:
    def __init__(self, before, after): #I put before and after in here because in the fullStack method we'll call the database class load function and use self.before,self.after
        self.before = before
        self.after = after

    def find_tickers(self, comment):
        """
        Creates an initial list of "tickers" in the form $XYZ to be verified by sending the string to IEX. If we get a
        price back,we will add the ticker it into a table in our database, "MENTIONED_STOCKS" if it is not already in
        it. This function willrun through all comments in a batch, and then the verified MENTIONED_STOCKS will be used
        to look through each comment again to find tickers that aren't marked with $.
        This function acts on a single comment.
        """
        tickers = re.findall(r'\$[a-zA-Z]+\b', str(comment))
        print(tickers)
        return tickers

    def verify_tickers(self, tickers):
        """
        Verifies if a ticker is real by sending it to the IEX. If the API call doesn't error out,
        we assume it to be a real ticker and append it to a list of mentioned tickers.
        This function acts on a single comment.
        """
        mentioned_tickers = []
        for ticker in tickers:
            try:
                ticker = str(ticker).replace("$", "")
                found = Stock(ticker, token="pk_294d45992fbb4e8aa325cae768f6468b",
                              output_format="json").get_company_name()
                mentioned_tickers.append(ticker)

            except TypeError as e:
                # ignore the stock name
                continue
        return mentioned_tickers

    def create_master_ticker_list(self, comments):
        """
        Takes in a list of comments and searches through them to create a master list of mentioned comments per batch
        Returns a dataframe list of stocks to be loaded into the MENTIONED_STOCKS table.
        """
        verified_tickers = []
        for comment in comments:
            tickers = self.find_tickers(comment)  # get list of tickers in a comment
            mentioned_tickers = self.verify_tickers(tickers)  # verify if they're real
            for ticker in mentioned_tickers:
                verified_tickers.append(ticker)
        return verified_tickers

    def tickerStack(self):
        comment = self.find_tickers(comment="$TSLA $APPL $PAYP")
        self.verify_tickers(comment)


test = TickerPipe()
test.tickerStack()

