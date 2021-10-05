import database
import psycopg2

conn = psycopg2.connect(database="WallStreet-Social",
                        user='postgres',
                        password='123',
                        host='127.0.0.1',
                        port='5432')

databse = database.Database(conn=conn)
print(databse.loadCommentBatch(0, 0))
