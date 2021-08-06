import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import yfinance as yf
from pprint import pprint


symbol = "TSLA"
ticker = yf.ticker.Ticker(ticker=symbol)

ticker_info = ticker.info
pprint(ticker_info)
# Dash app instantiation
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css",
                        dbc.themes.GRID,
                        "https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title="Wall-Street Social")

# Acaully dash app

app.layout = html.Div(
    className="container-lg",
    children=[

        # Stock Info
        html.Div(
            className="app-header app-adv",
            children=[
                dbc.Row([
                    dbc.Col([html.H2(ticker_info.get('shortName'))], className="col-2", ),
                    dbc.Col([html.H2(ticker_info.get('symbol'))], className="col-2", ),
                ], align="baseline"),

                dbc.Row([
                    dbc.Col([
                        html.H5(" TODAY'S CHANGE"),
                        dbc.Row([
                            dbc.Col([html.H3(f"{ticker_info.get('regularMarketPrice')}")]),
                            dbc.Col([html.H3(f"{round(ticker_info.get('regularMarketPrice')-ticker_info.get('regularMarketPreviousClose'),3)} ")]),
                            dbc.Col([html.H3(f"{round(ticker_info.get('regularMarketPrice') - ticker_info.get('regularMarketPreviousClose'), 3)*100} ")]),
                        ]),

                    ]),
                    dbc.Col([
                        html.H5("VOLUME"),
                        html.H3(f"{ticker_info.get('regularMarketVolume')}")
                    ]),
                    dbc.Col([
                        html.H5("MARKET CAPITALISATION"),
                        html.H3(f"{ticker_info.get('marketCap')}")
                    ])
                ]),
            ]),

        # Stock Graph
        html.Div(
            className="graph",
            children=[
                dcc.Graph(
                    id="basic",
                    figure=go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])
                )]
        ),
        # NewsFeed
        html.Div(
            className="apps-change",
            children=[
                dbc.Row([
                    dbc.Col([
                        html.H4('NEWS FEED'),
                        dbc.Row([
                            html.P("Blashjsadjadshjsad"),
                            html.P("date: 2021/08/5"),
                        ]),
                    ]),
                    dbc.Col([
                        html.H4('ANNOUNCEMENTS'),
                        dbc.Row([
                            html.P("Blashjsadjadshjsad"),
                            html.P("date: 2021/08/5"),
                        ]),
                    ])
                    ], align="baseline")
            ]),
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
