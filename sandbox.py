from WallStreetSocial.backend import reddit
from WallStreetSocial.backend import database

reddit = reddit.RedditPipe()
createDB = database.DatabasePipe()


def redditStack():
    # Pulls comments from reddit and adds them to SQLITE DB
    comments_df = reddit.retrieve_submissions("WallStreetBets", start="2018-08-04", end="2018-08-8")
    final_df = reddit.clean_submissions(comments_df)
    addToDB = createDB.insert_into_comments(final_df)
    return addToDB


def DatabasePipeline():
    # Create DB/Tables
    createDB.table_automation()
    # Pulls comments and adds them to the DB
    redditStack()
    # Finds Tickers
    createDB.ticker_generation()


