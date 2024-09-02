import os
import spacy
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from WallStreetSocial.preprocess import preprocess

model_loc = "C:\\Users\\JGola\\Documents\\GitHub\\WallStreetSocial\\wsb_ner\\wsb_ner"

Base = declarative_base()


class Comment(Base):
    __tablename__ = 'comment'
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    permalink = Column(String)
    subreddit = Column(String)
    author = Column(String)
    body = Column(String)
    score = Column(String)
    created_utc = Column(String)


class Post(Base):
    __tablename__ = 'post'
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    author = Column(String)
    subreddit = Column(String)
    url = Column(String)
    title = Column(String)
    created_utc = Column(String)
    score = Column(String)


class Ticker(Base):
    __tablename__ = 'ticker'
    ticker_id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(Integer, ForeignKey('comment.comment_id'))
    ticker_symbol = Column(String(5))
    ticker_sentiment = Column(Float)
    comment = relationship("Comment", back_populates="tickers")


class Option(Base):
    __tablename__ = 'option'
    option_id = Column(Integer, primary_key=True, autoincrement=True)
    ticker_id = Column(Integer, ForeignKey('ticker.ticker_id'))
    opt_type = Column(String(4))
    opt_strike = Column(Float)
    opt_exp_date = Column(DateTime)
    opt_contracts = Column(Integer)
    opt_premium = Column(Float)
    ticker = relationship("Ticker", back_populates="options")


Comment.tickers = relationship("Ticker", order_by=Ticker.ticker_id, back_populates="comment")
Ticker.options = relationship("Option", order_by=Option.option_id, back_populates="ticker")


class DatabasePipe:
    def __init__(self):
        base_folder = os.path.dirname(os.path.abspath(os.curdir))
        db_path = os.path.join(base_folder, 'WallStreetBets.db')
        self.engine = create_engine(f'sqlite:///{db_path}')

        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def insert_into_option_table(self, option_id, ticker_id, option_type, option_strike, option_expiration_date,
                                 option_contracts, option_premium):
        new_option = Option(option_id=option_id, ticker_id=ticker_id, opt_type=option_type,
                            opt_strike=option_strike, opt_exp_date=option_expiration_date,
                            opt_contracts=option_contracts, opt_premium=option_premium)
        self.session.add(new_option)
        self.session.commit()

    def insert_into_row(self, table, data):
        self.session.bulk_insert_mappings(table, data)
        self.session.commit()

    def insert_into_ticker(self, comment_id, ticker, sentiment):
        new_ticker = Ticker(comment_id=comment_id, ticker_symbol=str(ticker).upper(), ticker_sentiment=sentiment)
        self.session.add(new_ticker)
        self.session.commit()

    def ticker_generation(self):
        loadData = self.session.query(Comment.comment_id, Comment.body).filter(
            ~Comment.comment_id.in_(self.session.query(Ticker.comment_id))
        ).all()

        wsb = spacy.load(model_loc)
        sia = SentimentIntensityAnalyzer()

        for row in loadData:
            doc = wsb(preprocess(str(row.body)))
            if len(doc.ents) > 0:
                for ticker in doc.ents:
                    self.insert_into_ticker(row.comment_id, ticker, sia.polarity_scores(row.body)['compound'])
            else:
                self.insert_into_ticker(row.comment_id, None, 0)

    def unique_symbols(self):
        """
        list of every unique symbol
        Returns: a list of every unique symbol

        """
        symbols = self.session.query(Ticker.ticker_symbol).distinct().all()
        return [symbol[0] for symbol in symbols]