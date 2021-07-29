
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
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


game_card = dbc.Card(
    [
        dbc.CardBody(
            [
                dash_table.DataTable(
                    id='game_table', 
                    columns= [{'name': 'Game ID', 'id': 'game_id'}, {'name': 'Team 1 Name', 'id': 'team1_name'}, {'name': 'Team 2 Name', 'id': 'team2_name'}, {'name': 'Date Played', 'id': 'day_played'}, {'name': 'Process State', 'id': 'process_state'}], # [{"name": i, "id": i} for i in df_game.columns], #['Game ID', 'Team 1 Name', 'Team 2 Name', 'Day Played', 'Process State'],# 
                    page_current=0,
                    page_size=5,
                ),
            ]
        )
    ]
)


main_card = dbc.Card(
    [
        dbc.CardHeader(
            
        ),
        dbc.CardBody(
            [
                dbc.Button(
                    "Game Collapse",
                    id="collapse_button",
                    n_clicks=0,
                ),
                html.Br(),
                html.Br(),
                dbc.Collapse(
                    game_card,
                    id="game_collapse",
                    is_open=False,
                )
            ]
        )
    ]
)


entry_card = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Input(id="game_input", placeholder="Game ID", type="number", min=0, step=1, style={'width': '40%', 'display': 'inline-block', "margin-left": "0px", "margin-right": "15px",}),
                dbc.Button("Select Game", id='select_game'),
                html.Div(id="link_output"),
            ]
        )
    ]
)


layout = html.Div([
    html.Br(),
    html.H1('Sports Science AI Home Page', style={'textAlign': 'center'}),
    dbc.Container(
        [
            html.Div(id="link_location"),
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(main_card, md=8),
                    dbc.Col(entry_card),
                ],
            ),
        ],
        fluid=True,
    ), 
])

# callback to create the table
@app.callback(
    Output('game_table', 'data'),
    Input('game_table', "page_current"),
    Input('game_table', "page_size"),
    Input('game_table', 'sort_by')
    )
def update_table(page_current,page_size,sort_by): # 'Game ID', 'Team 1 Name', 'Team 2 Name', 'Day Played', 'Process State'
    global df_game
    if 'user_id' in df_game:
        df_game = df_game.drop(['user_id', 'team1_id', 'team2_id', 'day_uploaded', 'video_original', 'video_modified'], axis=1)
    #print([{"name": i, "id": i} for i in df_game.columns])
    return df_game.to_dict('records')

# Collapse callback
@app.callback(
    Output("game_collapse", "is_open"),
    Input("collapse_button", "n_clicks"),
    State("game_collapse", "is_open"),
    )
def game_collapse(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

# callback for the select game button
@app.callback(
    Output("link_output", "children"),
    Output("game_id", "data"), # outputs to the game_id dcc.store on index page
    Output("video_path", "data"), # outputs to the video link dcc.store on index
    Input("select_game", "n_clicks"),
    State("game_input", "value"),
    State("game_id", "data"),
    prevent_initial_call=True)
def select_game(n_clicks, game_id, game_id_storage):
    # use the game_id to grab the link to the video + process_state
    # then use the process state to determine which link to generate
    if n_clicks:
        process_state = 0
        output = None
        error = 0

        if process_state == 0: # 0: PAGE - Initial Reveiew (Game freshly uploaded)
            output = dbc.Button("Initial Review Link", id="link", href='/apps/initial_review')
        elif process_state == 1: # 1: PROCESS - Converted to 15 fps
            output = "Video currently being converted to 15fps."
        elif process_state == 2: # 2: PAGE - Video Editor (Being edited)
            output = dbc.Button("Video Editor Link", id="link", href='/apps/video_edit')
        elif process_state == 3: # 3: PROCESS - Video being recompiled with removed frames (Then usually goes back to stage 2 unless no more editing needs to be done)
            output = "Video still being recompiled."
        elif process_state == 4: # 4: PROCESS - Detection algorithm being run
            output = "Detection algorithm being run."
        elif process_state == 5: # 5: PAGE - Dashboard (Track matching + Manual annotation + Add track)
            output = dbc.Button("Dashboard Link", id="link", href='/apps/dashboard')
        elif process_state == 6: # 6: PROCESS - Homography being run
            output = "Homography being run"
        elif process_state == 7: # 7: PAGE - Final review page
            output = "Video processing completed."
        else:
            error = 1
        
        return output, game_id, "Path"
    else:
        return None, game_id_storage, None


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
