import math
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from WallStreetSocial.backend import database


def millify(n):
    millnames = ['', ' K', ' M', ' B', ' T']
    n = float(n)
    if n == 0:
        return 0
    else:
        millidx = max(0, min(len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
        return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])


def verifyStockInput(symbol):
    connection = database.DatabasePipe()
    result = connection.cursor.execute(
        f"""
            SELECT DISTINCT TickerSymbol
            FROM Ticker
            WHERE TickerSymbol != "NONE" AND TickerSymbol = '{symbol}';
        """
    ).fetchone()
    if result is None:
        return False

    elif len(result) == 1:
        return True


def find_common_terms(symbol):
    db = database.DatabasePipe()
    query = db.cursor.execute(f"""
    SELECT 
       t.TickerSymbol,
       c.CommentText
    FROM Ticker t INNER JOIN Comment c
    ON t.CommentID = c.CommentID
    WHERE t.TickerSymbol ="{symbol}";
    """).fetchall()
    en_stops = set(stopwords.words('english'))
    list1 = []

    for comment in query:
        word_list = word_tokenize(comment[1])
        for word in word_list:
            word_removed = False

            if len(word) <= 2:
                word_removed = True

            if word in en_stops:
                word_removed = True

            if word_removed is True:
                break
            else:
                list1.append(word)

    uniques_values = np.unique(list1)
    final_list = []
    for i in range(0, len(uniques_values)):
        final_list.append((uniques_values[i], list1.count(uniques_values[i])))
    return final_list
