import os
import sqlite3
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from WallStreetSocial.models.model_utils.preprocess import preprocess


class DatabasePipe:
    """
    This class is used for the creation of an sqlite database/tables
    """
    def __init__(self):
        self.conn = sqlite3.connect(os.getcwd()+'/WallStreetBets.db')
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
                CommentPostDate TIMESTAMP,
                CommentText text,
                CommentHasTicker boolean
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

    def table_automation(self):
        """"""
        self.create_comment_table()
        self.create_ticker_table()

    def insert_into_comments(self, data):
        """"""
        data = data.to_records(index=False).tolist()
        self.cursor.executemany(f"""INSERT INTO Comment (CommentAuthor, CommentPostDate, CommentText) 
                                    VALUES(?, ?, ?);""", data, )
        self.conn.commit()

    def insert_into_ticker(self):
        """"""
        loadData = self.cursor.execute("SELECT * FROM Comment WHERE CommentHasTicker is null;").fetchall()
        wsb = spacy.load(os.getcwd()+"/WallStreetSocial/models/wsb_ner")
        sia = SentimentIntensityAnalyzer()

        # Add to Ticker DB
        for row in loadData:
            text = row[3]
            doc = wsb(preprocess(text))
            has_ticker = 0
            for en in doc.ents:
                if len(doc.ents) >= 1:
                    has_ticker = 1
                    self.cursor.execute(
                        f"""
                            INSERT INTO Ticker (CommentID, TickerSymbol, TickerSentiment)
                            VALUES ({row[0]},
                                    {"'" + str(en).replace("$", "").upper() + "'"}, 
                                    {sia.polarity_scores(text)['compound']})
                        """)
                    self.conn.commit()
            self.cursor.execute(
                f"""
                    UPDATE Comment
                    SET CommentHasTicker = {has_ticker}
                    WHERE CommentID = {row[0]}
                """)
            self.conn.commit()
