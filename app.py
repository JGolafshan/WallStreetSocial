from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import date
from datetime import datetime as dt

# Alpha Vantage instantiation
av_key = "EPX9O905XDNWU29K"
ts = TimeSeries(key=av_key, output_format="csv")
fd = FundamentalData(key=av_key, output_format="json")

# select stock ticker and create AV objects
stock = "IBM"
fd_real = fd.get_company_overview(stock).__getitem__(0)

# Dash app instantiation
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css", dbc.themes.GRID, "E:\WallStreetBets_Analysis\stylesheet.css"]
app = dash.Dash("Wall-Street Social", external_stylesheets=external_stylesheets)
app.title = "Wall-Street Social"

# Acaully dash app
fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])
app.layout = html.Div([
    html.Div([
        dbc.Row([
            dbc.Col([html.P( f"Full Name: {fd_real.get('Name')}")]),
            dbc.Col([html.P(f"Symbol: {fd_real.get('Symbol')}")])
        ], align="baseline"),

        dbc.Row([
            dbc.Col([html.P(f"Asset Type: {fd_real.get('AssetType')}")]),
            dbc.Col([html.P(f"Sector: {fd_real.get('Sector')}")]),
            dbc.Col([html.P(f"Industry Group: {fd_real.get('Industry')}")])
        ], align="baseline")
    ]),
    dcc.Graph(
        id="basic",
        figure=fig
    )
], className="container")

if __name__ == '__main__':
    app.run_server(debug=True)
