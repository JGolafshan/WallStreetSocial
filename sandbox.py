from WallStreetSocial.backend import reddit
from WallStreetSocial.backend import database
from pprint import pprint
reddit = reddit.RedditPipe()
createDB = database.DatabasePipe()


def redditStack():
    # Pulls comments from reddit and adds them to SQLITE DB
    comments_df = reddit.retrieve_submissions("WallStreetBets", start="2019-09-02 8:30:00", end="2019-09-02 9:00:00")
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


DatabasePipeline()

# createDB.table_automation()
# data = {'id': ['hmu1223a', 'hmu1224a', 'hmu1231'],
#         'created_utc': ['2021-02-02 12:02:02', '2021-02-02 12:05:02', '2021-02-02 12:05:02'],
#         'body': ['Man, TSLA really feels like its headed to a large jump, have you seen the fundamentals',
#                  'Sell TSLA, Buy GME', 'I Dont like that stock']}
#
# df = pd.DataFrame(data)
# sql = createDB.insert_into_comments(df)
# createDB.ticker_generation()
pprint(createDB.cursor.execute("SELECT * FROM Comment").fetchall())
pprint(createDB.cursor.execute("SELECT * FROM Ticker").fetchall())
