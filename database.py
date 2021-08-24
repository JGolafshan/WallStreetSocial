import psycopg2
import os
import pandas.io.sql as sqlio


class Database:
    """"""

    def __init__(self):
        self.conn = psycopg2.connect(
            database="WallStreet-Social", user='postgres', password='123', host='127.0.0.1', port='5432')
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
        files = ["createRedditTableSimplified.txt", "createTickerTable.txt"]
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
