from WallStreetSocial.backend import reddit
from WallStreetSocial.backend import database


# Pulls comments froms reddit and adds them to SQLITE DB
reddit = reddit.RedditPipe()
def redditStack():
    comments_df = reddit.get_reddit_comments("WallStreetBets", start="2019-09-02 10:02:00", end="2019-09-02 10:06:00")
    final_df = reddit.create_final_dataframe(comments_df)
    sql = createDB.insert_into_comments(final_df)
    return sql


createDB = database.DatabasePipe()
def DatabasePipeline():
    # Create DB/Tables
    createDB.table_automation()
    # Pulls comments and adds them to the DB
    redditStack()
    # Finds Tickers
    createDB.insert_into_ticker()

DatabasePipeline()

print(createDB.cursor.execute("SELECT * FROM Ticker").fetchall())
print(createDB.cursor.execute("SELECT * FROM Comment").fetchall())
