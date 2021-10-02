import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
from layouts import layout1, layout2, errorMessage, navbar

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        app.title = "WallStreet Social ● Home"
        layout = [navbar]

        return layout
    elif pathname == '/about-us':

        app.title = "WallStreet Social ● About"
        return layout1

    elif pathname == '/rankings':
        app.title = "WallStreet Social ● Stock Rankings"
        return layout2

    else:
        app.title = "Page Not Found ● WSS "
        layout = [
            navbar, errorMessage]
        return layout


if __name__ == '__main__':
    app.run_server(debug=True, port=3304)
