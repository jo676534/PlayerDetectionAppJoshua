import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
import dash_table

from app import app

from api import api_game

df_game = api_game.get_unfinished_games()


# need to find a way to dynamically create this
dropdown = dbc.DropdownMenu(
    label="game_selection",
    children=[
        dbc.DropdownMenuItem("Game 0"),
        dbc.DropdownMenuItem("Game 1"),
        dbc.DropdownMenuItem("Game 2"),
    ],
)


game_table = dash_table.DataTable(
    id='datatable-paging',
    columns=[{"name": i, "id": i} for i in df_game.columns],
    page_current=0,
    page_size=len(df_game),
)


layout = html.Div([
    html.H1('Home Page Placeholder'),
    dbc.Container(
        [
            # dbc.Row([
            #     dbc.Input(id="game_input", placeholder="game id", type="integer", min=0, step=1, style={'width': '25%', 'display': 'inline-block', "margin-left": "0px", "margin-right": "15px",}),
            #     dbc.Button("Select Game", id='generate_link'),
            # ]),
            html.Div(id="link_location"),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(game_table, md=8),
                    dbc.Col([
                        dbc.Input(id="game_input", placeholder="game id", type="number", min=0, step=1, style={'width': '40%', 'display': 'inline-block', "margin-left": "0px", "margin-right": "15px",}),
                        dbc.Button("Select Game", id='generate_link'),
                    ])
                ],
            ),
        ],
        fluid=True,
    ), 
])


@app.callback(
    Output('datatable-paging', 'data'),
    [Input('datatable-paging', "page_current"),
     Input('datatable-paging', "page_size"),
     Input('datatable-paging', 'sort_by')])
def update_table(page_current,page_size,sort_by):
    return df_game.to_dict('records')



# @app.callback(
#     Output('disp_button', 'children'),
#     [Input('sbutton{}'.format(name1), 'n_clicks') for name1 in filelist['Key']]
# )
# def update(*button_clicks):
#     # here I'm assuming you just care which one was clicked most recently
#     # so use dash.callback_context.triggered and ignore the n_clicks values
#     return dash.callback_context.triggered[0]


# need to do the following:
    # have a choice between games
        # retrieve from the database
    # decide on a game
    # generate a button based on the game's state

# States:
# 0: PAGE - Initial Reveiew (Game freshly uploaded)
# 1: PROCESS - Converted to 15 fps
# 2: PAGE - Video Editor (Being edited)
# 3: PROCESS - Video being recompiled with removed frames (Then usually goes back to stage 2 unless no more editing needs to be done)
# 4: PROCESS - Detection algorithm being run
# 5: PAGE - Dashboard (Track matching + Manual annotation + Add track)
# 6: PROCESS - Homography being run
# 7: PAGE - Final review page
