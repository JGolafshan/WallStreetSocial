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
        self.conn = sqlite3.connect(os.getcwd() + '/WallStreetBets.db')
        self.cursor = self.conn.cursor()

    def create_comment_table(self):
        """
        generates the sql need for the the comments table
        To create the tables use 'table_automation'
        this is an internal function.
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Comment 
            (
                CommentID integer PRIMARY KEY AUTOINCREMENT,
                CommentAuthor text,
                CommentPostDate timestamp,
                CommentText text
            );
            """
        )
        self.conn.commit()

    def create_ticker_table(self):
        """
        generates the sql need for the the ticker table
        To create the tables use 'table_automation'
        this is an internal function.
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Ticker 
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

    def insert_into_comments(self, data):
        """inserts comments into the Comment table"""
        data = data.to_records(index=False).tolist()
        self.cursor.executemany(f"""
                                    INSERT INTO Comment (CommentAuthor, CommentPostDate, CommentText)VALUES(?, ?, ?);
                                """, data, )
        self.conn.commit()

    def insert_into_ticker(self, comment_id, ticker, sentiment):
        """inserts tickers into the Ticker table"""
        self.cursor.execute(
            f""" INSERT INTO Ticker (CommentID, TickerSymbol, TickerSentiment) VALUES (?, ?, ?)""",
            (comment_id, str(ticker).upper(), sentiment))
        self.conn.commit()

    def ticker_generation(self):
        """Uses the the sentiment and ticker models to generate tickers and sentiment for each comment"""
        loadData = self.cursor.execute("""SELECT C.CommentID, C.CommentText FROM Comment C 
                                          WHERE C.CommentID NOT IN (SELECT T.CommentID FROM Ticker T)""").fetchall()
        wsb = load(os.getcwd() + "/WallStreetSocial/models/wsb_ner")
        sia = SentimentIntensityAnalyzer()
        # Add to Ticker DB
        for row in loadData:
            doc = wsb(preprocess(row[1]))
            if len(doc.ents) > 0:
                for ticker in doc.ents:
                    self.insert_into_ticker(row[0], ticker, sia.polarity_scores(row[1])['compound'])
            else:
                self.insert_into_ticker(row[0], None, None)

    def table_automation(self):
        """generates the tables in sql."""
        self.create_comment_table()
        self.create_ticker_table()
