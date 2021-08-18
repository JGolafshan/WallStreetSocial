import psycopg2
import os


class Database:
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
        files = ["createRedditTableSimplified.txt", "createTickerTable.txt"]
        for i in files:
            try:
                self.createFromExisting(i)
            except psycopg2.Error:
                pass


    def redditDump(self, path):
        with open(path, 'r', encoding='utf-8-sig') as f:
            next(f)
            self.cursor.copy_from(f, 'Reddit', sep=',', columns = ('RedditAuthor','RedditPostDate','RedditText'))

        self.conn.commit()


db = Database()
db.createMerged()