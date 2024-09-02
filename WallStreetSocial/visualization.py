import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from plotly.subplots import make_subplots
from sqlalchemy import func

from WallStreetSocial import database
from database import Ticker, Comment


class SummariseBase:
    def __init__(self, symbol, subreddit=''):
        self.symbol = symbol
        self.subreddit = subreddit
        self.db = database.DatabasePipe()

    def has_symbol(self):
        """
        Checks to see if a symbol exists in the database.
        """
        result = self.db.session.query(Ticker).filter(Ticker.ticker_symbol == self.symbol).first()
        return result is not None

    def summarise_symbol(self):
        """
            Retrieves ticker data including TickerSymbol, created_utc, DAY, and TickerSentiment.
            """
        subquery = (
            self.db.session.query(
                Comment.comment_id,
                Ticker.ticker_symbol,
                Comment.created_utc,
                Ticker.ticker_sentiment
            ).join(
                Ticker, Ticker.comment_id == Comment.comment_id
            ).filter(
                Ticker.ticker_symbol == self.symbol
            ).subquery()
        )

        query = (
            self.db.session.query(
                subquery.c.ticker_symbol,
                subquery.c.created_utc,
                func.strftime('%Y-%m-%d', func.datetime(subquery.c.created_utc, 'unixepoch')).label('DAY'),
                subquery.c.ticker_sentiment
            ).all()
        )

        df = pd.DataFrame(query, columns=["symbol", "utc", "dt", "sentiment"])
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
