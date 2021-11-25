import os
import time
import datetime as dt
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash_extensions import Keyboard
from WallStreetSocial.backend import database
from app import app

# Elements

def search_bar():
    return html.Div([
        Keyboard(id="keyboard"),
        dbc.Row([
            dbc.Col(
                dbc.Input(id="submit-val", type="search", placeholder="Search Stock Tickers", className="search_bar")),
        ],
            className="w-25 mx-auto",
            align="center",
        )
    ])


def date_picker():
    return html.Div([
        dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=dt.date(1995, 8, 5),
            max_date_allowed=dt.date(dt.date.today().year, dt.date.today().month, dt.date.today().day),
            initial_visible_month=dt.date(2017, 8, 5),
            end_date=dt.date(2017, 8, 25),
            start_date=dt.date(2017, 8, 25)
        ),
    ])


def navbar():
    return html.Div([
        dbc.Col([
            search_bar(),
            date_picker()
        ])
    ], className="nav_bar")


@app.callback(
    Output('output-container-date-picker-range', 'children'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output(start_date, end_date):
    if start_date is not None:
        start_date_object = dt.date.fromisoformat(start_date)
    if end_date is not None:
        end_date_object = dt.date.fromisoformat(end_date)


def grouped_ticker_sentiment(dataframe):
    fig = px.bar(dataframe, y=['Positive Sentiment', 'Negative Sentiment', 'Neutral Sentiment'],
                 x="Symbol", hover_name="Symbol", barmode="stack",
                 color_discrete_sequence=['#00ce48', '#ff2724', '#404040'], title="WallStreetBets Ticker Sentiment")

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#7b7d7e',
        width=800,
        font=dict(size=9, ),
        bargap=0.4,
        title=dict(yanchor="top", y=0.95, x=0.5, xanchor="center"),
        title_font=dict(size=20, color="#ffffff"),
        legend=dict(orientation="h", yanchor="top", y=1.1, x=0.5, xanchor="center"),
        legend_title_text=""
    )
    fig.update_traces(marker_line_width=0, opacity=0.9)
    fig.update_yaxes(showgrid=False, title="", ),
    fig.update_xaxes(showgrid=False, title="", tickangle=-40, tickfont=dict(size=10, color="#ffffff"))
    return fig


def stock_table(dataframe):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(dataframe.columns),
                    fill_color='#808080',
                    align='left'),
        cells=dict(values=[dataframe["Symbol"], dataframe["Positive Sentiment"], dataframe["Negative Sentiment"],
                           dataframe["Neutral Sentiment"], dataframe["Total"]],
                   fill_color='rgba(51, 51, 51, 0.5)',
                   align='left'))
    ])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff'
    )
    return fig


@app.callback(Output("url", "pathname"), Input("keyboard", "keydown"), State("submit-val", "value"))
def keydown(event, value):
    time.sleep(1.5)
    if type(event) is not None:
        if event.get("key") == "Enter":
            return "/stock/" + value


# Pages

def page_landing():
    connection = database.DatabasePipe()
    path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/WallStreetSocial/sql_queries/"
    result = connection.cursor.execute(open(file=path + "GroupSentiments.txt").read())
    long_df = pd.DataFrame.from_records(result, columns=['Symbol', 'Positive Sentiment',
                                                         'Negative Sentiment', 'Neutral Sentiment'])
    long_df["Total"] = long_df["Positive Sentiment"] + long_df["Negative Sentiment"] + long_df["Neutral Sentiment"]
    content = dbc.Container(
        className="container", children=[
            html.Div([
                dcc.Graph(id='example-graph-2', figure=grouped_ticker_sentiment(long_df.head(15)))
            ], className="center-block"),
            html.Div([
                dcc.Graph(id='example-graph-2', figure=stock_table(long_df))
            ], className="")
        ])
    return content


# graph-single
def page_error(errorType, symbol):
    errorDesc = ""
    if errorType == "stock":
        errorDesc = "Sorry, we cant find " + symbol

    if errorType == "url":
        errorDesc = "Sorry, an error occurred with our website"

    errorMessage = html.Div(
        className="errorDisplay",
        children=[
            html.H1("Oops!"),
            html.H3("Something went wrong"),
            html.H5(errorDesc),
            html.P(dbc.Button("Go Back", color="light", href="/"), className="mr-1"),
        ])
    return errorMessage
