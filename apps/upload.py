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

# Globals start here ========================

df_team = api_team.get_teams()
name = None
t_id = None

# Dash components start here ================

main_upload_card = dbc.Card(
    id = 'main_upload_card',
    children=[
        dbc.CardHeader(
            [
                html.H2("Player Info Card"),
            ]
        ),
        dbc.CardBody(
            "Player data input table"
        ),
        dbc.CardFooter(
            "Submit zone"
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


# modal toggle callback
@app.callback(
    Output("team_modal", "is_open"),
    Input("team_open_modal", "n_clicks"), 
    Input("team_close_modal", "n_clicks"),
    State("team_modal", "is_open"),
    prevent_initial_call=True)
def toggle_modal(open, close, is_open):
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
    global name
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
                name = df['name']
                id = df['team_id']
                t_id = int(id)
                return(f"Team ID: {id}, Team Name: {name}", {'display': 'none'}, {'display': 'block'})

    elif(cbcontext == "add_team.n_clicks" and add_clicks):
        name = team_name
        if(team_name is None): return("Please enter a team name first.", {'display': 'none'}, {'display': 'none'})
        return(f"This will create a new team named \"{name}\". Are you sure?", {'display': 'block'}, {'display': 'none'})

    elif(cbcontext == "confirm_team.n_clicks" and confirm):
        # here need to commit the team to the database
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

# set team b
@app.callback(
    Output("team_b_id", "value"),
    Input("set_b", "n_clicks"),
    prevent_initial_callback=True)
def set_team_b(n_clicks):
    global t_id
    if n_clicks is not None:
        return t_id

