# Imports
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect apps here
from apps import home
from apps import test
from apps import dashboard_oldapp


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Home|', href='/apps/home'),
        dcc.Link('Test|', href='/apps/test'),
        dcc.Link('Dashboard', href='/apps/dashboard_oldapp'),
    ], className="row"),
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/home':
        return home.layout
    if pathname == '/apps/test':
        return test.layout
    if pathname == '/apps/dashboard_oldapp':
        return dashboard_oldapp.layout
    else:
        return "404 Page Error! Please choose a link"


if __name__ == '__main__':
    app.run_server(debug=False)