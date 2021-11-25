import math
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

def find_common_terms():
    pass