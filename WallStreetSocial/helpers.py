from WallStreetSocial import database
from pmaw import PushshiftAPI
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import datetime as dt
import pandas as pd
import os


class SummariseBase:
    def __init__(self, symbol, subreddit=''):
        self.symbol = symbol
        self.subreddit = subreddit
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
                    """

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
        """
        create a simple interactive view from the data
        """

        df = self.summarise_symbol()
        history = yf.Ticker(self.symbol).history(start=df["dt"][0], end=df["dt"][len(df.index) - 1])

        fig = make_subplots(rows=4, cols=2,
                            specs=[[{"colspan": 2}, None],
                                   [{"colspan": 2}, None],
                                   [{"colspan": 2}, None],
                                   [{"colspan": 1}, {"colspan": 1}]],
                            subplot_titles=["Mentions", "Stock Price", "Sentiment"],
                            row_heights=[2, 2, 1, 0])

        trace_1 = go.Bar(name="Positive Count", x=df["dt"], y=df["Positive Count"], offsetgroup=0)
        trace_2 = go.Bar(name="Negative Count", x=df["dt"], y=df["Negative Count"], offsetgroup=0,
                         base=df["Positive Count"])
        trace_3 = go.Bar(name="Neutral Count", x=df["dt"], y=df["Neutral Count"], offsetgroup=0,
                         base=df["Negative Count"] + df["Positive Count"])

        yf_trace = go.Scatter(x=history.index, y=history["Open"], name=f"{self.symbol} Price")
        sentiment = go.Scatter(x=df["dt"], y=df["Average Sentiment"], name="Sentiment")

        fig.add_trace(trace_1, 1, 1)
        fig.add_trace(trace_2, 1, 1)
        fig.add_trace(trace_3, 1, 1)
        fig.add_trace(yf_trace, 2, 1)
        fig.add_trace(sentiment, 3, 1)
        fig.update_layout(showlegend=False)
        fig.update_layout()
        fig.show()


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
    if os.path.isdir(path) is False:
        exit("could not find path")
    else:
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
    """
    Fetches comments and posts from a subreddit between a date range
    adds it to the database,
    then it create tick entries inside the ticker table
    """
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
