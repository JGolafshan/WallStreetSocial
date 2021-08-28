from database import Database
from ticker import TickerPipe
import datetime as dt

db = Database()
ticker = TickerPipe()

loadData = db.loadCommentBatch(0, 0)

for index, row in loadData.iterrows():
    check_for_tickler = ticker.find_tickers(row[3])
    if len(check_for_tickler) >= 1:

        db.cursor.execute(
            f"""
            INSERT INTO public."Ticker" ("CommentID_FK", "TickerSymbol", "TickerSentiment")
            VALUES ({row[0]}, {str(check_for_tickler[0]).replace("$","")}, {0.0})
            """
        )
        db.conn.commit()
