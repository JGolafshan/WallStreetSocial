import os
import time
import pandas as pd
from app import app
import datetime as dt
import yfinance as yf
import plotly.express as px
import dash_extensions as de
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from WallStreetSocial import database
from assets.plotly_app_functions import find_common_terms
from dash.dependencies import Input, Output, State


def date_range(year, month, day):
    return html.Div([
        dcc.DatePickerSingle(
            id='my-date-picker-single',
            min_date_allowed=dt.date(1995, 8, 5),
            max_date_allowed=dt.date(dt.date.today().year, dt.date.today().month, dt.date.today().day),
            initial_visible_month=dt.date(2017, 8, 5),
            date=dt.date(year, month, day)
        ),
    ])


dropdown = dbc.DropdownMenu(
    label="Date Selection",
    className="drop_menu",
    group=True,
    children=[
        dbc.Row([html.Div([html.P("Start Date: "), date_range(year=2021, month=1, day=1)])]),
        dbc.Row([html.P("End Date: "), date_range(year=2021, month=1, day=1)])
    ],
)
search_bar = html.Div([
    de.Keyboard(id="keyboard"),
    dbc.Row([
        dbc.Col(dbc.Input(id="submit-val", type="search", placeholder="Search Stock Tickers", )),
    ])
])


@app.callback(Output("url", "pathname"), Input("keyboard", "keydown"), State("submit-val", "value"))
def keydown(event, value):
    time.sleep(1.5)
    if type(event) is not None:
        if event.get("key") == "Enter":
            return "/stock/" + value


def nav_bar():
    return dbc.NavbarSimple(
        id="navbar",
        children=[
            dropdown,
            search_bar

        ])


def grouped_ticker_sentiment(dataframe):
    fig = px.bar(dataframe, y=['Positive Sentiment', 'Negative Sentiment', 'Neutral Sentiment'],
                 x="Symbol", hover_name="Symbol", barmode="stack",
                 color_discrete_sequence=['#00ce48', '#ff2724', '#404040'])

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
        font_color='#ffffff',
        margin=dict(t=20),
    )
    return fig


def line_graph(dataframe):
    fig = px.line(dataframe, x="Date", y="Change", )
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
        legend_title_text="",
        margin=dict(l=0, r=0, b=0, t=10, pad=0),
    )
    fig.update_traces(marker_line_width=0, opacity=0.9)
    fig.update_yaxes(showgrid=True, title=""),
    fig.update_xaxes(showgrid=True, title="")
    return fig


def common_words_table(dataframe):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(dataframe.columns),
                    fill_color='#808080',
                    align='left'),
        cells=dict(values=[dataframe["Word"], dataframe["Count"]],
                   fill_color='rgba(51, 51, 51, 0.5)',
                   align='left'))
    ])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        margin=dict(l=0, r=0, b=0, t=10, pad=0),
    )
    return fig


def graph_body(title, desc, html_element):
    return html.Div([
        html.H5(title, className="stock-graph-title"),
        html.P(desc, className="stock-graph-description"),
        dcc.Graph(figure=html_element, className="stock-graph-graph")
    ], className="stock-container")


# Pages

def landing_page():
    connection = database.DatabasePipe()
    path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/WallStreetSocial/sql_queries/"
    result = connection.cursor.execute(open(file=path + "GroupSentiments.txt").read())
    long_df = pd.DataFrame.from_records(result, columns=['Symbol', 'Positive Sentiment',
                                                         'Negative Sentiment', 'Neutral Sentiment'])
    long_df["Total"] = long_df["Positive Sentiment"] + long_df["Negative Sentiment"] + long_df["Neutral Sentiment"]

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("WSB Sentiment", style={'textAlign': 'center'}),
                dcc.Graph(figure=grouped_ticker_sentiment(long_df.head(25)))
            ], className="spacer")
        ]),
        dbc.Row([
            dbc.Col([
                html.H3("Table of All Mentioned Tickers", style={'textAlign': 'center'}),
                dcc.Graph(figure=stock_table(long_df))
            ], className="spacer")
        ])
    ])


def terminal_page(symbol):
    ticker = yf.Ticker(ticker=symbol)
    history = ticker.history()
    history.reset_index(inplace=True)
    history['Change'] = ((history['Close'] / history['Close'].shift(1)) - 1) * 100

    common_words = find_common_terms(symbol)
    long_df = pd.DataFrame.from_records(common_words, columns=['Word', 'Count']).sort_values(by='Count',
                                                                                             ascending=False)

    return dbc.Container([
        dbc.Row([
            dbc.Col([graph_body("WSB Sentiment", f"{symbol} stock sentiment and popularity", line_graph(history))]),
            dbc.Col([graph_body(f"Common {symbol} Words",
                                f" get a feel for what retail traders are be saying about {symbol}",
                                common_words_table(long_df))])
        ]),
    ])


def error_page(errorType, symbol):
    errorDesc = ""
    if errorType == "stock":
        errorDesc = "Sorry, we cant find the stock: " + symbol

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
