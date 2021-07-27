# Imports
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
# from app import server

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
    color="#000e44",
    dark=True,
    id = "nav_bar",
    className= "nav_bar_style",
    brand_style={"margin-left": "-160px"},
)

info_storage = html.Div([
    dcc.Store(id="game_id", storage_type='session', data=0),
    dcc.Store(id="video_path", storage_type='session'),
    dcc.Store(id='start_frame_add', storage_type='session'),
    dcc.Store(id='final_frame_add', storage_type='session'),
    dcc.Store(id='player_id_add', storage_type='session'),
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', children=[]),
    info_storage,
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
        return home.layout




application = app.server 
if __name__ == '__main__':
    application.run(debug=True, port=8080)
