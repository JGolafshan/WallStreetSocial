import dash
import dash_bootstrap_components as dbc

# Dash app instantiation
external_stylesheets = [dbc.themes.GRID,
                        "https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                title="WallStreet Social", suppress_callback_exceptions=True)

server = app.server
