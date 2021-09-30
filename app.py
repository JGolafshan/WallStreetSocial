import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from assets import plotly_app_functions as func

# Dash app instantiation
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css",
                        dbc.themes.GRID,
                        "https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, title="Wall-Street Social")

# Acaully dash app

app.layout = html.Div(
    className="",
    children=[

        # Stock Info
        html.Div(className="company-header", children=[
            html.Div(className="container container-md", children=[
                dbc.Row([
                    html.Tr([
                        html.Th([html.H1(func.ticker_info.get('shortName'))]),
                        html.Th([html.H2(func.ticker_info.get('symbol'))]),
                    ]),

                ], align="baseline", className="remove-distance", ),

                html.Div(className="row standard", children=[
                    html.Dl(className="dl dl-lg col-md-3 col-sm-5 ", children=[
                        html.Dt(["Last Price / Today's Change"]),
                        html.Tr([
                            html.Th([html.Dd(className="price",
                                             children=["$" + str(round(func.ticker_info.get('regularMarketPrice'), 2))])]),
                            html.Th([html.Dd(className="price_info", children=[func.change])]),
                            html.Th([html.Dd(className="price_info", children=[f"({func.change_percentage})%"])]),
                        ]),
                    ]),

                    html.Dl(className="dl dl-lg col-md-3 col-sm-5 ", children=[
                        html.Dt(["VOLUME"]),
                        html.Dd(className="price_info", children=[f"{func.millify(func.ticker_info.get('regularMarketVolume'))}"])
                    ]),

                    html.Dl(className="dl dl-lg col-md-3 col-sm-5 ", children=[
                        html.Dt(["MARKET CAPITALISATION"]),
                        html.Dd(className="price_info", children=[f"{func.millify(func.ticker_info.get('marketCap'))}"])
                    ])
                ]),
                html.Div(className="row standard", children=[
                    html.Dl(className="dl dl-lg col-md-3 col-sm-5 ", children=[
                        html.Dt([f"{func.ticker_info.get('sector')}: {func.ticker_info.get('industry')}"]),
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

        html.Div(className="company-info", children=[
            html.Div(className="container container-md", children=[
                html.Div(className="container container-md", children=[
                    html.Div(className="col-xs-12 col-md-6 col-lg-4", children=[
                        html.Table(className="col-xs-12 col-md-6 col-lg-4", children=[
                            html.H3(className="key_stats_title", children=["Share Infomation"]),
                            html.Tbody([
                                html.Tr([
                                    html.Th([]),
                                    html.Td([]),
                                ])
                            ])
                        ])
                    ])
                ])
            ]),
        ]),
        # NewsFeed
        html.Div(
            className="",
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
