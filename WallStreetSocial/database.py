import os
import spacy
import sqlite3
from WallStreetSocial.preprocess import preprocess
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

model_loc = None


class DatabasePipe:
    def __init__(self):
        self.conn = sqlite3.connect(os.getcwd() + '/WallStreetBets.db')
        self.cursor = self.conn.cursor()

    def create_database(self):
        self.create_comment_table()
        self.create_post_table()
        self.create_ticker_table()
        self.create_option_table()

    def create_comment_table(self):
        table = """CREATE TABLE IF NOT EXISTS "comment" (
                    "comment_id"	INTEGER,
                    "permalink"	String,
                    "subreddit"	String,
                    "author"	String,
                    "body"	String,
                    "score"	String,
                    "created_utc"	String,
                    PRIMARY KEY("comment_id" AUTOINCREMENT)
                );  """
        self.cursor.execute(table)
        self.conn.commit()

    def create_post_table(self):
        table = """CREATE TABLE IF NOT EXISTS "post" (
                    "post_id"	INTEGER,
                    "author"	String,
                    "subreddit"	String,
                    "url"	String,  
                    "title"	String,
                    "created_utc"	String,
                    "score"	String,
                    PRIMARY KEY("post_id" AUTOINCREMENT)
                );"""

        self.cursor.execute(table)
        self.conn.commit()

    def create_ticker_table(self):
        table = """CREATE TABLE IF NOT EXISTS "ticker" (
                    "TickerID"	integer,
                    "CommentID"	integer,
                    "TickerSymbol"	VARCHAR(5),
                    "TickerSentiment"	float,
                    FOREIGN KEY("CommentID") REFERENCES "Comment"("CommentID"),
                    PRIMARY KEY("TickerID" AUTOINCREMENT)
                ); """

        self.cursor.execute(table)
        self.conn.commit()

    def create_option_table(self):
        table = """CREATE TABLE IF NOT EXISTS "option" (
                    "OptionID"	INTEGER,
                    "TickerID"	INTEGER,
                    "OptType"	VARCHAR(4),
                    "OptStrike"	FLOAT,
                    "OptExpDate"	DATETIME,
                    "OptContracts"	INTEGER,
                    "OptPremium"	FLOAT,
                    PRIMARY KEY("OptionID" AUTOINCREMENT)
                ); """

        self.cursor.execute(table)
        self.conn.commit()

    def insert_into_option_table(self, option_id, ticker_id, option_type, option_strike, option_expiration_date,
                                 option_contracts, option_premium):
        self.cursor.executemany(f"""INSERT INTO option  (OptionID, TickerID, OptType, OptStrike, OptExpDate, 
                                    OptContracts, OptPremium) VALUES(?,?,?,?,?,?,?);""",
                                (option_id, ticker_id, option_type, option_strike,
                                 option_expiration_date, option_contracts,
                                 option_premium,), )
        self.conn.commit()

    def insert_into_row(self, table, data):
        table_info = data.columns.values.tolist()

        values = "? , " * len(table_info)
        columns = ", ".join(table_info)

        data = data.to_records(index=False).tolist()
        self.cursor.executemany(f"""INSERT INTO {table} ({columns}) VALUES({values[:-2]});""", data, )
        self.conn.commit()

    def insert_into_ticker(self, comment_id, ticker, sentiment):
        self.cursor.execute(
            f""" INSERT INTO Ticker (CommentID, TickerSymbol, TickerSentiment) VALUES (?, ?, ?)""",
            (comment_id, str(ticker).upper(), sentiment))
        self.conn.commit()

    def ticker_generation(self):
        loadData = self.cursor.execute("""
                                        SELECT c.comment_id, c.body FROM comment c 
                                        WHERE c.comment_id NOT IN (SELECT t.CommentID FROM ticker t)
                                        """).fetchall()
        wsb = spacy.load(model_loc)
        sia = SentimentIntensityAnalyzer()

        # Add to Ticker DB
        for row in loadData:
            doc = wsb(preprocess(str(row[1])))
            if len(doc.ents) > 0:
                for ticker in doc.ents:
                    self.insert_into_ticker(row[0], ticker, sia.polarity_scores(row[1])['compound'])
            else:
                self.insert_into_ticker(row[0], None, 0)
