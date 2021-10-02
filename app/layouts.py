import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from assets import plotly_app_functions as func

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", className="ml-2", n_clicks=0
            ),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("About Us", href="/about-us")),
        dbc.NavItem(dbc.NavLink("Rankings", href="/rankings")),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True, is_open=False),
    ],
    brand="Wall Street Social",
    brand_href="/",
    sticky="top",
)


def Error(errorType, symbol):
    errorDesc = ""
    if errorType == "stock":
        errorDesc = "Sorry, we cant find "+symbol

    if errorType == "url":
        errorDesc = "Sorry, an error occurred with our website"

    errorMessage = html.Div(
        className="errorDisplay",
        children=[
            html.H1("Oops!"),
            html.H3("Something went wrong"),
            html.H5(errorDesc),
            html.P(dbc.Button("Go Back", color="dark", href="/"), className="mr-1"),
        ])
    return errorMessage


def Stock(symbol):
    stock = func.tickerResults(symbol)
    return html.Div(
        className="",
        children=[
            # Stock Info
            html.Div(className="company-header", children=[
                html.Div(className="container container-md", children=[
                    dbc.Row([
                        html.Tr([
                            html.Th([html.H1(stock[2].get('shortName'))]),
                            html.Th([html.H2(stock[2].get('symbol'))]),
                        ]),

                    ], align="baseline", className="remove-distance", ),

                    html.Div(className="row standard", children=[
                        html.Dl(className="dl dl-lg col-md-3 col-sm-5 ", children=[
                            html.Dt(["Last Price / Today's Change"]),
                            html.Tr([
                                html.Th([html.Dd(className="price",
                                                 children=["$" + str(round(stock[2].get('regularMarketPrice'), 2))])]),
                                html.Th([html.Dd(className="price_info", children=[stock[0]])]),
                                html.Th([html.Dd(className="price_info", children=[f"({stock[1]})%"])]),
                            ]),
                        ]),

                        html.Dl(className="dl dl-lg col-md-3 col-sm-5 ", children=[
                            html.Dt(["VOLUME"]),
                            html.Dd(className="price_info",
                                    children=[f"{func.millify(stock[2].get('regularMarketVolume'))}"])
                        ]),

                        html.Dl(className="dl dl-lg col-md-3 col-sm-5 ", children=[
                            html.Dt(["MARKET CAPITALISATION"]),
                            html.Dd(className="price_info", children=[f"{func.millify(stock[2].get('marketCap'))}"])
                        ])
                    ]),
                    html.Div(className="row standard", children=[
                        html.Dl(className="dl dl-lg col-md-3 col-sm-5 ", children=[
                            html.Dt([f"{stock[2].get('sector')}: {stock[2].get('industry')}"]),
                        ]),
                    ]),

                ]),
            ]),
            # Stock Graph
            html.Div(
                className="graph container-md",
                children=[
                    dcc.Graph(
                        id="basic",
                        figure=go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])
                    )]),
        ])
