from app import app
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from layouts import nav_bar, landing_page, terminal_page
from assets import plotly_app_functions as funcs


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):

    if pathname == '/':
        app.title = "WallStreet Social"
        layout = [nav_bar(), landing_page()]
        return layout

    elif "/stock/" in pathname:
        getTicker = pathname.split("/")
        symbol = getTicker[2]
        check = funcs.verifyStockInput(symbol)

        if check is True:
            layout = [nav_bar(), terminal_page(symbol)]
            return layout
        else:
            layout = []
            return layout
    else:
        layout = []
        return layout


if __name__ == '__main__':
    app.run_server(debug=True, port=3304)
