import psycopg2
import os


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(

            database="WSS", user='postgres', password='123', host='127.0.0.1', port='5432'
        )
        self.cursor = self.conn.cursor()
        self.conn.autocommit = True
        self.dir_name = os.path.dirname(os.path.abspath(__file__))

    def createFromExisting(self, file):
        file = f"{self.dir_name}\dependencies\{file}"
        read_doc = open(file, "r")
        toSQL = read_doc.read()
        return self.cursor.execute(toSQL)

    def createDatabase(self, name):
        sqlCreateDatabase = f"""CREATE database {name} ;"""
        self.cursor.execute(sqlCreateDatabase)

    def createTable(self, tableName):
        create_comment_table = f"""CREATE TABLE public."{tableName}"
                (
                    "{tableName}ID" integer,
                    "{tableName}Date" date,
                    "{tableName}Text" text,
                    PRIMARY KEY ("{tableName}ID")
                ); 
        """
        self.cursor.execute(create_comment_table)

    def update(self, query=
    """"
                    INSERT INTO public."Comments"("CommentsID",  "CommentsText")
                    VALUES (0,  'sssss');
                    """
               ):
        return self.cursor.execute(query)

    def query(self):
        pass


db = Database()
x = db.createFromExisting(file="temp_sql.txt")

print(x)
