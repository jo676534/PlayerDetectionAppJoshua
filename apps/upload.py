from dash_bootstrap_components._components.Button import Button
import pandas as pd
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandasql as ps
import dash_table
import dash

from app import app

from api import api_team
from api import api_player

# Globals start here ========================

df_team = api_team.get_teams()
df_player = api_player.get_players()
df_player_a = None # dataframe for the players on team a
df_player_b = None # dataframe for the players on team b

t_name = None
t_id = None
p_name = None
p_id = None

# Dash components start here ================

main_upload_card = dbc.Card(
    id = 'main_upload_card',
    children=[
        dbc.CardHeader(
            [
                html.H2("Player Info Card"),
                html.Br(),
                html.Div("Player ID:", style={'display': 'inline-block'}),
                dbc.Input(id="player_id_input", placeholder="Player ID", type="number", min=0, step=1, style={'width': '15%', 'display': 'inline-block', "margin-left": "10px", "margin-right": "15px",}, className= 'add_track_input',),
                html.Div(id="player_name_output", style={'display': 'inline-block'}),
                html.Br(),
                dbc.Button("Find Player ID", id="player_open_modal", style={'display': 'inline-block'}),
                dbc.Button("Add to Team A", id="add_player_a", style={'display': 'inline-block', "margin-left": "20px"}),
                dbc.Button("Add to Team B", id="add_player_b", style={'display': 'inline-block', "margin-left": "20px"}),
                html.Br(),
                html.Div(id="add_player_output"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Player ID Search"),
                        dbc.ModalBody(
                            [
                                html.Div("Player Name:", style={'display': 'inline-block'}),
                                dbc.Input(id="player_name_input", placeholder="Player Name", style={'width': '30%', 'display': 'inline-block', "margin-left": "15px", "margin-right": "15px",}, className= 'add_track_input',),
                                dbc.Button("Search", id="player_search", style={'display': 'inline-block'}),
                                dbc.Button("Add New player", id="add_new_player", style={'display': 'inline-block', "margin-left": "15px"}),
                                html.Br(),
                                html.Div("Search Result:", style={'display': 'inline-block', 'margin-right': "10px"}),
                                html.Div(id="player_search_output", style={'display': 'inline-block'}),
                                html.Br(),
                                html.Div( # div for the add new player confirm/deny (not implemented yet)
                                    [
                                        dbc.Button("Confirm", id="confirm_player", style={'display': 'inline-block', "margin-right": "15px"}),
                                        dbc.Button("Deny", id="deny_player", style={'display': 'inline-block'}),
                                    ],
                                    id="player_button_div",
                                    style={'display': 'none'},
                                ),
                                html.Div(
                                    [
                                        dbc.Button("Set Player ID", id="set_player", style={'display': 'inline-block'}),
                                    ],
                                    id="player_add_div",
                                    style={'display': 'none'},
                                ),
                                # html.Div( # potential div for having the add to team buttons be within the modal
                                #     [
                                #         dbc.Button("Add to Team A", id="add_player_a_modal", style={'display': 'inline-block', "margin-right": "15px"}),
                                #         dbc.Button("Add to Team B", id="add_player_b_modal", style={'display': 'inline-block'}),
                                #     ],
                                #     id="player_add_div",
                                #     style={'display': 'none'},
                                # ),
                                html.Hr(),
                                html.H5("Player List"),
                                # dash_table.DataTable(
                                #     id='player_table',
                                #     columns=[
                                #         {'name': 'Team ID', 'id': 'team_id'}, 
                                #         {'name': 'Team Name', 'id': 'name'}, 
                                #     ],
                                #     page_current=0,
                                #     page_size=20,
                                #     style_as_list_view=True,
                                #     style_cell={'padding': '5px', 'font_family': 'Helvetica', 'textAlign': 'left'},
                                #     style_header={
                                #         'backgroundColor': '#000e44',
                                #         'fontWeight': 'bold',
                                #         'color': '#00c2cb',
                                #     }
                                # )
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button("Close Modal", id="player_close_modal", n_clicks=0)
                            ]
                        ),
                    ],
                    id="player_modal",
                    size="lg",
                    scrollable=True,
                    is_open=False,
                ),
            ]
        ),
        dbc.CardBody(
            [
                html.H4("Team A Table"),
                html.Br(),
                dash_table.DataTable(
                    id='player_table_a',
                    columns=[
                        {'name': 'Player ID', 'id': 'player_id'}, 
                        {'name': 'Player Name', 'id': 'name'}, # add more later
                        {'name': 'Initials', 'id':'initials'},
                        {'name': 'Jersey', 'id':'jersey'},
                    ],
                    page_current=0,
                    page_size=20,
                    style_as_list_view=True,
                    style_cell={'padding': '5px', 'font_family': 'Helvetica', 'textAlign': 'left'},
                    style_header={
                        'backgroundColor': '#000e44',
                        'fontWeight': 'bold',
                        'color': '#00c2cb',
                    }
                ),
                html.Br(),
                html.Div("Player ID to Remove from Team A:", style={'display': 'inline-block'}),
                dbc.Input(id="player_input_remove_a", placeholder="Player ID", type="number", min=0, step=1, style={'width': '15%', 'display': 'inline-block', "margin-left": "10px", "margin-right": "15px",}, className= 'add_track_input',),
                dbc.Button("Remove Player", id="player_button_remove_a", style={'display': 'inline-block'}),
                html.Hr(),
                html.H4("Team B Table"),
                html.Br(),
                dash_table.DataTable(
                    id='player_table_b',
                    columns=[
                        {'name': 'Player ID', 'id': 'player_id'}, 
                        {'name': 'Player Name', 'id': 'name'}, # add more later
                        {'name': 'Initials', 'id':'initials'},
                        {'name': 'Jersey', 'id':'jersey'},
                    ],
                    page_current=0,
                    page_size=20,
                    style_as_list_view=True,
                    style_cell={'padding': '5px', 'font_family': 'Helvetica', 'textAlign': 'left'},
                    style_header={
                        'backgroundColor': '#000e44',
                        'fontWeight': 'bold',
                        'color': '#00c2cb',
                    }
                ),
                html.Br(),
                html.Div("Player ID to Remove from Team B:", style={'display': 'inline-block'}),
                dbc.Input(id="player_input_remove_b", placeholder="Player ID", type="number", min=0, step=1, style={'width': '15%', 'display': 'inline-block', "margin-left": "10px", "margin-right": "15px",}, className= 'add_track_input',),
                dbc.Button("Remove Player", id="player_button_remove_b", style={'display': 'inline-block'}),
            ]
        ),
        dbc.CardFooter(
            [
                html.H2("Submit zone"),
                html.Div("Take the date of the game"),
                html.Div("Have a place to upload the actual video file"),
                html.Div("Submit Button when finished. Needs to check for at least 11 players on both teams, Team ids filled out, date filled out, anything else?"),
                html.Div(id="hidden_div_set_player"), # used to update other parts like: 1. close the modal, 2. clear the modal player name input
                html.Div(id="hidden_div_add_player"), # used to update other parts like: 1. clear the player id input
                html.Div(id="hidden_div_remove_player"), # used to update other parts like: 1. regen the table with the removed player
            ]
        ),
    ]
)


team_upload_card = dbc.Card(
    id = 'main_upload_card',
    children=[
        dbc.CardHeader(
            [
                html.H2("Team Info Card")
            ]
        ),
        dbc.CardBody(
            [
                html.Div("Team A ID:", style={'display': 'inline-block'}),
                dbc.Input(id="team_a_id", placeholder="Team A ID", type="number", min=0, step=1, style={'width': '30%', 'display': 'inline-block', "margin-left": "10px", "margin-right": "15px",}, className= 'add_track_input',),
                html.Div(id="team_a_name", style={'display': 'inline-block'}),
                html.Br(),
                html.Div("Team B ID:", style={'display': 'inline-block'}),
                dbc.Input(id="team_b_id", placeholder="Team B ID", type="number", min=0, step=1, style={'width': '30%', 'display': 'inline-block', "margin-left": "10px", "margin-right": "15px",}, className= 'add_track_input',),
                html.Div(id="team_b_name", style={'display': 'inline-block'}),
                html.Br(),

                dbc.Button("Find Team ID", id="team_open_modal", n_clicks=0),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Team ID Search"),
                        dbc.ModalBody(
                            [
                                html.Div("Team Name:", style={'display': 'inline-block'}),
                                dbc.Input(id="team_name", placeholder="Team Name", style={'width': '30%', 'display': 'inline-block', "margin-left": "15px", "margin-right": "15px",}, className= 'add_track_input',),
                                dbc.Button("Search", id="team_search", style={'display': 'inline-block'}),
                                dbc.Button("Add New Team", id="add_team", style={'display': 'inline-block', "margin-left": "15px"}),
                                html.Br(),
                                html.Div("Search Result:", style={'display': 'inline-block', 'margin-right': "10px"}),
                                html.Div(id="team_id_output", style={'display': 'inline-block'}),
                                html.Br(),
                                html.Div(
                                    [
                                        dbc.Button("Confirm", id="confirm_team", style={'display': 'inline-block', "margin-right": "15px"}),
                                        dbc.Button("Deny", id="deny_team", style={'display': 'inline-block'}),
                                    ],
                                    id="button_div",
                                    style={'display': 'none'},
                                ),
                                html.Div(
                                    [
                                        dbc.Button("Set Team A", id="set_a", style={'display': 'inline-block', "margin-right": "15px"}),
                                        dbc.Button("Set Team B", id="set_b", style={'display': 'inline-block'}),
                                    ],
                                    id="set_div",
                                    style={'display': 'none'},
                                ),
                                html.Hr(),
                                html.H5("Team List"),
                                dash_table.DataTable(
                                    id='team_table',
                                    columns=[
                                        {'name': 'Team ID', 'id': 'team_id'}, 
                                        {'name': 'Team Name', 'id': 'name'}, 
                                    ],
                                    page_current=0,
                                    page_size=20,
                                    style_as_list_view=True,
                                    style_cell={'padding': '5px', 'font_family': 'Helvetica', 'textAlign': 'left'},
                                    style_header={
                                        'backgroundColor': '#000e44',
                                        'fontWeight': 'bold',
                                        'color': '#00c2cb',
                                    }
                                )
                            ]
                        ),
                        dbc.ModalFooter(
                            [
                                dbc.Button("Close Modal", id="team_close_modal", n_clicks=0)
                            ]
                        ),
                    ],
                    id="team_modal",
                    size="lg",
                    scrollable=True,
                    is_open=False,
                ),
            ]
        ),
        dbc.CardFooter(
            [
                html.Div(id="hidden_div_team"),
            ]
        ),
    ]
)


layout = html.Div([
    html.Br(),
    html.H1('Upload Page', style={'textAlign': 'center'}),
    html.Br(),
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(team_upload_card, xs=4, sm=4, md=4, lg=4, xl=4),
                    dbc.Col(main_upload_card, xs=8, sm=8, md=8, lg=8, xl=8),
                ],
                justify="center",
            )
        ],
        fluid=True,
    ), 
])


# team callbacks =======================================================================================

# team modal toggle callback
@app.callback(
    Output("team_modal", "is_open"),
    Input("team_open_modal", "n_clicks"), 
    Input("team_close_modal", "n_clicks"),
    State("team_modal", "is_open"),
    prevent_initial_call=True)
def toggle_team_modal(open, close, is_open):
    if open or close:
        return not is_open
    return is_open


# table creation callback
@app.callback(
    Output('team_table', 'data'),
    Input('team_table', "page_current"),
    Input('team_table', "page_size"),
    Input('team_table', 'sort_by'))
def update_table(page_current, page_size, sort_by):
    global df_team
    return df_team.to_dict('records')


# team search modal callback
@app.callback(
    Output("team_id_output", "children"),
    Output("button_div", "style"),
    Output("set_div", "style"),
    Input("team_search", "n_clicks"),
    Input("add_team", "n_clicks"),
    Input("confirm_team", "n_clicks"),
    Input("deny_team", "n_clicks"),
    State("team_name", "value"),
    prevent_inital_callback=True)
def search_team(search_clicks, add_clicks, confirm, deny, team_name):
    global t_name
    global t_id
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]

    if(cbcontext == "team_search.n_clicks" and search_clicks):
        sql = f'''SELECT * FROM df_team WHERE name like '%{team_name}%' '''
        df_out = ps.sqldf(sql)
        if(len(df_out) > 1):
            return f"This query returned {len(df_out)} teams. Please be more specific.", {'display': 'none'}, {'display': 'none'}
        elif(len(df_out) == 0):
            return "No teams were found with that name.", {'display': 'none'}, {'display': 'none'}
        else:
            for index, df in df_out.iterrows():
                t_name = df['name']
                id = df['team_id']
                t_id = int(id)
                return(f"Team ID: {id} // Team Name: {t_name}", {'display': 'none'}, {'display': 'block'}) # displays the add to team a or team b buttons

    elif(cbcontext == "add_team.n_clicks" and add_clicks):
        t_name = team_name
        if(team_name is None): return("Please enter a team name first.", {'display': 'none'}, {'display': 'none'})
        return(f"This will create a new team named \"{t_name}\". Are you sure?", {'display': 'block'}, {'display': 'none'}) # displays the confirm/deny buttons used in the next part of the callback

    elif(cbcontext == "confirm_team.n_clicks" and confirm):
        # here need to commit the team to the database
        # get max team id + 1
        # sql = f'''SELECT MAX(team_id) FROM df_team'''
        # new_team_id = ps.sqldf(sql)
        # print("\n")
        # print(new_team_id.loc[0])
        
        # do the api query for max team id
        # add one
        # commit team to the database
        # query back the new team table

        return("Team successfully added", {'display': 'none'}, {'display': 'none'})

    elif(cbcontext == "deny_team.n_clicks" and deny):
        return("Team not added.", {'display': 'none'}, {'display': 'none'})

    else:
        return(None, {'display': 'none'}, {'display': 'none'})


# set team a
@app.callback(
    Output("team_a_id", "value"),
    Input("set_a", "n_clicks"),
    prevent_initial_callback=True)
def set_team_a(n_clicks):
    global t_id
    if n_clicks is not None:
        return t_id
    else:
        return None


# set team b
@app.callback(
    Output("team_b_id", "value"),
    Input("set_b", "n_clicks"),
    prevent_initial_callback=True)
def set_team_b(n_clicks):
    global t_id
    if n_clicks is not None:
        return t_id


# get a name
@app.callback(
    Output("team_a_name", "children"),
    Input("team_a_id", "value"),
    prevent_initial_callback=True)
def get_a_name(team_id):
    if(team_id is None): return None
    sql = f'''SELECT * FROM df_team WHERE team_id={team_id}'''
    df_out = ps.sqldf(sql)
    if(len(df_out) == 0):
        return "Invalid Team ID"
    else:
        for index, df in df_out.iterrows():
            return df['name']


# get b name
@app.callback(
    Output("team_b_name", "children"),
    Input("team_b_id", "value"),
    prevent_initial_callback=True)
def get_b_name(team_id):
    if(team_id is None): return None
    sql = f'''SELECT * FROM df_team WHERE team_id={team_id}'''
    df_out = ps.sqldf(sql)
    if(len(df_out) == 0):
        return "Invalid Team ID"
    else:
        for index, df in df_out.iterrows():
            return df['name']


# player callbacks =======================================================================================

# player modal toggle callback
@app.callback(
    Output("player_modal", "is_open"),
    Input("player_open_modal", "n_clicks"), 
    Input("player_close_modal", "n_clicks"),
    Input("hidden_div_set_player", "children"),
    State("player_modal", "is_open"),
    prevent_initial_call=True)
def toggle_player_modal(open, close, hidden_div, is_open):
    if open or close or hidden_div:
        return not is_open
    return is_open


# player search modal callback
@app.callback(
    Output("player_search_output", "children"),
    Output("player_button_div", "style"),
    Output("player_add_div", "style"),
    Output("player_name_input", "value"),
    Input("player_search", "n_clicks"),
    Input("hidden_div_set_player", "children"),
    State("player_name_input", "value"),
    prevent_inital_callback=True)
def search_player(search_clicks, hidden_div, player_name):
    global p_id
    global p_name

    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if(cbcontext == "player_search.n_clicks" and search_clicks):
        sql = f'''SELECT * FROM df_player WHERE name like '%{player_name}%' '''
        df_out = ps.sqldf(sql)
        if(len(df_out) > 1):
            return f"This query returned {len(df_out)} players. Please be more specific.", {'display': 'none'}, {'display': 'none'}, player_name
        elif(len(df_out) == 0):
            return "No players were found with that name.", {'display': 'none'}, {'display': 'none'}, player_name
        else:
            for index, df in df_out.iterrows():
                p_name = df['name']
                id = df['player_id']
                p_id = int(id)
                return f"Player ID: {id} // Player Name: {p_name}", {'display': 'none'}, {'display': 'block'}, player_name
    
    elif(cbcontext == "hidden_div_set_player.children"):
        return None, {'display': 'none'}, {'display': 'none'}, None

    else:
        return None, {'display': 'none'}, {'display': 'none'}, player_name


# set player
@app.callback(
    Output("player_id_input", "value"),
    Output("hidden_div_set_player", "children"), # used to update other parts like: 1. close the modal, 2. clear the input
    Input("set_player", "n_clicks"),
    Input("hidden_div_add_player", "children"),
    prevent_initial_callback=True)
def set_player(n_clicks, hidden_div):
    global p_id
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]

    if n_clicks is not None and cbcontext == "set_player.n_clicks":
        return p_id, None
    else:
        return None, None


# display player name
@app.callback(
    Output("player_name_output", "children"),
    Input("player_id_input", "value"),
    prevent_initial_callback=True)
def get_a_name(player_id):
    if(player_id is None): return None
    sql = f'''SELECT * FROM df_player WHERE player_id={player_id}'''
    df_out = ps.sqldf(sql)
    if(len(df_out) == 0):
        return "Invalid Player ID"
    else:
        for index, df in df_out.iterrows():
            return df['name']


# add player to team (also updates the output tables)
@app.callback(
    Output('player_table_a', 'data'), # table a
    Output('player_table_b', 'data'), # table b
    Output('add_player_output', "children"), # text output
    Output("hidden_div_add_player", "children"), # hidden div
    Input("add_player_a", "n_clicks"), # add to team a
    Input("add_player_b", "n_clicks"), # add to team b
    Input("hidden_div_remove_player", "children"),
    State("player_id_input", "value"), # player id input
    prevent_initial_callback=True)
def add_player_to_team(add_a, add_b, hidden_div, player_id):
    global df_player_a
    global df_player_b
    output_a = None
    output_b = None
    output_text = None

    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    # add player to team
    if cbcontext == "add_player_a.n_clicks" and add_a is not None and player_id is not None:
        # get df with the player's info
        sql = f'''SELECT * FROM df_player WHERE player_id={player_id}'''
        df_out = ps.sqldf(sql)
        
        # check if this if the first player or not
        if df_player_a is None: # if so we create the df with their info
            for index, df in df_out.iterrows():
                data = [[df['player_id'], df['name'], df['initials'], df['team_id'], df['jersey']]]
                df_player_a = pd.DataFrame(data, columns=["player_id", "name", "initials", "team_id", "jersey"])
        else: # otherwise we just append the dataframe with their info
            for index, df in df_out.iterrows():
                data = [[df['player_id'], df['name'], df['initials'], df['team_id'], df['jersey']]]
                temp_df = pd.DataFrame(data, columns=["player_id", "name", "initials", "team_id", "jersey"])
                df_player_a = df_player_a.append(temp_df)

        # readies outputs (if None we have to use None since None has no .to_dict operation)
        if df_player_a is None: output_a = None
        else: output_a = df_player_a.to_dict('records')

        if df_player_b is None: output_b = None
        else: output_b = df_player_b.to_dict('records')

        return output_a, output_b, output_text, None

    elif cbcontext == "add_player_b.n_clicks" and add_b is not None and player_id is not None:
        # get df with the player's info
        sql = f'''SELECT * FROM df_player WHERE player_id={player_id}'''
        df_out = ps.sqldf(sql)
        
        # check if this if the first player or not
        if df_player_b is None: # if so we create the df with their info
            for index, df in df_out.iterrows():
                data = [[df['player_id'], df['name'], df['initials'], df['team_id'], df['jersey']]]
                df_player_b = pd.DataFrame(data, columns=["player_id", "name", "initials", "team_id", "jersey"])
        else: # otherwise we just append the dataframe with their info
            for index, df in df_out.iterrows():
                data = [[df['player_id'], df['name'], df['initials'], df['team_id'], df['jersey']]]
                temp_df = pd.DataFrame(data, columns=["player_id", "name", "initials", "team_id", "jersey"])
                df_player_b = df_player_b.append(temp_df)

        
        # readies outputs (if None we have to use None since None has no .to_dict operation)
        if df_player_a is None: output_a = None
        else: output_a = df_player_a.to_dict('records')

        if df_player_b is None: output_b = None
        else: output_b = df_player_b.to_dict('records')

        return output_a, output_b, output_text, None

    else:
        # readies outputs (if None we have to use None since None has no .to_dict operation)
        if df_player_a is None: output_a = None
        else: output_a = df_player_a.to_dict('records')

        if df_player_b is None: output_b = None
        else: output_b = df_player_b.to_dict('records')

        if player_id is None and (add_a or add_b): output_text = "Need to input a Player ID first."
        else: output_text = None

        return output_a, output_b, output_text, None


# remove player from table
@app.callback(
    Output("hidden_div_remove_player", "children"),
    Output("player_input_remove_a", "value"), # used to refresh the inputs
    Output("player_input_remove_b", "value"), # used to refresh the inputs
    Input("player_button_remove_a", "n_clicks"),
    Input("player_button_remove_b", "n_clicks"),
    State("player_input_remove_a", "value"),
    State("player_input_remove_b", "value"),
    prevent_initial_callback=True)
def remove_player(a_click, b_click, a_id, b_id):
    global df_player_a
    global df_player_b
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]

    if cbcontext == "player_button_remove_a.n_clicks":
        df_player_a = df_player_a[df_player_a.player_id != a_id]
        return None, None, b_id
    elif cbcontext == "player_button_remove_b.n_clicks":
        df_player_b = df_player_b[df_player_b.player_id != b_id]
        return None, a_id, None
    else:
        return None, a_id, b_id



