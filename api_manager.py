from iexfinance import account

api_keys = [
    "pk_294d45992fbb4e8aa325cae768f6468b",
    "pk_f74c2c3a28b04fb6b756bb029766860b"
]

# select stock ticker and create AV objects
symbol = "TSLA"
stock = Stock(symbol, token="pk_294d45992fbb4e8aa325cae768f6468b", output_format="json")

