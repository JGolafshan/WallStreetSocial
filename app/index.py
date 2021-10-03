import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from layouts import Error, navbar, Stock, LandingPage, Loading
from assets import plotly_app_functions as funcs

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        app.title = "WallStreet Social ● Home"
        layout = [navbar, LandingPage()]
        return layout

    elif "/stock/" in pathname:
        getTicker = pathname.split("/")
        symbol = getTicker[2]
        check = funcs.verifyStockInput(symbol)

        if check is True:
            layout = [navbar, Stock(symbol)]
            return layout
        else:
            layout = [navbar, Error("stock", symbol)]
            return layout

    elif pathname == '/about-us':
        app.title = "WallStreet Social ● About"
        return "about us"

    elif pathname == '/rankings':
        app.title = "WallStreet Social ● Stock Rankings"
        return "rankings"

    else:
        app.title = "Page Not Found ● WSS "
        layout = [navbar, Error("url", None)]
        return layout


if __name__ == '__main__':
    app.run_server(debug=True, port=3304)
