# INSTALL LIBRARIES ---------------------------------------------------------------------------------------------------------------------------
# Comment
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import os
from os.path import isfile, join
from skimage import io
import numpy as np
import psycopg2 as pg2
import pandas as pd
from dash.exceptions import PreventUpdate
import cv2  # from vid2frames


# FILE FUNCTION IMPORTS ----------------------------------------------------------------------------------------------------------------------

from app import app

from apps import add_track

from api import api_detections
from api import api_team
from api import api_player

# GET FRAMES FROM VIDEO OR STORAGE ############################################################################################################

########### NEW VID TO FRAMES###########

# vidcap = cv2.VideoCapture('Sample Soccer Video.mp4')
# frames = []

# def getFrame(sec):
#     vidcap.set(cv2.CAP_PROP_POS_MSEC, sec*1000)
#     hasFrames, image = vidcap.read()
#     if hasFrames:
#         # Instead of writing to directory, save to an image array
#         # cv2.imwrite(os.path.join(dirname,"image"+str(count) + ".jpg"), image)
#         image2 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#         frames.append(image2)
#     return hasFrames

# sec = 0
# frameRate = 0.02  # 30 frames per second?
# count = 1
# success = getFrame(sec)
# while success:
#     count = count + 1
#     sec = sec + frameRate
#     sec = round(sec, 2)
#     success = getFrame(sec)

########### END NEW VID TO FRAMES###########


########### OLD VID TO FRAMES###########

pathIn = './vid2img/'
frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
frames.sort(key=lambda x: int(x[5:-4]))

########### END OLD VID TO FRAMES###########


# GLOBAL VARIABLES #############################################################################################################################

maxFrames = len(frames)-1
player_tracks_counter = 0
all_tracks_counter = 0
viewable_tracks_counter = 0
player_tracks = ["17", "12"]  # Hardcoded until "assign track" is working

dic = api_detections.get_frame_detections(0)
dic_tracks, unique_tracks = api_detections.get_tracks(0)

# fetch the detections ----------------
df_detections = api_detections.get_game_detections(0)

# fetch the teams ------------------
df_teams = api_team.get_teams(0)
# fetch the players ----------------
df_players = api_player.get_players(0)


# NON-DASH FUNCTIONS ##############################################################################################################################


def add_editable_box(fig, track_id, x0, y0, x1, y1, name=None, color=None, opacity=1, group=None, text=None):
    fig.add_shape(
        editable=True,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        line_color=color,
        opacity=opacity,
        line_width=3,
        name=name,
    )
    fig.add_annotation(  # ((x0+x1)/2)
        x=((x0+x1)/2),
        y=y0-30,
        text="{0}".format(track_id),
        showarrow=False,  # True
        font=dict(
            family="Courier New, monospace",
            size=9,
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
        bgcolor="#ff7f0e",
        opacity=0.8
    )


def read_input():
    for i in range(maxFrames):
        fp = open("./detections/f" + str(i) + ".txt", "r")  # grab new file
        df = read_file(fp)
        dic[i] = df


def read_file(fp):  # returns complete dataframe
    df = pd.DataFrame([], columns=['id', 'x0', 'y0', 'x1', 'y1'])
    fp.read(16)  # get rid of dummy inputs
    for line in fp:  # loop for the rest of the inputs
        start, end = line.split("[")
        nums, garbage = end.split("]")
        garbage2, id_num = garbage.split(":")

        x, y, w, h = nums.split()
        x0 = float(x)
        y0 = float(y)
        x1 = x0 + float(w)
        y1 = y0 + float(h)

        df_temp = pd.DataFrame([[int(id_num), x0, y0, x1, y1]], columns=[
                               'id', 'x0', 'y0', 'x1', 'y1'])
        df = df.append(df_temp)
    return df


def updateSection(button_id):
    global section
    if button_id == "but7":
        section = "A"
    if button_id == "but8":
        section = "B"


# FUNCTION WITH RETURNED DASH COMPONENT #################################################################################################################

# DASH COMPONENTS #######################################################################################################################################

fig = px.imshow(io.imread(pathIn+frames[0]), binary_backend="jpg")  # OLD
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
# fig = px.imshow(frames[0], binary_backend="jpg")  NEW

# Button Sections for teams: ======================================================================================================================


# Retrive value for each team
a_row = df_players[df_players["team_id"] == 0]
b_row = df_players[df_players["team_id"] == 1]


# # Dash component for team A

sectionA = html.Div([
    html.Div(children=[
    dbc.Col([dbc.Button("Assign Track", id = 'assign_track_bt',color="secondary",block = True, style={"font-size": "12px","margin-bottom":"10px"}),
             dbc.Button("Create a track", id = 'create_track_bt', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},),],
             align = 'center',),
    dbc.Col([dcc.RadioItems(
    options=[
        {'label': str(a_row.iloc[i]["name"]), 'value': str(a_row.iloc[i]["player_id"])} for i in range(0, len(a_row))],
    #value=str(a_row.iloc[1]["player_id"]), 
    id = "radio_players_A",
   
    )],
    align = 'center',
    style={'width': '250px', 
           'height': '590px', 
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
             dbc.Button("Create a track", id = 'create_track', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},),],
             align = 'center',),
    dbc.Col([dcc.RadioItems(
    options=[
        {'label': str(b_row.iloc[i]["name"]), 'value': str(b_row.iloc[i]["player_id"])} for i in range(0, len(b_row))],
    #value=str(b_row.iloc[1]["name"]),  
    id = "radio_players_A",
   
    )],
    align = 'center',
    style={'width': '250px', 
           'height': '590px', 
           'overflow': 'scroll', 
           'padding': '10px 10px 10px 20px'
          }), 
    ],
    )

])


# Button Sections for Tracks: ====================================================================================================================

# Generate Function for ea/ track (player track)
def generate_player_tracks_row(i):
    global player_tracks_counter

    return dbc.Row(
        dbc.Col([
            dcc.Checklist(id="checkbox"+str(i), options=[
                          {'label': ' ', 'value': 'false', 'disabled': False}, ], value=['true']),
            dbc.Button(
                i,
                id="collbutt_playertrack" +
                str(i),
                className="mb-3",
                color="secondary",
                style={"font-size": "12px"},
            ),
            dbc.Collapse(
                dbc.Card(dbc.CardBody([
                    dbc.Row(dbc.Button("Modify Track: Go to Start("+str(
                        player_tracks_counter)+")", color="black", style={"font-size": "12px"}),),
                    dbc.Row(dbc.Button("Delete Track: Go to End("+str(
                        player_tracks_counter+1)+")", color="black", style={"font-size": "12px"}),),
                ])),
                id="coll_playertrack" +
                str(i),
                style={"font-size": "12px"}
            ),
        ]))


# Player Tracks Component
viewPlayerTracks = html.Div([
                            html.Div(children=[generate_player_tracks_row(
                                i) for i in player_tracks]),
                            ])


# Video Player Card ===============================================================================================================================


image_annotation_card = dbc.Card(
    id="imagebox",
    children=[
        dbc.CardHeader(html.Div(
            [
                dbc.FormGroup(
                            [
                                dbc.Checklist(
                                    options=[
                                        {"label": "Assigned Track Boxes", "value": 1}, #1 is assigned
                                        {"label": "Unassigned Track Boxes", "value": 2}, #2 is unassigned
                                    ],
                                    value=[1, 2],
                                    labelStyle = {'display': 'inline-block', 'margin-left':'100px'},
                                    id="switches-input",
                                    switch=True,
                                ),
                            ]
                        ),
            ]
        )),
        html.Div(id='hidden_div_j0', style= {'display':'none'}),
        dbc.CardBody(
            [
                html.Div(id="manual_annotation_output"),
                dcc.Interval(
                    id='frame_interval',
                    interval=500,
                    disabled=True,
                    n_intervals=0,      # number of times the interval has passed
                    max_intervals=maxFrames
                ),
                dcc.Graph(
                    id="graph",
                    style={'width': '1000px', 'height': '600px'},
                    figure=fig,
                    config={"modeBarButtonsToAdd": ["drawrect", "eraseshape"]},
                )
            ]
        ),
        dbc.CardFooter(
            [
                # Slider Component
                dcc.Slider(
                    id='frame-slider',
                    min=0,
                    max=maxFrames,
                    value=0,
                    step=1,
                    marks={round(i*maxFrames/16): '{}'.format(round(i*maxFrames/16))
                           for i in range(maxFrames)},
                ),
                html.Div(id='slider-output-container'),
                # Pause/Player Buttons
                dbc.ButtonGroup(
                    [
                        dbc.Button("Previous", id="previous", outline=True, style={
                                   "margin-left": "50px", "margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("Rewind", id="rewind", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("Play", id="playpause", outline=True,
                                   style={"margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("Fastforward", id="fastforward", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("  Next  ", id="next", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}),
                    ],
                    style={"width": "100%"}
                ),
            ]
        ),
    ],
    style={"margin-top": "20px", "margin-bottom": "20px", "margin-right": "10px"}
)


# Track List Card =============================================================================================================================


annotated_data_card = dbc.Card(
    [
        dbc.CardHeader(html.Div(
            [
                dbc.Button("All Tracks", id="all_tracks_bt", outline=True, style={
                       "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("Viewable Tracks", id="viewable_tracks_bt", outline=True, style={
                    "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("Player Tracks", id="player_tracks_bt",
                           outline=True, style={"font-size": "12px"}),
            ])),
        dbc.CardBody(
            [ 
                html.Div(id='hidden-div', style= {'display':'none'}),
                html.Div(id='hidden-div2', style= {'display':'none'}),
                html.Div(id='track_container', children=[html.Div([
                html.Div(children=[
                dbc.Col([dbc.Button("Modify Track", color="secondary",block = True, style={"font-size": "12px","margin-bottom":"10px"}),
                        dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},),],
                        align = 'center',),
                dbc.Col([dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}),
                        dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"},),],
                        align = 'center'),
                dbc.Col([dcc.RadioItems(
                options=[
                    {'label': 'Track ID: ' + str(dic_tracks[i]['track_id'][0]), 'value': str(dic_tracks[i]['track_id'][0])} for i in range(0, unique_tracks)],
                #value=str(list(dic_tracks.keys())[1]), 
                id = "radio_all_tracks",
            
                )],
                align = 'center',
                style={'width': '100%', 
                            'height': '500px', 
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

            ]
        ),
    ],
    style={"margin-top": "20px", "margin-bottom": "20px", "margin-right": "10px"}
)


# PLayer Lists Card ===========================================================================================================================


annotated_data_card2 = dbc.Card(
    [
        dbc.CardHeader(html.Div(
            [
                dbc.Button("Team A", id="but7", outline=True, style={
                       "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("Team B", id="but8", outline=True,
                           style={"font-size": "12px"}),
            ])),
        dbc.CardBody(
            [
                html.Div(id='container'),
                # dbc.Button("Regenerate Tracks", id="button_regen")
            ]
        ),
        dbc.CardFooter(
            [
                html.H6("Add Track Section"),
                html.Div(
                    [
                        dbc.Input(id="dashboard_input_start", placeholder="Start", type="number", min=0, step=1), # value
                        dbc.Input(id="dashboard_input_final", placeholder="Final", type="number", min=0, step=1), 
                    ]
                ),
                html.Div(
                    [
                        dbc.ButtonGroup(
                            [
                                dbc.Button("Set Start Frame", id="set_start"),
                                dbc.Button("Set Final Frame", id="set_final"),
                                dbc.Button("Add Track", id="add_track")
                            ]
                        )
                    ]
                ),
                html.Div(id="add_track_output"),
                html.Br(),
                html.Div(id="useless_output")
            ]
        ),
    ],
    
    style={"margin-top": "20px", "margin-bottom": "20px"}
)


# App Layout ====================================================================================================================================

layout = html.Div(  # was app.layout
    [
        # navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(image_annotation_card, md=7.5),
                        dbc.Col(annotated_data_card, md=2.5),
                        dbc.Col(annotated_data_card2, md=2.5),
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)

# CALLBACK FUNCTION DEFINITIONS #########################################################################################################################

# Callbacks for the Manual Annotation Portion ==========================================================

ma_output_fix = 0
@app.callback(
    Output("manual_annotation_output", "children"),
    Output("hidden_div_j0", "children"),
    Input('graph', 'relayoutData'),
    State('frame-slider', 'value'),
    State("radio_players_A", 'value'),
    prevent_initial_call=True)
def manual_annotation(graph_relayout, frame, player_id):
    global dic
    global ma_output_fix
    
    if (ma_output_fix == 0):
        ma_output_fix = 1
        return None, None

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
        
        df = df.reset_index() # needed because the add box indexing can overlap, causing multiple entries to be deleted
        df = df.drop(df[df['track_id'] == int(track_id)].index)
        dic[frame] = df

        # works, just commented out for now
        # api_detections.delete_detection(0, frame, track_id)

        return "Detection box deleted from frame {} and track {}".format(frame, track_id), None

    # ADD BOX ------------------------------------
    elif (new_num_boxes > old_num_boxes): 
        if (player_id is None):
            return "Need a player_id selected to add a box", None
        elif (old_num_boxes+1 == new_num_boxes): # good condition
            ctr = 0
            df_temp = []

            for box in graph_relayout['shapes']: # this will only have one iteration (b/c there should only be one bounding box)
                if ctr == old_num_boxes:
                    df_temp = pd.DataFrame([[0, frame, box['x0'], box['y0'], box['x1'], box['y1'], -2, player_id]], columns=['game_id', 'frame', 'x0', 'y0', 'x1', 'y1', 'track_id', 'player_id'])
                    dic[frame] = dic[frame].append(df_temp)

                    # works, just commented out for now
                    # api_detections.add_detection(0, frame, box['x0'], box['y0'], box['x1'], box['y1'], -2, player_id)

                    return "Box successfully added (not db linked) [norm]", None
                else:
                    ctr += 1
        elif (old_num_boxes >= new_num_boxes):
            return "Bad Output: None drawn -or- Deleted and drawn", None
        elif (old_num_boxes+1 < new_num_boxes):
            return "Bad Output: Too many drawn", None
        else:
            return "Unknown ERROR", None

    # ERROR --------------------------------------
    else:
        return "Unknown ERROR", None

# Callbacks for the Add Track Portion ==================================================================

# callback for set start frame
@app.callback(
    Output("dashboard_input_start", "value"),
    Input("set_start", "n_clicks"),
    State('frame-slider', 'value'))
def set_start_frame(n_clicks, frame):
    # probably want to include the values for the other side (and this goes for that side too) to ensure they don't pass each other in negative ways
    if n_clicks is not None:
        return frame

# callback for set final frame
@app.callback(
    Output("dashboard_input_final", "value"),
    Input("set_final", "n_clicks"),
    State('frame-slider', 'value'))
def set_start_frame(n_clicks, frame):
    if n_clicks is not None:
        return frame

# callback for add track button
@app.callback(
    Output("add_track_output", "children"),
    Output("start_frame_add", "data"),
    Output("final_frame_add", "data"),
    Input("add_track", "n_clicks"),
    State("dashboard_input_start", "value"),
    State("dashboard_input_final", "value"),
    State("start_frame_add", "data"),
    State("final_frame_add", "data"),)
def add_track(n_clicks, start_frame, final_frame, storage1, storage2):
    if n_clicks is not None:
        if ((start_frame is None) or (final_frame is None)):
            return ("Must have inputs for start and final frame.", start_frame, final_frame)
        elif start_frame >= final_frame:
            return ("Start frame must be less than final frame.", start_frame, final_frame)
        else:
            # now need some way to store the relevant values
            # Want to eventually use dcc.store or something like that
            return (dbc.Button("Now Click Here", id="go_to_add_track", href='/apps/add_track'), start_frame, final_frame)
    else:
        return ("{}".format(storage1), start_frame, final_frame)

# callback to regenerate the detections dataframe
@app.callback(
    Output("useless_output", "children"),
    Input("button_regen", "n_clicks"),)
def add_track_return(n_clicks):
    global dic
    dic = api_detections.get_frame_detections(0)
    return "test {}".format(n_clicks)

# --------------------------------------------------

# Call back that toggles between Team A and Team B
@app.callback(Output('container', 'children'),
              Input("but7", 'n_clicks'),
              Input("but8", 'n_clicks'))
def display(btn1, btn2):

    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    updateSection(button_id)

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
              State("frame_interval", 'n_intervals'),
              State("radio_players_A", 'value'))
def display_2(btn1, btn2, btn3, frame, value):
    ctx = dash.callback_context

    global dic_tracks
    global unique_tracks

    dic_tracks, unique_tracks = api_detections.get_tracks(0)

    #print("THIS IS BEING CALLED")

    if not ctx.triggered:
        button_id = 'No clicks yet'
        return  html.Div([
                html.Div(children=[
                dbc.Col([dbc.Button("Modify Track", color="secondary",block = True, style={"font-size": "12px","margin-bottom":"10px"}),
                        dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},),],
                        align = 'center',),
                dbc.Col([dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}),
                        dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"},),],
                        align = 'center'),
                dbc.Col([dcc.RadioItems(
                options=[
                    {'label': 'Track ID: ' + str(dic_tracks[i]['track_id'][0]), 'value': str(dic_tracks[i]['track_id'][0])} for i in range(0, unique_tracks)],
                #value=str(list(dic_tracks.keys())[1]), 
                id = "radio_all_tracks",
            
                )],
                align = 'center',
                style={'width': '100%', 
                            'height': '500px', 
                            'overflow': 'scroll', 
                            'padding': '10px 10px 10px 20px'
                    }), 
                ],
                )
            ])
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    #str(dic_tracks[i]['track_id'][0]

    if button_id == "all_tracks_bt":
        return  html.Div([
                html.Div(children=[
                dbc.Col([dbc.Button("Modify Track", color="secondary",block = True, style={"font-size": "12px","margin-bottom":"10px"}),
                        dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, style={"font-size": "12px","margin-bottom":"10px"},),],
                        align = 'center',),
                dbc.Col([dbc.Button("Delete Track",id = 'delete_bt', color="secondary",block = True, style={"font-size": "12px", "margin-bottom":"10px"}),
                        dbc.Button("Go to Start", id = 'gts_all_tracks',color="secondary", block = True, style={"font-size": "12px", "margin-bottom":"10px"},),],
                        align = 'center'),
                dbc.Col([dcc.RadioItems(
                options=[
                    {'label': 'Track ID: ' + str(dic_tracks[i]['track_id'][0]), 'value': str(dic_tracks[i]['track_id'][0])} for i in range(0, unique_tracks)],
                #value=str(list(dic_tracks.keys())[1]), 
                id = "radio_all_tracks",
            
                )],
                align = 'center',
                style={'width': '100%', 
                            'height': '500px', 
                            'overflow': 'scroll', 
                            'padding': '10px 10px 10px 20px'
                    }), 
                ],
                )
            ])

    if button_id == "viewable_tracks_bt":
        df_detections = api_detections.get_game_detections(0)
        viewable_row = df_detections[df_detections["frame"] == frame]
        return html.Div([
                        html.Div(children=[
                            dbc.Col([dbc.Button("Modify Track", color="secondary",block = True, 
                                        style={"font-size": "12px","margin-bottom":"10px"}),
                                    dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, 
                                        style={"font-size": "12px","margin-bottom":"10px"},),],
                                    align = 'center',),
                            dbc.Col([dbc.Button("Delete Track", id = 'delete_bt',color="secondary",block = True, 
                                        style={"font-size": "12px", "margin-bottom":"10px"}),
                                    dbc.Button("Go to Start", id = 'gts_all_tracks', color="secondary", block = True, 
                                        style={"font-size": "12px", "margin-bottom":"10px"},),],
                                    align = 'center'),
                            dbc.Col([dcc.RadioItems(
                                options=[
                                    {'label': 'Track ID: ' + str(viewable_row.iloc[i]['track_id']), 
                                    'value': str(viewable_row.iloc[i]['track_id'])} for i in range(0, len(viewable_row))],
                                # labelStyle = {'textAlign':'center'},
                                #value=str(viewable_row.iloc[frame]['track_id']), 
                                id = "radio_all_tracks",)],
                            align = 'center',
                            style={'width': '100%', 
                                    'height': '550px', 
                                    'overflow': 'scroll', 
                                    'padding': '10px 10px 10px 20px'}), 
                        ],)
                ])

    if button_id == "player_tracks_bt":

        if value is None:
            return 'Select a Player to View Tracks'
        
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
                return html.Div(children=[
                                dbc.Col([dbc.Button("Modify Track", color="secondary",block = True, 
                                            style={"font-size": "12px","margin-bottom":"10px"}),
                                        dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, 
                                            style={"font-size": "12px","margin-bottom":"10px"},),],
                                        align = 'center',),
                                dbc.Col([dbc.Button("Delete Track", color="secondary",block = True, 
                                            style={"font-size": "12px", "margin-bottom":"10px"}),
                                        dbc.Button("Go to Start", id = 'gts_all_tracks', color="secondary", block = True, 
                                            style={"font-size": "12px", "margin-bottom":"10px"},),],
                                        align = 'center'),
                                dcc.Markdown('No Tracks have been assigned to this player',
                                style={'width': '100%', 
                                            'font-size': '16px',
                                            'height': '550px', 
                                            'overflow': 'scroll', 
                                            'padding': '10px 10px 10px 20px'}),
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
                                    dbc.Col([dbc.Button("Modify Track", color="secondary",block = True, 
                                                style={"font-size": "12px","margin-bottom":"10px"}),
                                            dbc.Button("Go to End", id = 'go_to_end', color="secondary", block = True, 
                                                style={"font-size": "12px","margin-bottom":"10px"},),],
                                            align = 'center',),
                                    dbc.Col([dbc.Button("Delete Track", color="secondary",block = True, 
                                                style={"font-size": "12px", "margin-bottom":"10px"}),
                                            dbc.Button("Go to Start", id = 'gts_all_tracks', color="secondary", block = True, 
                                                style={"font-size": "12px", "margin-bottom":"10px"},),],
                                            align = 'center'),
                                    dbc.Col([dcc.RadioItems(
                                        options=[
                                            {'label': 'Track ID: ' + str(trackList[i]), 
                                            'value': str(trackList[i])} for i in range( len(trackList))],
                                        # labelStyle = {'textAlign':'center'},
                                        #value=str(viewable_row.iloc[frame]['track_id']), 
                                        id = "radio_all_tracks",)],
                                    align = 'center',
                                    style={'width': '100%', 
                                            'height': '550px', 
                                            'overflow': 'scroll', 
                                            'padding': '10px 10px 10px 20px'}), 
                                ],)
                        ])
    else:
        return "Select Tracks"


# Call back for video Player/Pause
@app.callback(
    Output('frame_interval', 'disabled'),
    Output('playpause', 'children'),
    Input('playpause', 'n_clicks'),
    State('frame_interval', 'disabled'),
)
def togglePlay(play, isPaused):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    text = 'Play'

    if cbcontext == "playpause.n_clicks":
        if isPaused == True:
            isPaused = False
            text = 'Pause'
        elif isPaused == False:
            isPaused = True
        else:
            raise PreventUpdate
    return (isPaused, text)


# Video Display Callback
# Go to Start
# Go to End
# Callback for assign/unassign toggle
@app.callback(
    Output('graph', 'figure'),
    Output('frame_interval', 'n_intervals'),
    Output('frame-slider', 'value'),
    Input('frame_interval', 'n_intervals'),
    Input('frame-slider', 'value'),
    Input('previous', 'n_clicks'),
    Input('next', 'n_clicks'),
    Input('gts_all_tracks', 'n_clicks'),
    Input('go_to_end','n_clicks'),
    Input('switches-input', 'value'),
    Input("hidden_div_j0", "children"),
    State('frame_interval', 'disabled'),
    State('radio_all_tracks', 'value'),
)
def update_figure(interval, slider, previousBut, nextBut, gtsBut ,gteBut, switches_value, hidden_div_j0, isPaused, value):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    currentFrame = 0

    global dic

    if isPaused == False:
        if interval is None:
            interval = 0
        currentFrame = interval
    elif isPaused == True:
        currentFrame = interval
        if cbcontext == "previous.n_clicks":
            if(currentFrame != 0):
                currentFrame += -1
        if cbcontext == "next.n_clicks":
            if(currentFrame != maxFrames):
                currentFrame += 1
        if cbcontext =="gts_all_tracks.n_clicks":
            if cbcontext == "frame-slider.value":
                currentFrame = slider
            else:  
                for i in range (0, unique_tracks):
                    if int(dic_tracks[i]['track_id'][0]) == int(value):
                        currentFrame = min(dic_tracks[i]['frame'])
        if cbcontext =="go_to_end.n_clicks":
            if cbcontext == "frame-slider.value":
                currentFrame = slider
            else:
                for i in range (0, unique_tracks):
                    if int(dic_tracks[i]['track_id'][0]) == int(value):
                        currentFrame = max(dic_tracks[i]['frame'])
    if cbcontext == "frame-slider.value":
        currentFrame = slider
    # print(currentFrame)

    fig = px.imshow(
        io.imread(pathIn+frames[currentFrame]), binary_backend="jpg")  # OLD
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
    # fig = px.imshow(frames[currentFrame], binary_backend="jpg") # NEW
    frame_df = dic[currentFrame]
    
    # print("\nCurrent Frame Bounding Boxes:")
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
    
    if   (unassinged_is_checked and assigned_is_checked):
        for i in range(len(frame_df)):
            x0 = frame_df.iloc[i]['x0']
            y0 = frame_df.iloc[i]['y0']
            x1 = frame_df.iloc[i]['x1']
            y1 = frame_df.iloc[i]['y1']
            id_num = frame_df.iloc[i]['track_id']
            add_editable_box(fig, id_num, x0, y0, x1, y1)

    elif (unassinged_is_checked and assigned_is_checked == 0):
        for i in range(len(frame_df)):
            player_id = frame_df.iloc[i]['player_id']
            if(player_id == -1):
                #print(player_id)
                x0 = frame_df.iloc[i]['x0']
                y0 = frame_df.iloc[i]['y0']
                x1 = frame_df.iloc[i]['x1']
                y1 = frame_df.iloc[i]['y1']
                id_num = frame_df.iloc[i]['track_id']
                add_editable_box(fig, id_num, x0, y0, x1, y1)

    elif (assigned_is_checked and unassinged_is_checked == 0):
        for i in range(len(frame_df)):
            player_id = frame_df.iloc[i]['player_id']
            if(player_id != -1):
                #print(player_id)
                x0 = frame_df.iloc[i]['x0']
                y0 = frame_df.iloc[i]['y0']
                x1 = frame_df.iloc[i]['x1']
                y1 = frame_df.iloc[i]['y1']
                id_num = frame_df.iloc[i]['track_id']
                add_editable_box(fig, id_num, x0, y0, x1, y1)       

    # print(id_num, x0, y0, x1, y1)
    return (fig, currentFrame, currentFrame)

# Callback for Slider
@app.callback(
    dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('frame_interval', 'n_intervals')])
def update_output(value):
    return '  Current Frame "{}"'.format(value)

# Callback for Assign Tracks
@app.callback(
    Output('hidden-div', 'children'),
    Input('assign_track_bt', 'n_clicks'),
    State('radio_all_tracks', 'value'),
    State("radio_players_A", 'value')
)
def update_player_tracks(assignBt, trackIDValue, playerIDValue):
    global dic_tracks
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]

    global dic

    if cbcontext == 'assign_track_bt.n_clicks':
        conn = pg2.connect(database='soccer',
            user='postgres',
            host='localhost',  # localhost-------------------!
            password='root')
        cur = conn.cursor()
        cur.execute('''UPDATE detections SET player_id = %s WHERE track_id = %s''', (playerIDValue, trackIDValue))
        conn.commit()
        cur.close()
        conn.close()
    
    # Instead of updating the whole dictionary, update the assigned track for efficiency ------ change to make!
    dic = api_detections.get_frame_detections(0)

    return '  Test: "{}"'.format(playerIDValue) 

# Callback for delete
@app.callback(
    Output('hidden-div2', 'children'),
    Input('delete_bt', 'n_clicks'),
    State('radio_all_tracks', 'value'),
)
def delete_track(delete_bt, track_id):

    global dic

    if track_id is None:
        return track_id

    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if cbcontext == 'delete_bt.n_clicks':
        print("It entered")
        conn = pg2.connect(database='soccer',
            user='postgres',
            host='localhost',  # localhost-------------------!
            password='root')
        cur = conn.cursor()
        cur.execute('''DELETE FROM detections WHERE track_id = %s''' % track_id)
        conn.commit()
        cur.close()
        conn.close()

    # Instead of updating the whole dictionary, update the deleted track for efficiency ------ change to make!
    dic = api_detections.get_frame_detections(0)
