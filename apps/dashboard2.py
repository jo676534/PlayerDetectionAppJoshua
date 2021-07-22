# INSTALL LIBRARIES ---------------------------------------------------------------------------------------------------------------------------
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
# import dash_player
from dash.dependencies import Input, Output, State
import os
from os.path import isfile, join
from skimage import io
import numpy as np
import psycopg2 as pg2
import pandas as pd
from dash.exceptions import PreventUpdate
import cv2  # from vid2frames
from app import app
import time
import math
import asyncio
# import boto3

from app import app
from apps import add_track
from api import api_detections
from api import api_team
from api import api_player
from api import api_game



filename = "./Videos/game_0.mp4"
vidcap = cv2.VideoCapture(filename)

# OpenCV2 version 2 used "CV_CAP_PROP_FPS"
fps = vidcap.get(cv2.CAP_PROP_FPS)
frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
vidcap.release() 

duration = frame_count/fps
resolution = (1280, 720)

framesPerSection = 5000
sections = math.ceil(frame_count / framesPerSection)
maxFrames = frame_count-1
player_tracks_counter = 0
all_tracks_counter = 0
viewable_tracks_counter = 0
track_state = 0
dic = None # api_detections.get_frame_detections(0)
dic_tracks, unique_tracks = None, None # api_detections.get_tracks(0)
# fetch the teams ------------------
df_teams = None # api_team.get_teams(0)
# fetch the players ----------------
df_players = None # api_player.get_players(0)


def add_editable_box(fig, track_id, player_id, initials, x0, y0, x1, y1, name=None, color=None, opacity=1, group=None, text=None):
    # could put code here to determine colors
    line_color = ""
    header = ""
    if player_id == -1:
        line_color = "#c90000" # red (not assigned)
        header = str(track_id)
    else: 
        line_color = "#0600b3" # blue (is assigned)
        header = initials


    fig.add_shape(
        editable=True,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        line_color=line_color,
        opacity=opacity,
        line_width=2,
        name=name,
    )
    fig.add_annotation( # ((x0+x1)/2)
        x=((x0+x1)/2),
        y=y0-30,
        text="{0}".format(header),
        showarrow=False, # True
        font=dict(
            family="Roboto",  # "Courier New, monospace",
            size=13,
            color="#ffffff"
        ),
        align="center",
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#636363",
        ax=0,  # 20
        ay=0,  # -30
        bordercolor="#c7c7c7",
        borderwidth=1,  # 2
        borderpad=2,  # 4
        bgcolor="#000000", # "#ff7f0e"
        opacity=0.8
    )

def getSections(sections):
    sectionOptions = [
        {'label': 'Section {}'.format(i+1), 'value': i}
        for i in range(sections)
    ]
    return sectionOptions

info_storage_DB = html.Div([
    dcc.Store(id='section_DB', storage_type='local', data=0),
    dcc.Store(id='frame_DB', storage_type='local', data=1), 
    dcc.Store(id='video_state_DB', storage_type='session', data=False),
])

video_card_DB = dbc.Card(
    id="imagebox",
    children=[
        dbc.CardHeader(
            html.Div(
            [   dbc.Row( 
                   children = [ 
                       dbc.FormGroup(
                                dbc.Checklist(
                                    options=[
                                        {"label": "Assigned Track Boxes", "value": 1}, #1 is assigned
                                        {"label": "Unassigned Track Boxes", "value": 2}, #2 is unassigned
                                    ],
                                    value=[1, 2],
                                    id="switches-input",
                                    style ={'margin-left':'20px'},
                                    switch=True,
                                    inline=True,
                                ),              
                    ),
                        html.Div(
                        [
                            dcc.Dropdown(
                                id = 'dropdown_DB',
                                options=getSections(sections),
                                searchable=False,
                                clearable=False,
                            ),
                            html.Div(id="dd-output-container"),
                        ],
                        style={"width": "20%", 'margin-left':'200px', 'font-size': '14px'},  
                )])    
            ],style = {"margin-bottom":"-15px"}
        ),
        className= "player_card_header",
        ),
        html.Div(id='hidden_div_j0', style= {'display':'none'},),
        html.Div(id='hidden_div_j1', style= {'display':'none'}),
        html.Div(id='hidden_div_j2', style= {'display':'none'}),
        html.Div(id='hidden_div_j3', style= {'display':'none'}),
        dbc.CardBody(
            [
                html.Div(id="manual_annotation_output"),
                html.Div(children=[ # needs to be properly initialized //////////////////////////////////////////////////////////////////////
                    dcc.Interval(
                        id='interval_DB',
                        disabled=False,
                        n_intervals=0,      # number of times the interval has passed
                        max_intervals=maxFrames # alternative way to do this = properly output the maxFrames to
                    ),
                ]),
                dcc.Graph( # WILL HAVE TO INITIALIZE THIS AS WELL //////////////////////////////////////////////////////////////////////////////////////////
                    id="canvas_DB",
                    style={'width': '1000px', 'height': '600px'},
                    config={"modeBarButtonsToAdd": ["drawrect", "eraseshape"]},
                )
            ]
        ),
        dbc.CardFooter(
            [
                # Slider Component
                dcc.Slider( # need to have a default slider w/pointless values and then have it replaced later during initialization ///////////////////////
                    id='slider_DB',
                    step=1,

                ),
                html.Div(id='frame_display_DB', className='current_frame'),
                # Pause/Player Buttons
                dbc.ButtonGroup(
                    [
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/PreviousSection.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="previousSec", outline=True, style={
                                   "margin-left": "50px", "margin-right": "15px", "margin-bottom": "15px"},color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/rw50.png?raw=true',
                                                 style={'height':'30px'})],  
                                    id="rewind-50_DB", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/rw10.png?raw=true',
                                                 style={'height':'30px'})],  
                                    id="rewind-10_DB", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/Prev.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="previous_DB", outline=True, style={
                                    "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/Play.png?raw=true',
                                                 style={'height':'30px'})],
                                   id="playpause_DB", outline=True,
                                   style={"margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/Next.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="next_DB", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/ff10.png?raw=true',
                                                 style={'height':'30px'})], 
                                    id="fastforward-10_DB", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/ff50.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="fastforward-50_DB", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/NextSection.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="nextSec", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                    ],
                    style={"width": "100%", 'margin-left':'-10px'}
                ),
            ]
        ),
    ],
    style={"margin-left": "5px","margin-top": "20px", "margin-bottom": "20px", "margin-right": "10px"}
)


track_card = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Col(
            html.Div(
            [
                dbc.Button("All Tracks", id="all_tracks_bt", outline=True, style={
                       "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("Viewable Tracks", id="viewable_tracks_bt", outline=True, style={
                    "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("Player Tracks", id="player_tracks_bt",
                           outline=True, style={"font-size": "12px"}),
            ]))),
        dbc.CardBody(
            [ 
                html.Div(id='hidden-div', style= {'display':'none'}),
                html.Div(id='hidden-div2', style= {'display':'none'}),
                html.Div(id="hidden_div_init_input", style= {'display':'none'}),
                html.Div(id='track_container', children=[html.Div([
                    html.Div(children=
                        [
                            dbc.Col(
                                [
                                    dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"}, disabled=True),
                                    dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"}, disabled=True),
                                    dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}, disabled=True),
                                ],
                                align = 'center',
                            ),        
                            dbc.Col(
                                [
                                    dbc.RadioItems(
                                        options=[
                                            {'label': "Select a Track View", 
                                            'value': str(1)}
                                        ],
                                        id = "radio_all_tracks",
                                        className= "radio_items",
                                    )
                                ],
                                align = 'center',
                                style={'width': '100%', 
                                            'height': '437px', 
                                            'overflow': 'scroll', 
                                            'padding': '10px 10px 10px 20px'
                                }), 
                        ],
                    )
                ])])
            ]
        ),
        dbc.CardFooter(
            [
                html.H6("Add Track Section", className = "add_track_section_header"),
                html.Div(
                    [
                        dbc.Input(id="dashboard_input_start", placeholder="Start", type="number", min=0, step=1, className= "dashboard_input"), # value
                        dbc.Input(id="dashboard_input_final", placeholder="Final", type="number", min=0, step=1, className= "dashboard_input"), 
                    ]
                ),
                html.Div(
                    [
                        dbc.ButtonGroup(
                            [
                                dbc.Button("Set Start", id="set_start", style = {'font-size': '12px'}),
                                dbc.Button("Set Final", id="set_final", style = {'font-size': '12px'}),
                                dbc.Button("Add Track", id="add_track", style = {'font-size': '12px'}),
                                dbc.Button("Delete Section", id="delete_section", style = {'font-size': '12px'})
                            ]
                        )
                    ]
                ),
                dbc.Spinner(html.Div(id="add_track_output"))
            ]
        ),
    ],
    style={"margin-top": "20px", "margin-bottom": "20px", "margin-right": "10px"}
)


team_card = dbc.Card(
    [
        dbc.CardHeader(
            html.Div( 
                id = "team_buttons",
                children = 
                    [
                        dbc.Button("Team A", id="but7", outline=True, style={
                            "margin-left": "45px", "font-size": "12px"}),
                        dbc.Button("Team B", id="but8", outline=True,
                                style={"margin-left": "15px","font-size": "12px"}),
                    ])),
        dbc.CardBody(
            [
                html.Div(id='container', children=
                    [
                        dbc.Col([dbc.Button("Assign Track", id = 'assign_track_bt',color="secondary",block = True, style={"font-size": "12px","margin-bottom":"10px"}, disabled=True),
                                dbc.Spinner(html.Div(id="assign_track_output")),],
                                align = 'center',),
                        dbc.Col([dbc.RadioItems(
                        options=
                            [
                                {'label': "Select a Team View", 
                                'value': str(1)}
                            ],
                        id = "radio_players_A",
                        className= "radio_items",
                    
                        )],
                        align = 'center',
                        style={'width': '250px', 
                            'height': '670px', 
                            'overflow': 'scroll', 
                            'padding': '10px 10px 10px 20px'
                            }), 
                    ]
                ),
            ]
        ),
        dbc.CardFooter(
            [

            ]
        ),
    ],
    
    style={"margin-top": "20px", "margin-bottom": "20px"}
)


layout = html.Div(  # was app.layout
    [
        # navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(video_card_DB, md=7.5),
                        dbc.Col(track_card, md=2.5),
                        dbc.Col(team_card, md=2.5),

                    ],
                ),
            ],
            fluid=True,
        ),
        info_storage_DB
    ],
)


# manual annotation callback
@app.callback(
    Output("manual_annotation_output", "children"),
    Output("hidden_div_j0", "children"),
    Input('canvas_DB', 'relayoutData'),
    State('slider_DB', 'value'),
    State("radio_players_A", 'value'),
    prevent_initial_call=True)
def manual_annotation(graph_relayout, frame, player_id):
    global dic
    global dic_tracks
    global unique_tracks

    if (not 'shapes' in graph_relayout):
        return "Please do not resize boxes, that is not supported", None
    
    old_num_boxes = len(dic[frame])
    new_num_boxes = len(graph_relayout['shapes'])

    track_id = 0

    # DELETE BOX ---------------------------------
    if (new_num_boxes < old_num_boxes): 
        df = dic[frame]

        i = 0
        skip = 0
        graph_len = len(graph_relayout['shapes'])
        
        # Iterate through the known values
        for index, temp_df in df.iterrows():
            x0_a = temp_df['x0']
            y0_a = temp_df['y0']
            x1_a = temp_df['x1']
            y1_a = temp_df['y1']
            
            if i != graph_len:
                x0_b = graph_relayout['shapes'][i]['x0']
                y0_b = graph_relayout['shapes'][i]['y0']
                x1_b = graph_relayout['shapes'][i]['x1']
                y1_b = graph_relayout['shapes'][i]['y1']
            else:
                skip = 1

            i += 1

            # Determine if this is the missing value
            if (x0_a != x0_b or y0_a != y0_b or x1_a != x1_b or y1_a != y1_b or skip == 1):
                track_id = temp_df['track_id']
                break
        
        # UPDATE LOCATION (Works) ///////////////////////////////////////////////////////////////////////////////////////////////////////////
        # we do this rather than making an api call because it will likely be faster and cost less
        df = df.reset_index() # needed because the add box indexing can overlap, causing multiple entries to be deleted
        df = df.drop('index', 1) # this creates a new index column with the old index values that we don't want so we discard it
        df = df.drop(df[df['track_id'] == int(track_id)].index) # then we search for indexes with the proper track_id and drop them
        dic[frame] = df # now we update the dictionary with the new, modified dataframe

        # works, just commented out for now
        api_detections.delete_detection(0, frame, track_id)

        dic_tracks, unique_tracks = api_detections.get_tracks(0)
        
        return "Detection box deleted from frame {} and track {}".format(frame, track_id), None

    # ADD BOX ------------------------------------
    elif (new_num_boxes > old_num_boxes): 
        print("ADD BOX CALLED")
        if (player_id is None):
            return "Need a player_id selected to add a box", None
        elif (old_num_boxes+1 == new_num_boxes): # good condition
            # Need to check here if there is already a track/detection with an assigned player_id in this frame
            err = False
            for index, detection in dic[frame].iterrows():
                if detection['player_id'] == int(player_id):
                    err = True
                    break
            if not err:
                bounding_box = graph_relayout['shapes'][old_num_boxes]

                x0 = bounding_box['x0']
                y0 = bounding_box['y0']
                x1 = bounding_box['x1']
                y1 = bounding_box['y1']

                if x0 > x1: x0, x1 = x1, x0
                if y0 > y1: y0, y1 = y1, y0

                track_id = -2 - int(player_id) # the smallest player_id is 0 and every player has a unique id, therefore manual track annotation ids can be consistently assigned through this simple formula

                # manual update of dic for efficiency
                initials = api_detections.get_player_initials(player_id)
                df_temp = pd.DataFrame([[0, frame, x0, y0, x1, y1, track_id, player_id, initials]], columns=['game_id', 'frame', 'x0', 'y0', 'x1', 'y1', 'track_id', 'player_id', 'initials'])
                dic[frame] = dic[frame].append(df_temp)

                # works, just commented out for now
                api_detections.add_detection(0, frame, x0, y0, x1, y1, -2, player_id)

                # UPDATE LOCATION (Works) ///////////////////////////////////////////////////////////////////////////////////////////////////////////
                dic_tracks, unique_tracks = api_detections.get_tracks(0)
                
                return "Box successfully added (not db linked) [norm]", None
            else:
                return "This player already has a detection assigned to them in this frame", None
        elif (old_num_boxes >= new_num_boxes):
            return "Bad Output: None drawn -or- Deleted and drawn", None
        elif (old_num_boxes+1 < new_num_boxes):
            return "Bad Output: Too many drawn", None
        else:
            return "Unknown ERROR 1", None

    # ERROR --------------------------------------
    else:
        return "Unknown ERROR 2", None


# set start frame
@app.callback(
    Output("dashboard_input_start", "value"),
    Input("set_start", "n_clicks"),
    State('slider_DB', 'value'))
def set_start_frame(n_clicks, frame):
    # probably want to include the values for the other side (and this goes for that side too) to ensure they don't pass each other in negative ways
    if n_clicks is not None:
        return frame


# set final frame
@app.callback(
    Output("dashboard_input_final", "value"),
    Input("set_final", "n_clicks"),
    State('slider_DB', 'value'))
def set_final_frame(n_clicks, frame):
    if n_clicks is not None:
        return frame


# callback for add track button
@app.callback(
    Output("add_track_output", "children"),
    Output("start_frame_add", "data"),
    Output("final_frame_add", "data"),
    Output('player_id_add', 'data'),
    Input("add_track", "n_clicks"),
    Input("delete_section", "n_clicks"),
    State("dashboard_input_start", "value"),
    State("dashboard_input_final", "value"),
    State("start_frame_add", "data"),
    State("final_frame_add", "data"),
    State("radio_players_A", 'value'),
    State('radio_all_tracks', 'value'),
    prevent_initial_call=True)
def add_track_function(add_clicks, delete_clicks, start_frame, final_frame, storage1, storage2, player_id, track_id):
    global dic
    global dic_tracks
    global unique_tracks

    # universal checks
    if add_clicks is None and delete_clicks is None: # if this callback was accidently called or initialized
        return None, start_frame, final_frame, player_id
    if ((start_frame is None) or (final_frame is None)):
        return ("Must have inputs for start and final frame.", start_frame, final_frame, player_id)
    elif start_frame >= final_frame:
        return ("Start frame must be less than final frame.", start_frame, final_frame, player_id)
    
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    # Delete Section
    if cbcontext == 'delete_section.n_clicks':
        if track_id is None:
            return ("Must have an intended track selected.", start_frame, final_frame, player_id)

        api_detections.delete_detection_section(0, start_frame, final_frame, track_id) # don't check and just purge the section even if there isn't anything there or only partially there within the single api call (simpler and doesn't matter much)
        
        # UPDATE LOCATION //////////////////////////////////////////////////////////////////////////////////////////////////
        dic = api_detections.get_frame_detections(0)
        dic_tracks, unique_tracks = api_detections.get_tracks(0)

        return ("Deleted selected dections from the track.", start_frame, final_frame, player_id)
    # Add Track
    elif cbcontext == 'add_track.n_clicks':
        if player_id is None:
            return ("Must have an intended player selected.", start_frame, final_frame, player_id)
        else:
            return (dbc.Button("Now Click Here", id="go_to_add_track", href='/apps/add_track'), start_frame, final_frame, player_id)
    else:
        return ("{}".format(storage1), start_frame, final_frame, player_id)


# simple callback that will only be called on page startup/refresh to create the necessary data structures
@app.callback(
    Output("hidden_div_init_input", "children"),
    Input("hidden_div_init_input", "children"),
    State("game_id", "data"))
def initializer(useless_input, game_id):
    global dic
    global dic_tracks
    global unique_tracks
    global df_teams
    global df_players

    if not game_id: 
        game_id = 0

    dic = api_detections.get_frame_detections(game_id)
    dic_tracks, unique_tracks = api_detections.get_tracks(game_id)

    df_teams = api_team.get_teams(game_id)
    df_players = api_player.get_players_roster(game_id)

    return None


# Call back that toggles between Team A and Team B
@app.callback(Output('container', 'children'),
              Input("but7", 'n_clicks'),
              Input("but8", 'n_clicks'),
              State("game_id", "data"))
def display(btn1, btn2, game_id):

    global df_players
    ctx = dash.callback_context

    if not game_id: 
        game_id = 0

    if not ctx.triggered:
        button_id = 'No clicks yet'
        df_players =  api_player.get_players_roster(game_id)

    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    global section
    if button_id == "but7":
        section = "A"
    if button_id == "but8":
        section = "B"

    # Players in team A
    a_row = df_players[df_players["team_id"] == 0]
    # Players in team B
    b_row = df_players[df_players["team_id"] == 1]
    

    # # Dash component for team A

    sectionA = html.Div([
        html.Div(children=[
        dbc.Col([dbc.Button("Assign Track", id = 'assign_track_bt',color="secondary",block = True, style={"font-size": "12px","margin-bottom":"10px"}),
                dbc.Spinner(html.Div(id="assign_track_output")),],
                align = 'center',),
        dbc.Col([dbc.RadioItems(
        options=[
            {'label': "("+ str(a_row.iloc[i]["jersey"]) + ") "+ str(a_row.iloc[i]["name"]), 'value': str(a_row.iloc[i]["player_id"])} for i in range(0, len(a_row))],
        #value=str(a_row.iloc[1]["player_id"]), 
        id = "radio_players_A",
        className= "radio_items",
    
        )],
        align = 'center',
        style={'width': '250px', 
            'height': '670px', 
            'overflow': 'scroll', 
            'padding': '10px 10px 10px 20px'
            }), 
        ],
        )
    ])

    # # Dash component for team B
    sectionB = html.Div([
        html.Div(children=[
        dbc.Col([dbc.Button("Assign Track", id = 'assign_track_bt',color="secondary",block = True, style={"font-size": "12px","margin-bottom":"10px"}),
                dbc.Spinner(html.Div(id="assign_track_output")),],
                align = 'center',),
        dbc.Col([dbc.RadioItems(
        options=[
            {'label': "("+ str(b_row.iloc[i]["jersey"]) + ") "+str(b_row.iloc[i]["name"]), 'value': str(b_row.iloc[i]["player_id"])} for i in range(0, len(b_row))],
        #value=str(b_row.iloc[1]["name"]),  
        id = "radio_players_A",
        className= "radio_items",
        )],
        align = 'center',
        style={'width': '250px', 
            'height': '670px', 
            'overflow': 'scroll', 
            'padding': '10px 10px 10px 20px'
            }), 
        ],
        )
    ])

    if button_id == "but7":
        return sectionA

    if button_id == "but8":
        return sectionB

    else:
        return sectionA


# Callback that toggles between track buttons:
# all tracks, viewable tracks, player tracks
@app.callback(Output('track_container', 'children'),
              Input("all_tracks_bt", 'n_clicks'),
              Input("viewable_tracks_bt", 'n_clicks'),
              Input("player_tracks_bt", 'n_clicks'),
              Input('hidden_div_j1', 'children'),
              Input("radio_players_A", 'value'),
              Input('hidden_div_j2', 'children'),
              State("frame_DB", 'data'),)
def display_2(btn1, btn2, btn3, hidden_div_j1, value, hidden_div_j2, frame):
    ctx = dash.callback_context
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    unassinged_is_checked = False
    assigned_is_checked = False
    global dic_tracks
    global unique_tracks
    global track_state # 0 is no state, 1 is all, 2 is view, 3 is player

    if not dic_tracks:
        dic_tracks, unique_tracks = api_detections.get_tracks(0)

    if not ctx.triggered:
        button_id = 'No clicks yet'
        return  html.Div([
                html.Div(children=[
                dbc.Col([
                        dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"},),
                        dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},),
                        dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}),
                        ],
                        align = 'center',),            
                dbc.Col([dbc.RadioItems(
                options=[
                    {'label': 'Track ID: ' + str(dic_tracks[i]['track_id'][0]), 'value': str(dic_tracks[i]['track_id'][0])} for i in range(0, unique_tracks)],
                #value=str(list(dic_tracks.keys())[1]), 
                id = "radio_all_tracks",
                className= "radio_items",
                )],
                align = 'center',
                style={'width': '100%', 
                            'height': '437px', 
                            'overflow': 'scroll', 
                            'padding': '10px 10px 10px 20px'
                    }), 
                ],
                )
            ])
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    #str(dic_tracks[i]['track_id'][0]

    # This first part uses the most recent track_state to determine which radio list should display when it needs to be refreshed
    # hidden_div_j1 == video display callback
    # radio_players_A == player buttons
    # hidden_div_j2 == delete button
    if cbcontext == 'hidden_div_j1.children' or cbcontext == 'radio_players_A.value' or cbcontext == 'hidden_div_j2.children':
        if (track_state == 0 or track_state == 1) and (cbcontext == 'hidden_div_j2.children'):
            button_id = "all_tracks_bt"
        elif (track_state == 2) and (cbcontext == 'hidden_div_j1.children' or cbcontext == 'hidden_div_j2.children'):
            button_id = "viewable_tracks_bt"
        elif (track_state == 3) and (cbcontext == 'radio_players_A.value' or cbcontext == 'hidden_div_j2.children'):
            button_id = "player_tracks_bt"
        else:
            raise PreventUpdate
    # Otherwise "normal" callbacks need to set the track_state value so it's remembered what was last clicked for when a refresh comes
    elif cbcontext == 'all_tracks_bt.n_clicks':
        track_state = 1
    elif cbcontext == 'viewable_tracks_bt.n_clicks':
        track_state = 2
    elif cbcontext == 'player_tracks_bt.n_clicks':
        track_state = 3

    # if cbcontext == 'switches_input.n_clicks':
    #     print("First if")
    #     if track_state == 2: 
    #         print("Second if")
    #         if (len(switches_value)==2):
    #             unassinged_is_checked = True
    #             assigned_is_checked = True

    #         if (len(switches_value)==1):
    #             if (switches_value[0]==1):
    #                 unassinged_is_checked = False
    #                 assigned_is_checked = True
    #             if (switches_value[0]==2):
    #                 unassinged_is_checked = True
    #                 assigned_is_checked = False 
            
    #         if (len(switches_value)==0):
    #             unassinged_is_checked = False
    #             assigned_is_checked = False

    #         button_id = "viewable_tracks_bt"

    if button_id == "all_tracks_bt":
        return  html.Div([
                html.Div(children=[
                dbc.Col([
                        dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"},),
                        dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},),
                        dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}),
                        ],
                        align = 'center',),            
                dbc.Col([dbc.RadioItems(
                options=[
                    {'label': 'Track ID: ' + str(dic_tracks[i]['track_id'][0]), 'value': str(dic_tracks[i]['track_id'][0])} for i in range(0, unique_tracks)],
                #value=str(list(dic_tracks.keys())[1]), 
                id = "radio_all_tracks",
                className= "radio_items",
                )],
                align = 'center',
                style={'width': '100%', 
                            'height': '437px', 
                            'overflow': 'scroll', 
                            'padding': '10px 10px 10px 20px'
                    }), 
                ],
                )
            ])

    if button_id == "viewable_tracks_bt":
        df_detections = api_detections.get_game_detections(0)
        viewable_row = df_detections[df_detections["frame"] == frame]
        viewable_row = viewable_row.sort_values(by=['track_id'])
        return html.Div([
                        html.Div(children=[
                           dbc.Col([
                        dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"},),
                        dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},),
                        dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}),
                        ],
                        align = 'center',), 
                            dbc.Col([dbc.RadioItems(
                                options=[
                                    {'label': 'Track ID: ' + str(viewable_row.iloc[i]['track_id']), 
                                    'value': str(viewable_row.iloc[i]['track_id'])} for i in range(0, len(viewable_row))],
                                # labelStyle = {'textAlign':'center'},
                                #value=str(viewable_row.iloc[frame]['track_id']), 
                                id = "radio_all_tracks",)],
                                className= "radio_items",
                            align = 'center',
                            style={'width': '100%', 
                                    'height': '437px', 
                                    'overflow': 'scroll', 
                                    'padding': '10px 10px 10px 20px'}), 
                        ],)
                ])

    if button_id == "player_tracks_bt":

        if value is None:
            return html.Div([
                         html.Div(children=[
                            dbc.Col([
                                dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"},disabled= True),
                                dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},disabled= True),
                                dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}, disabled= True),
                                ],
                                align = 'center',), 
                            dbc.Col([dbc.RadioItems(
                                options=[
                                {'label': "Select a Player", 
                                'value': str(dic_tracks[1]['track_id'][0])}],

                            id = "radio_all_tracks",)],
                            className= "radio_items",
                            align = 'center',
                            style={'width': '100%', 
                                    'height': '437px', 
                                    'overflow': 'scroll', 
                                    'padding': '10px 10px 10px 20px'}), 
                                ],)
                        ])
        
        else:
            trackList =[]
            conn = pg2.connect(database='soccer',
            user='postgres',
            host='localhost',  # localhost-------------------!
            password='root')
            cur = conn.cursor()
            cur.execute('''SELECT * FROM detections WHERE player_id = %s''' % value)
            data = cur.fetchall()
            
            cols = []
            for elt in cur.description:
                cols.append(elt[0])
            conn.commit()
            cur.close()
            conn.close()

            if len(data) < 1:

                return html.Div([
                         html.Div(children=[
                            dbc.Col([
                                dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"}, disabled= True),
                                dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},disabled= True),
                                dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}, disabled= True),
                                ],
                                align = 'center',), 
                            dbc.Col([dbc.RadioItems(
                                options=[
                                {'label': "No Assigned Tracks", 
                                'value': str(dic_tracks[1]['track_id'][0])}],

                            id = "radio_all_tracks",)],
                            className= "radio_items",
                            align = 'center',
                            style={'width': '100%', 
                                    'height': '437px', 
                                    'overflow': 'scroll', 
                                    'padding': '10px 10px 10px 20px'}), 
                                ],)
                        ])
            else:
                
                data1 = pd.DataFrame(data=data, columns=cols)
                unique_track_ids_temp = data1.iloc[1]['track_id']
                trackList.append(data1.iloc[1]['track_id'])
                for i in range(len(data1)):
                    if unique_track_ids_temp != data1.iloc[i]['track_id']:
                        unique_track_ids_temp = data1.iloc[i]['track_id']
                        trackList.append(unique_track_ids_temp)    

                trackList = sorted(set(trackList))
                return html.Div([
                                html.Div(children=[
                                    dbc.Col([
                                        dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"},),
                                        dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},),
                                        dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}),
                                        ],
                                        align = 'center',), 
                                    dbc.Col([dbc.RadioItems(
                                        options=[
                                            {'label': 'Track ID: ' + str(trackList[i]), 
                                            'value': str(trackList[i])} for i in range( len(trackList))],
                                        # labelStyle = {'textAlign':'center'},
                                        #value=str(viewable_row.iloc[frame]['track_id']), 
                                        id = "radio_all_tracks",)],
                                        className= "radio_items",
                                    align = 'center',
                                    style={'width': '100%', 
                                            'height': '350px', 
                                            'overflow': 'scroll', 
                                            'padding': '10px 10px 10px 20px'}), 
                                ],)
                        ])
    else:
        return "Select Tracks"


@app.callback(
    Output('frame_display_DB', 'children'),
    Input('frame_DB', 'data')
    )
def update_output(value):
    return (f'  Current Frame Number: {value}')


@app.callback(
    Output('hidden-div', 'children'),
    Output("assign_track_output", "children"),
    Input('assign_track_bt', 'n_clicks'),
    State('radio_all_tracks', 'value'),
    State("radio_players_A", 'value'),
    prevent_initial_call=True)
def update_player_tracks(assignBt, track_id, player_id):
    if assignBt:
        global dic_tracks
        global unique_tracks
        global dic

        cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
        
        player_frames = api_detections.get_player_frames(0, player_id)
        track_frames = api_detections.get_track_frames(0, track_id)
        intersection = [val for val in track_frames if val in player_frames]

        if cbcontext == 'assign_track_bt.n_clicks':
            if intersection: 
                api_detections.delete_detection_list(0, track_id, intersection) # maybe check if it has an item in it first
            api_detections.assign_track(0, player_id, track_id)
        
        # UPDATE LOCATION (Works) ///////////////////////////////////////////////////////////////////////////////////////////////////////////
        dic = api_detections.get_frame_detections(0)
        dic_tracks, unique_tracks = api_detections.get_tracks(0)

        return None, "Track successfully assigned."
    else:
        return None, None


# Callback for delete
@app.callback(
    Output('hidden-div2', 'children'),
    Output('hidden_div_j2', 'children'),
    Output('hidden_div_j3', 'children'),
    Input('delete_bt', 'n_clicks'),
    State('radio_all_tracks', 'value'),
    prevent_initial_call=True)
def delete_track(delete_bt, track_id):
    global dic_tracks
    global unique_tracks
    global dic

    if track_id is None:
        return (None, None, None)

    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if cbcontext == 'delete_bt.n_clicks':
        api_detections.delete_track(0, track_id)

    # UPDATE LOCATION ///////////////////////////////////////////////////////////////////////////////////////////////////////////
    dic = api_detections.get_frame_detections(0)
    dic_tracks, unique_tracks = api_detections.get_tracks(0)

    return (None, None, None)


@app.callback(
    Output('team_buttons', 'children'),
    Input("hidden_div_init_input", "children"),
    State("game_id", "data"))
def init_team_buttons(hidden_div, game_id):

    global a_name
    global b_name

    if not game_id: 
        game_id = 0

    a_name, b_name = api_game.get_team_names(game_id)

    print ("Callback triggered")
    return html.Div( children = [dbc.Button(str(a_name), id="but7", outline=True, style={ "font-size": "12px"}),
           dbc.Button(str(b_name), id="but8", outline=True, style={"margin-left": "5px","font-size": "12px"})])


def draw_tracks(fig, currentFrame, switches_value):

    global dic
    if not dic:
        dic = api_detections.get_frame_detections(0)


    frame_df = dic[currentFrame] # api_detections.gfd(0, currentFrame) # 
    unassinged_is_checked = False
    assigned_is_checked = False
    
    if (len(switches_value)==2):
        unassinged_is_checked = True
        assigned_is_checked = True

    if (len(switches_value)==1):
        if (switches_value[0]==1):
            unassinged_is_checked = False
            assigned_is_checked = True
        if (switches_value[0]==2):
            unassinged_is_checked = True
            assigned_is_checked = False 
    
    if (len(switches_value)==0):
        unassinged_is_checked = False
        assigned_is_checked = False
    
    if (unassinged_is_checked and assigned_is_checked):
        for i in range(len(frame_df)):
            x0 = frame_df.iloc[i]['x0']
            y0 = frame_df.iloc[i]['y0']
            x1 = frame_df.iloc[i]['x1']
            y1 = frame_df.iloc[i]['y1']
            track_id = frame_df.iloc[i]['track_id']
            player_id = frame_df.iloc[i]['player_id']
            initials = frame_df.iloc[i]['initials']
            add_editable_box(fig, track_id, player_id, initials, x0, y0, x1, y1)

    elif (unassinged_is_checked and assigned_is_checked == 0):
        for i in range(len(frame_df)):
            player_id = frame_df.iloc[i]['player_id']
            if(player_id == -1):
                #print(player_id)
                x0 = frame_df.iloc[i]['x0']
                y0 = frame_df.iloc[i]['y0']
                x1 = frame_df.iloc[i]['x1']
                y1 = frame_df.iloc[i]['y1']
                track_id = frame_df.iloc[i]['track_id']
                player_id = frame_df.iloc[i]['player_id']
                initials = frame_df.iloc[i]['initials']
                add_editable_box(fig, track_id, player_id, initials, x0, y0, x1, y1)

    elif (assigned_is_checked and unassinged_is_checked == 0):
        for i in range(len(frame_df)):
            player_id = frame_df.iloc[i]['player_id']
            if(player_id != -1):
                #print(player_id)
                x0 = frame_df.iloc[i]['x0']
                y0 = frame_df.iloc[i]['y0']
                x1 = frame_df.iloc[i]['x1']
                y1 = frame_df.iloc[i]['y1']
                track_id = frame_df.iloc[i]['track_id']
                player_id = frame_df.iloc[i]['player_id']
                initials = frame_df.iloc[i]['initials']
                add_editable_box(fig, track_id, player_id, initials, x0, y0, x1, y1)     


    return fig 


def get_frame(current_frame):

    vidcap = cv2.VideoCapture(filename)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    hasFrames, image = vidcap.read()
    if not hasFrames: return None 
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image  = cv2.resize(image, dsize=(resolution))
    vidcap.release()
    return image 


@app.callback(
    Output('canvas_DB', 'figure'),

    # draw inputs 
    Output('hidden_div_j1', 'children'),
    Input('switches-input', 'value'),
    Input("hidden_div_j0", "children"),
    Input("hidden_div_j3", "children"),
    # end of draw inupts 

    Input('frame_DB', 'data'),
    State('section_DB', 'data'),
    State('frame_DB', 'data'),)
def update_player(switches_value, hiddenj0, hiddenj3, current_frame, section, frame_data):
    fig = px.imshow(get_frame(current_frame-1), binary_backend="jpg") # should subtract 1 b/c the video's frames are zero indexed while the slider is 1 indexed 
    fig.update_layout(
        xaxis= {
            'showgrid': False, # thin lines in the background
            'zeroline': False, # thick line at x=0
            'visible': False,  # numbers below
        },
        yaxis= {
            'showgrid': False, # thin lines in the background
            'zeroline': False, # thick line at x=0
            'visible': False,  # numbers below
        },
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        dragmode="drawrect",
    )
    draw_tracks(fig, current_frame, switches_value)

    return fig, None


@app.callback(
    Output('video_state_DB', 'data'),
    Output('playpause_DB', 'children'),
    Output('interval_DB', 'disabled'),
    Input('playpause_DB', 'n_clicks'),
    State('video_state_DB', 'data'),
    State('interval_DB', 'disabled'),
)
def player_state(play_button, video_state, interval_state):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    string = 'Pause' if interval_state else 'Play'
    text = html.Img(src = f'https://github.com/dianabisbe/Images/blob/main/{string}.png?raw=true',
                              style={'height':'30px'})
    

    video_state = not video_state 
    interval_state = not interval_state
    return video_state, text, interval_state

@app.callback(
    Output('frame_DB', 'data'),
    Output('slider_DB', 'value'),
    Input('previous_DB', 'n_clicks'),
    Input('next_DB', 'n_clicks'),
    Input('fastforward-10_DB', 'n_clicks'),
    Input('fastforward-50_DB', 'n_clicks'),
    Input('rewind-10_DB', 'n_clicks'),
    Input('rewind-50_DB', 'n_clicks'),
    Input('interval_DB', 'n_intervals'),
    Input('slider_DB', 'value'),
    Input('section_DB', 'data'),
    Input('gts_all_tracks', 'n_clicks'),
    Input('go_to_end', 'n_clicks'),
    State('slider_DB', 'min'),
    State('slider_DB', 'max'),
    State('frame_DB', 'data'),
    State('radio_all_tracks', 'value'),)
def update_frame(previous_DB, next_DB, ff10, ff50, rw10, rw50, interval, slider, section, gts, gte, slider_min, slider_max, data, radioValue):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]

    if cbcontext == "previous_DB.n_clicks":
        data = data - 1 if data != slider_min else data 
        return data, data 
    elif cbcontext == "next_DB.n_clicks":
        data = data + 1 if data != slider_max else data 
        return data, data 
    elif cbcontext == "fastforward-10_DB.n_clicks":
        data = data + 10 if data < (slider_max - 10) else slider_max
        return data, data 
    elif cbcontext == "fastforward-50_DB.n_clicks":
        data = data + 50 if data < (slider_max - 50) else slider_max
        return data, data 
    elif cbcontext == "rewind-10_DB.n_clicks":
        data = data - 10 if data > (slider_min + 9) else slider_min
        return data, data 
    elif cbcontext == "rewind-50_DB.n_clicks":
        data = data - 50 if data > (slider_min + 49) else slider_min
        return data, data 
    elif cbcontext =="gts_all_tracks.n_clicks":
        for i in range (0, unique_tracks):
            if radioValue:
                if int(dic_tracks[i]['track_id'][0]) == int(radioValue):
                    data = min(dic_tracks[i]['frame'])
                    return data, data 
            else:
                raise PreventUpdate
    elif cbcontext =="go_to_end.n_clicks":
        for i in range (0, unique_tracks):
            if radioValue:
                if int(dic_tracks[i]['track_id'][0]) == int(radioValue):
                    data = max(dic_tracks[i]['frame'])
                    return data, data
            else:
                raise PreventUpdate 
    elif cbcontext == 'interval_DB.n_intervals': data += 1; return data, data
    elif cbcontext == 'section_DB.data': return slider_min, slider_min
    else: data = slider; return slider, slider



@app.callback(
    Output("slider_DB", 'min'),
    Output("slider_DB", 'max'),
    Output("slider_DB", 'marks'),
    Output('section_DB', 'data'),
    Input('dropdown_DB', 'value'),
    State('section_DB', 'data')
)
def initialize_section_and_slider(sectionValue, data):
    minFrame = (sectionValue * framesPerSection) + 1
    if (sectionValue+1) != sections:
        maxFrame = (sectionValue+1) * framesPerSection
    else:
        maxFrame = (frame_count % framesPerSection) + (minFrame-1)


    diff = round((maxFrame - minFrame)/20)
    marks = [(minFrame-1)+x*diff for x in range(21)]
    if marks[0] % framesPerSection == 0:
        marks[0] += 1
    sliderMarks = {}
    for i in marks:
        sliderMarks[f'{i}'] = f'{i}'

    data = sectionValue 
    return minFrame, maxFrame, sliderMarks, data

# initializes the states 
@app.callback(Output('dropdown_DB', 'value'),
                Input('section_DB', 'modified_timestamp'),
                State('section_DB', 'data'),
                State('frame_DB', 'data'),
                State('video_state_DB', 'data'),
)
def initial(section_ts, sectiondata, framedata, video_state):
    # if section_ts is None:
        # raise PreventUpdate
    sectiondata = sectiondata or 0
    framedata = framedata or 0
    video_state = False 
    return sectiondata
