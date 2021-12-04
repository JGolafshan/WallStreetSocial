import os
import sqlite3
from spacy import load
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from WallStreetSocial.models.model_utils.preprocess import preprocess


class DatabasePipe:
    """
    This class is used for the creation of an sqlite database/tables
    """

    def __init__(self):
        path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.conn = sqlite3.connect(path + '/WallStreetBets.db')
        self.cursor = self.conn.cursor()

    """
        Select DateRange -> 
        Get Posts -> Split posts into 2 dataframes (Account and Post) -> Add To Account  and Post ->
        Get Comments -> Split posts into 2 dataframes (Account and Comments) -> Add To Account  and Post ->
        Use ML to get tickers and find options.
    """

    # Account Table

    def create_account_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS account 
            (
                AccountID  integer PRIMARY KEY AUTOINCREMENT,
                AccountName TEXT,
                AccountFullName TEXT,
                AccountCreatedDate TIMESTAMP
            );
            """
        )
        self.conn.commit()

    def insert_account(self):
        pass

    def update_account(self):
        pass

    # Post Table

    def create_post_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS post 
            (
                PostID VARCHAR(25)  PRIMARY KEY,
                AccountID integer,
                PostDateTime TIMESTAMP,
                PostTitle STRING,
                PostBody TEXT,
                PostScore INTEGER,
                PostUrl TEXT,
                PostDomain TEXT,
                PostRedditLink TEXT,
                PostSubreddit TEXT,
                FOREIGN KEY (AccountID) REFERENCES account (AccountID)
            );
            """
        )
        self.conn.commit()

    def insert_post(self):
        pass

    # Comment Table

    def create_comment_table(self):
        """
        generates the sql need for the the comments table
        To create the tables use 'table_automation'
        this is an internal function.
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS comment 
            (
                CommentID VARCHAR(25) PRIMARY KEY,
                PostID VARCHAR(25),
                AccountID INTEGER,
                CommentPostDate DATETIME,
                CommentText TEXT,
                CommentScore INTEGER,
                CommentNestLevel INTEGER,
                CommentParentID VARCHAR(25),
                CommentLinkID VARCHAR(25),
                FOREIGN KEY (PostID) REFERENCES post (PostID)
                FOREIGN KEY (AccountID) REFERENCES account (AccountID)
            );
            """
        )
        self.conn.commit()

    def insert_comment(self):
        pass

    # Ticker Table

    def create_ticker_table(self):
        """
        generates the sql need for the the ticker table
        To create the tables use 'table_automation'
        this is an internal function.
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticker 
            (
                TickerID integer PRIMARY KEY AUTOINCREMENT,
                CommentID integer,
                TickerSymbol VARCHAR(5),
                TickerSentiment float,
                FOREIGN KEY (CommentID) REFERENCES Comment (CommentID)
            );
            """
        )
        self.conn.commit()

    def insert_ticker(self):
        pass

    # Option Table

    def create_option_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS option 
            (
                OptionID INTEGER PRIMARY KEY AUTOINCREMENT,
                TickerID INTEGER,
                OptionType VARCHAR(4),
                OptionStrike FLOAT,
                OptionExpirationDate DATETIME,
                OptionContracts INTEGER,
                OptionPremium FLOAT
            );
            """
        )
        self.conn.commit()

    def insert_option(self):
        pass

    def table_automation(self):
        """generates the tables in sql."""
        self.create_account_table()
        self.create_post_table()
        self.create_comment_table()
        self.create_ticker_table()
        self.create_option_table()
