import psycopg2
import os


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(

        database = 'WallStreet-Social',user='postgres', password='123', host='127.0.0.1', port='5432'
        )
        self.cursor = self.conn.cursor()
        self.conn.autocommit = True
        self.dir_name = os.path.dirname(os.path.abspath(__file__))

    def createFromExisting(self, file):
        """"""
        file = f"{self.dir_name}\dependencies\{file}"
        read_doc = open(file, "r")
        toSQL = read_doc.read()
        return self.cursor.execute(toSQL)

    def createMerged(self):
        files = ["createRedditTableSimplified.txt", "createTickerTable.txt"]

        for i in files:
            try:
                self.createFromExisting(i)
            except psycopg2.Error:
                pass

    def redditDump(self, conn, cur, path):
        with open(path, 'r', encoding='utf-8-sig') as f:
            next(f)
            cur.copy_from(f, 'Reddit', sep=',')

        conn.commit()


    def update(self, query):
        """"""
        query = """"INSERT INTO public."Comments"("CommentsID",  "CommentsText")
                VALUES (0,  'sssss');"""
        return self.cursor.execute(query)

    def query(self):
        """"""
        pass


db = Database()


db.createMerged()
