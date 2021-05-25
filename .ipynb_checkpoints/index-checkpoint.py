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
from apps import initial_review
from apps import video_edit
from apps import dashboard
from apps import add_track
from apps import final_review


navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(dcc.Link('Home', href='/apps/home')),
                dbc.DropdownMenuItem(dcc.Link('Initial Review', href='/apps/initial_review')),
                dbc.DropdownMenuItem(dcc.Link('Video Editor', href='/apps/video_edit')),
                dbc.DropdownMenuItem(dcc.Link('Dashboard', href='/apps/dashboard')),
                dbc.DropdownMenuItem(dcc.Link('Add Track', href='/apps/add_track')),
                dbc.DropdownMenuItem(dcc.Link('Final Review', href='/apps/final_review')),
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
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/home':
        return home.layout
    if pathname == '/apps/initial_review':
        return initial_review.layout
    if pathname == '/apps/video_edit':
        return video_edit.layout
    if pathname == '/apps/dashboard':
        return dashboard.layout
    if pathname == '/apps/add_track':
        return add_track.layout
    if pathname == '/apps/final_review':
        return final_review.layout
    else:
        return dashboard.layout


if __name__ == '__main__':
    app.run_server(debug=False)