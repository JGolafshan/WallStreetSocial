import psycopg2
import os
import pandas.io.sql as sqlio
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from models.model_utils.preprocess import preprocess


class Database:
    """"""

    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor()

    def createFromExisting(self, file):
        """"""
        dir_name = os.path.dirname(os.path.abspath(__file__))
        folder = "dependencies"
        file = f"{dir_name}\{folder}\{file}"
        read_doc = open(file, "r")
        to_sql = read_doc.read()
        self.cursor.execute(to_sql)
        self.conn.commit()

    def createMerged(self):
        """"""
        files = ["createRedditCommentsTable.txt", "createTickerTable.txt"]
        for i in files:
            self.createFromExisting(i)

    def redditDump(self, path):
        """"""
        with open(path, 'r', encoding='utf-8-sig') as f:
            next(f)
            self.cursor.copy_from(f, 'Comment', sep=',', columns=('CommentAuthor', 'CommentPostDate', 'CommentText'))
            self.conn.commit()

    def loadCommentBatch(self, before, after):
        """
        Function loads a batch of data from Reddit table for processing. Returns pandas dataframe representing the
        comment data between the specified dates. Dates are input in string format, i.e. '2021-01-01'
        """
        sql = """
        select * 
        from public."Comment"
        """
        query_params = {'before': before, 'after': after}
        return sqlio.read_sql_query(sql, self.conn)

    def generateTickers(self):
        """
        loads data from the redddit table, and generates rows for ticker table
        """
        loadData = self.loadCommentBatch(0, 0)
        wsb = spacy.load("E:/WallStreetSocial/models/wsb_ner")
        sia = SentimentIntensityAnalyzer()

        # Add to Ticker DB
        for index, row in loadData.iterrows():
            text = row[3]
            doc = wsb(preprocess(text))
            for en in doc.ents:
                if (len(doc.ents) >= 1 and row[4] == None):
                    self.cursor.execute(
                        f"""
                            INSERT INTO public."Ticker" ("CommentID_FK", "TickerSymbol", "TickerSentiment")
                            VALUES ({row[0]}, {"'" + str(en).replace("$", "") + "'"}, {sia.polarity_scores(text)['compound']})
                        """
                    )
                    self.cursor.execute(
                        f"""
                            UPDATE public."Comment" 
                            SET "CommentHasTicker" = true
                            WHERE "CommentID" = {row[0]}
                        """
                    )
                    self.conn.commit()
                else:
                    self.cursor.execute(
                        f"""
                            UPDATE public."Comment" 
                            SET "CommentHasTicker" = false
                            WHERE "CommentID" = {row[0]}
                        """
                    )
                    self.conn.commit()