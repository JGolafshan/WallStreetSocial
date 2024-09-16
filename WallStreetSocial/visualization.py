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
        Create a simple interactive view from the data.
        """
        df = self.summarise_symbol()
        history = yf.Ticker(self.symbol).history(start=df.index[0], end=df.index[-1])

        fig = make_subplots(rows=3, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.1,
                            subplot_titles=["Mentions by Sentiment", "Stock Price", "Average Sentiment"])

        # Mentions by sentiment (stacked bar chart)
        trace_pos = go.Bar(name="Positive", x=df.index, y=df["Positive Count"], marker_color='green')
        trace_neg = go.Bar(name="Negative", x=df.index, y=df["Negative Count"], marker_color='red')
        trace_neutral = go.Bar(name="Neutral", x=df.index, y=df["Neutral Count"], marker_color='gray')

        # Stock price (line chart)
        trace_price = go.Scatter(x=history.index, y=history["Close"], mode='lines', name=f"{self.symbol} Price",
                                 line=dict(color='blue'))

        # Average sentiment (line chart)
        trace_sentiment = go.Scatter(x=df.index, y=df["Average Sentiment"], mode='lines+markers',
                                     name="Average Sentiment", line=dict(color='orange'))

        # Add traces to figure
        fig.add_trace(trace_pos, row=1, col=1)
        fig.add_trace(trace_neg, row=1, col=1)
        fig.add_trace(trace_neutral, row=1, col=1)
        fig.add_trace(trace_price, row=2, col=1)
        fig.add_trace(trace_sentiment, row=3, col=1)

        # Update layout for better visualization
        fig.update_layout(barmode='stack', title_text=f"Summary for {self.symbol}", height=800,
                          xaxis=dict(type='category'),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

        fig.update_yaxes(title_text="Mentions", row=1, col=1)
        fig.update_yaxes(title_text="Stock Price (USD)", row=2, col=1)
        fig.update_yaxes(title_text="Average Sentiment", row=3, col=1)

        fig.update_xaxes(title_text="Date")

        # Show the figure
        fig.show()
