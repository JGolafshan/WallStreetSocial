from matplotlib import pyplot as plt
from WallStreetSocial import database
from pmaw import PushshiftAPI
import yfinance as yf
import datetime as dt
import pandas as pd
import os


class SummariseBase:
    def __init__(self, symbol, subreddit='', start_date='', end_date=''):
        self.symbol = symbol
        self.subreddit = subreddit
        self.start_date = start_date
        self.end_date = end_date
        self.db = database.DatabasePipe()

    def has_symbol(self):
        """
        checks to see if a symbol exists
        """
        db = database.DatabasePipe()
        symbol_query = f"""SELECT DISTINCT(TickerSymbol) FROM ticker WHERE TickerSymbol = "{self.symbol}" """
        symbols = db.cursor.execute(symbol_query).fetchall()

        if symbols is None or len(symbols) == 0:
            return False

        else:
            return True

    def summarise_symbol(self):
        query = f"""SELECT TickerSymbol, created_utc,  
                    strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch')) as [DAY],TickerSentiment
                    FROM Comment c, Ticker t
                    WHERE t.TickerSymbol = "{self.symbol}" AND t.CommentID = c.comment_id
                    AND DAY Between {self.start_date} AND {self.end_date}"""

        return_values = self.db.cursor.execute(query).fetchall()

        df = pd.DataFrame(return_values, columns=["symbol", "utc", "dt", "sentiment"])
        df.set_index("dt", inplace=True)

        total_count = df.groupby('dt')['sentiment'].count().reset_index(name="Total Count")
        pos_count = df.groupby('dt')['sentiment'].apply(lambda x: (x > 0).sum()).reset_index(name="Positive Count")
        neg_count = df.groupby('dt')['sentiment'].apply(lambda x: (x < 0).sum()).reset_index(name="Negative Count")
        neutral_count = df.groupby('dt')['sentiment'].apply(lambda x: (x == 0).sum()).reset_index(name="Neutral Count")
        pos_sentiment = df.groupby('dt')['sentiment'].apply(lambda x: x.mean()).reset_index(name="AVG Sentiment")

        df_resized = pd.DataFrame(data=pos_count)
        df_resized["Negative Count"] = neg_count["Negative Count"]
        df_resized["Neutral Count"] = neutral_count["Neutral Count"]
        df_resized["Total Count"] = total_count["Total Count"]
        df_resized["Average Sentiment"] = pos_sentiment["AVG Sentiment"]
        return df_resized

    def display_stats(self):
        symbol_history = yf.Ticker(self.symbol).history(start=self.start_date, end=self.end_date)
        data_df = self.summarise_symbol()

        # Word Graph
        fig = plt.figure()
        gs = fig.add_gridspec(3, hspace=0.4)
        axs = gs.subplots(sharex=True)

        #fig.suptitle(f'{self.symbol} Stock between the {self.start_date} and {self.end_date}')

        axs[1].set_title("Stock Sentiment")
        axs[1].plot(data_df["Average Sentiment"], label="Average Sentiment")
        axs[1].legend()

        plt.show()


def unique_symbols():
    """
    list of every unique symbol
    Returns: a list of every unique symbol

    """
    db = database.DatabasePipe()
    symbol_query = """SELECT DISTINCT(TickerSymbol) FROM ticker"""
    symbols = db.cursor.execute(symbol_query).fetchall()
    return [x for sublist in symbols for x in sublist]


def validate_model(path):
    """
    checks to see if the user has specified a path for the model
    """
    if database.model_loc == '':
        exit("model has no location - please use this link to download the model\n"
             "https://github.com/JGolafshan/WallStreetSocial/blob/master/wsb_ner.zip")
    elif os.path.isdir(path) is False:
        exit("could not find path")

    database.model_loc = path
    print("Model Found!")
    return database.model_loc


def convert_date(date):
    """
    Description:
        converts a date/datetime to a unix timestamp so that Pushshift can understand it
    Parameters:
        date (str): takes a date-time, example 'YEAR-MONTH-DAY HOUR:MINUTE:SECOND'
    Returns:
        Returns a unix timestamp
    """

    datetime = str(date).split(" ")
    if len(datetime) == 1:
        datetime = datetime[0] + " 00:00:00"
    else:
        datetime = date

    return int(dt.datetime.strptime(datetime, '%Y-%m-%d %H:%M:%S').timestamp())


def log_submissions(df):
    """
    Description:
        Converts a dataframe to CSV which is saved for logging/debugging purposes.
            Which can be found in /dependencies/logs
    Parameters:
        df (dataframe): takes a date-time, example 'YEAR-MONTH-DAY HOUR:MINUTE:SECOND'
    Returns:
        Returns a unix timestamp
    """
    dir_name = os.path.dirname(os.getcwd())
    folder = 'temp'
    file_name = 'wsb_comments_' + dt.datetime.now().strftime("%Y_%m_%d_%I_%M")
    path = f"{dir_name}\{folder}\{file_name}.csv"
    df.to_csv(path, encoding='utf-8-sig', index=False)
    return path


def run(subreddits, start, end):
    start = convert_date(start)
    end = convert_date(end)
    api = PushshiftAPI(shards_down_behavior="None")
    db = database.DatabasePipe()
    db.create_database()

    print("fetching posts in the data range")
    posts = api.search_submissions(subreddit=subreddits, before=end, after=start)
    posts_df = pd.DataFrame(posts.responses)
    posts_df = posts_df.filter(["author", "subreddit", "url", "title", "created_utc", "score"])
    db.insert_into_row("post", posts_df)

    print("fetching comments in the data range")
    comments = api.search_comments(subreddit=subreddits, before=end, after=start)
    comment_df = pd.DataFrame(comments.responses)
    comment_df = comment_df.filter(["permalink", "subreddit", "author", "body", "score", "created_utc"])
    db.insert_into_row("comment", comment_df)

    db.ticker_generation()
