import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

layout1 = html.Div([
    html.H3('App 1'),
    dcc.Dropdown(
        id='app-1-dropdown',
        options=[
            {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    html.Div(id='app-1-display-value'),
    dcc.Link('Go to App 2', href='/apps/app2')
])

layout2 = html.Div([
    html.H3('App 2'),
    dcc.Dropdown(
        id='app-2-dropdown',
        options=[
            {'label': 'App 2 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    html.Div(id='app-2-display-value'),
    dcc.Link('Go to App 1', href='/apps/app1')
])

errorMessage = html.Div(
    className="errorDisplay",
    children=[
            html.H1("Oops!"),
            html.H3("Something went wrong"),
            html.H5("Sorry, an error occurred with our website"),
            html.P(dbc.Button("Go Back", color="dark", href="/"), className="mr-1"),
    ])
