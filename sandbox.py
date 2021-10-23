import database
import reddit


# Pulls comments froms reddit and adds them to SQLITE DB
reddit = reddit.RedditPipe()
def redditStack():
    comments_df = reddit.get_reddit_comments("WallStreetBets", start=1634378400, end=1634378900)
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

# Print The Tables
print(createDB.cursor.execute("SELECT * FROM Ticker").fetchall())
print(createDB.cursor.execute("SELECT * FROM Comment").fetchall())
