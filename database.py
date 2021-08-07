import psycopg2


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            database="WSS", user='postgres', password='123', host='127.0.0.1', port='5432'
        )
        self.cursor = self.conn.cursor()
        self.conn.autocommit = True

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
db.update()
