from database import Database
import datetime as dt
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

db = Database()
loadData = db.loadCommentBatch(0, 0)
wsb = spacy.load("E:/WallStreetSocial/models/wsb_ner")
sia = SentimentIntensityAnalyzer()

# Add to Ticker DB
for index, row in loadData.iterrows():
    text = row[3]
    doc = wsb(text)
    for en in doc.ents:
        db.cursor.execute(
            f"""
            INSERT INTO public."Ticker" ("CommentID_FK", "TickerSymbol", "TickerSentiment")
            VALUES ({row[0]}, {"'" + str(en).replace("$", "") + "'"}, {sia.polarity_scores(text)['compound']})
            """
        )
        db.conn.commit()
