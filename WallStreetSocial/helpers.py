from WallStreetSocial import database
from pmaw import PushshiftAPI
import datetime as dt
import pandas as pd
import os


class TickerBits(object):
    def __int__(self, symbol='', start_date='', end_date='',
                total_count=0, neutral_count=0, positive_count=0, negative_count=0,
                average_sentiment=0.0, positive_sentiment=0.0, negative_sentiment=0.0,
                positive_vectors=None, negative_vectors=None, cc_vectors=None, daily_bars=None, weekly_bars=None):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

        self.total_count = total_count
        self.neutral_count = neutral_count
        self.positive_count = positive_count
        self.negative_count = negative_count

        self.average_sentiment = average_sentiment
        self.positive_sentiment = positive_sentiment
        self.negative_sentiment = negative_sentiment

        self.positive_vectors = positive_vectors
        self.negative_vectors = negative_vectors
        self.cc_vectors = cc_vectors

        self.daily_bars = daily_bars
        self.weekly_bars = weekly_bars


class SummariseBase(TickerBits):
    def __str__(self):
        to_join = list()
        to_join.append('Symbol: {}'.format(self.symbol))
        to_join.append('Start Date: {}'.format(self.start_date))
        to_join.append('End Date: {}'.format(self.end_date))

        to_join.append('--------------------------------')

        to_join.append('Total Count: {}'.format(self.total_count))
        to_join.append('Neutral Count: {}'.format(self.neutral_count))
        to_join.append('Positive Count: {}'.format(self.positive_count))
        to_join.append('Negative Count: {}'.format(self.negative_count))

        to_join.append('--------------------------------')

        to_join.append('Average Sentiment: {}'.format(self.average_sentiment))
        to_join.append('Positive Sentiment: {}'.format(self.positive_sentiment))
        to_join.append('Negative Sentiment: {}'.format(self.negative_sentiment))

        to_join.append('--------------------------------')

        to_join.append('Positive Related Vectors: {}'.format(self.positive_vectors))
        to_join.append('Negative Related Vectors: {}'.format(self.negative_vectors))
        to_join.append('Cross Contaminated Vectors: {}'.format(self.cc_vectors))

        to_join.append('--------------------------------')
        to_join.append('Daily : {}'.format(self.daily_bars))
        to_join.append('Weekly : {}'.format(self.weekly_bars))

        return '\n'.join(to_join)


def summarise_symbol(symbol):
    db = database.DatabasePipe()
    base = SummariseBase()

    summary_query = f"""
        SELECT t.TickerSymbol,
        (SELECT count(p.TickerSymbol) FROM Ticker p
            WHERE p.TickerSentiment BETWEEN 0.0001 AND 1 AND t.TickerSymbol = p.TickerSymbol) AS [Positive Count],
            
        (SELECT count(p.TickerSymbol) FROM Ticker p
            WHERE p.TickerSentiment BETWEEN -1 AND -0.0001 AND t.TickerSymbol = p.TickerSymbol) AS [Negative Count], 
        
        (SELECT count(p.TickerSymbol) FROM Ticker p
            WHERE p.TickerSentiment is 0 AND t.TickerSymbol = p.TickerSymbol) AS [Neutral Count],
            
        count(*) AS Total,
            
        (SELECT AVG(p.TickerSentiment) FROM Ticker p
            WHERE p.TickerSentiment BETWEEN 0.0001 AND 1 AND t.TickerSymbol = p.TickerSymbol) AS [Positive Sentiment],
            
        (SELECT AVG(p.TickerSentiment) FROM Ticker p
            WHERE p.TickerSentiment BETWEEN -1 AND -0.0001 AND t.TickerSymbol = p.TickerSymbol) AS [Negative Sentiment],
            
        (SELECT AVG(p.TickerSentiment) FROM Ticker p
            WHERE t.TickerSymbol = p.TickerSymbol) AS [AVG Sentiment]
        
    FROM Comment c, Ticker t
    WHERE 
        t.TickerSymbol = '{symbol}' AND t.CommentID = c.comment_id
    """
    query = db.cursor.execute(summary_query).fetchone()

    daily_bars_query = f"""
    
    SELECT t.TickerSymbol, 
            count(*), 
            strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch')) as [DAY]                
            FROM Comment c, Ticker t
            WHERE t.TickerSymbol = "{symbol}" AND t.CommentID = c.comment_id
            GROUP BY DAY
    """
    query_2 = db.cursor.execute(daily_bars_query).fetchall()

    base.symbol = query[0]
    base.start_date = ''
    base.end_date = ''

    base.positive_count = query[1]
    base.negative_count = query[2]
    base.neutral_count = query[3]
    base.total_count = query[4]
    base.positive_sentiment = query[5]
    base.negative_sentiment = query[6]
    base.average_sentiment = query[7]

    base.positive_vectors = None
    base.negative_vectors = None
    base.cc_vectors = None

    base.daily_bars = query_2
    base.weekly_bars = query_2

    return base


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
    dir_name = os.path.dirname(os.path.dirname(__file__))
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
