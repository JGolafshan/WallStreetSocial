import database
import reddit


# Pulls comments froms reddit and adds them to SQLITE DB
reddit = reddit.RedditPipe()
def redditStack():
    comments_df = reddit.get_reddit_comments("WallStreetBets", start="2020-01-02 10:02:00", end="2020-01-03 10:02:00")
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
