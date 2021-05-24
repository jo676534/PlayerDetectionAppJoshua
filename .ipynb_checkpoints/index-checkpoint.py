# Imports
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect apps here
from apps import home
from apps import test
from apps import dashboard

navbar = dbc.NavbarSimple(
    children=[

        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Home josh", header=True),
                dbc.DropdownMenuItem("Video Trimming", href="#"),
                dbc.DropdownMenuItem("Next Phase", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="HOME",
        ),
    ],
    brand="General NavBar",
    brand_href="#",
    color="#6A6A6A",
    dark=True,
    brand_style={"margin-left": "-160px"},
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div([
        dcc.Link('Home|', href='/apps/home'),
        dcc.Link('Test|', href='/apps/test'),
        dcc.Link('Dashboard', href='/apps/dashboard'),
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
    if pathname == '/apps/dashboard':
        return dashboard.layout
    else:
        return home.layout


if __name__ == '__main__':
    app.run_server(debug=False)