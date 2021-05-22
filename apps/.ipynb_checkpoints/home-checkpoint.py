import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
from app import app


layout = html.Div([
    "Hello World"
])

# layout = html.Div([
#     dcc.Location(id='url', refresh=False),
#     html.Div([
#         html.H1('Welcome Home'),
#         dcc.Link('Test', href='/apps/test'),
#         html.H1('Goodbye Home')
#     ], className="row"),
#     html.Div(id='page-content', children=[])
# ])


# @app.callback(Output('page-content', 'children'),
#               [Input('url', 'pathname')])
# def display_page(pathname):
#     if pathname == '/apps/home':
#         return home.layout
#     if pathname == '/apps/test':
#         return test.layout
#     else:
#         return "404 Page Error! Please choose a link"