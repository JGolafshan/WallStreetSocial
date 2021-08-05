from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import date
from datetime import datetime as dt
import os
from pprint import pprint

# Alpha Vantage instantiation
av_key = "EPX9O905XDNWU29K"
ts = TimeSeries(key=av_key, output_format="csv")
fd = FundamentalData(key=av_key, output_format="json")

# select stock ticker and create AV objects
stock = "TSLA"
fd_real = fd.get_company_overview(stock).__getitem__(0)
ts_real = ts.get_weekly(stock).__getitem__(0)
ts_real = pd.DataFrame.from_records(ts_real)
pprint(fd_real)

# Dash app instantiation
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css",
                        dbc.themes.GRID,
                        "https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title="Wall-Street Social")

server = app.server
app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# Acaully dash app

app.layout = html.Div(
    className="container-lg",
    children=[

        # Stock Info
        html.Div(
            className="app-header app-adv",
            children=[
                dbc.Row([
                    dbc.Col([html.H2(fd_real.get('Name'))],className="col-2",),
                    dbc.Col([html.H2(fd_real.get('Symbol'))],className="col-2",),
                ], align="baseline"),

                dbc.Row([
                    dbc.Col([
                        html.H5(" TODAY'S CHANGE"),
                        html.H3(" TODAY'S CHANGE")
                    ]),
                    dbc.Col([
                        html.H5("VOLUME"),
                        html.H3("VOLUME")
                    ]),
                    dbc.Col([
                        html.H5("MARKET CAPITALISATION"),
                        html.H3(fd_real.get("MarketCapitalization"))
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

        # Share Fundamentals
        html.Div(
            className="app-adv",
            children=[
                dbc.Row([
                    dbc.Col([
                        html.H4('SHARE INFORMATION')
                    ]),
                    dbc.Col([
                        html.H4('FUNDAMENTALS')
                    ]),

                    dbc.Col([
                        html.H4('DIVIDENDS')
                    ]),
                ], align="baseline"),
            ]),

        # NewsFeed
        html.Div(
            className="app-adv",
            children=[
                dbc.Row([
                    html.H4('NEWS FEED'),
                    dbc.Row([
                        html.P("Blashjsadjadshjsad"),
                        html.P("date: 2021/08/5"),
                    ]),
                ], align="baseline"),

            ]),

        # NewsFeed
        html.Div(
            className="app-adv",
            children=[
                dbc.Row([
                    html.H4('ANNOUNCEMENTS'),
                    dbc.Row([
                        html.P("Blashjsadjadshjsad"),
                        html.P("date: 2021/08/5"),
                    ]),
                ], align="baseline"),

            ]),
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
