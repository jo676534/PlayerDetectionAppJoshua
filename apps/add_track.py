# INSTALL LIBRARIES ---------------------------------------------------------------------------------------------------------------------------

from typing import final
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
# import psycopg2 as pg2
import pandas as pd
from dash.exceptions import PreventUpdate
import cv2  # from vid2frames

from app import app

from api import api_detections
from api import api_team
from api import api_player

from .pysot.tools import demo


# GLOBAL VARIABLES #############################################################################################################################

pathIn = './vid2img/'
frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))] 
frames.sort(key=lambda x: int(x[5:-4]))

maxFrames = 0
state = 0 # 0 is not submitted yet, 1 is submitted 
state_save = 0 # 0 is not run, 1 is run, 2 is run and saved, 99 is currently running and disables functionality

dic = {}

# NORMAL FUNCTIONS #############################################################################################################################

def add_editable_box(fig, id_num, x0, y0, x1, y1, name=None, color=None, opacity=1, group=None, text=None):
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
    fig.add_annotation( #((x0+x1)/2)
        x=((x0+x1)/2),
        y=y0-30,
        text="{0}".format(id_num),
        showarrow=False, #True
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
        ax=0, #20
        ay=0, #-30
        bordercolor="#c7c7c7",
        borderwidth=1, #2
        borderpad=2, #4
        bgcolor="#ff7f0e",
        opacity=0.8
    )

# DASH COMPONENTS ##############################################################################################################################

# Card for the user interactions on the right side
right_side = dbc.Card(
    [
        dbc.CardHeader(
            [
                html.H2("Bounding Box Submit Area"),
                html.Div(id="test_output")
            ]
        ),
        dbc.CardBody(
            [
                html.H5("Instructions (Part 1):"),
                #html.Div("By default you can click and drag to draw an annotation bounding box on the image to the left. Once you draw a box around the player you are intending to track click on the submit box button to start the tracking."),
                html.Div("1. The video player is locked at the start frame until the tracker is finished running."),
                html.Div("2. Click and drag to draw an annotation bounding box around the intented player on the image."),
                html.Div("3. An already existing box can be interacted with by clicking on it's edges."),
                html.Div("  3a. It can then be modified by draging one of the corners."),
                html.Div("  3b. It can then be deleted by clicking \"Erase active shape\" in the top right corner above the image."),
                html.Div("4. Ensure there is only one bounding box around the intended player."),
                html.Div("5. Click \"Start Tracker\" below and wait for it to finish running."),
                html.Div("6. Don't press the button while the tracker is running."),
                html.Div("7. Once the tracker is finished, proceed to the area below."),
                #html.Br(),
                html.Button('Start Tracker', id='next_page', n_clicks=0),
                html.Br(),
                dbc.Spinner(html.Div(id='button_output'))
            ]
        ),
        dbc.CardFooter(
            [
                html.H5("Instructions (Part 2):"),
                html.Div("There are now three primary options for using the detection track:"),
                html.Div("1. If there are no errors with the detections you can click \"Save Detection Track\" to finish."),
                html.Div("2. If part of the track is correct you can input a start and end frame below before saving the detection track to only save the frames within that window."),
                html.Div("3. If you'd like to remove the detections all together and start over you can reset the tracker and try again."),
                html.Div(""),
                #html.Br(),
                html.Div(
                    [
                        dbc.Input(id="input_start", placeholder="Start", type="number", min=0, step=1, style={'width': '25%', 'display': 'inline-block', "margin-left": "0px", "margin-right": "15px",}),
                        dbc.Input(id="input_final", placeholder="Final", type="number", min=0, step=1, style={'width': '25%', 'display': 'inline-block', "margin-left": "15px", "margin-right": "15px",}),
                    ]
                ),
                html.Div(
                    [
                        dbc.Button("Set Start Frame", id="set_start_add", style={'width': '25%', 'display': 'inline-block', "margin-left": "0px", "margin-right": "15px",}),
                        dbc.Button("Set Final Frame", id="set_final_add", style={'width': '25%', 'display': 'inline-block', "margin-left": "15px", "margin-right": "15px",}),
                    ]
                ),
            ]
        )
    ],
    style={"margin-top": "20px", "margin-bottom": "20px", "margin-right": "10px"})

# Card for final buttons
end_buttons = dbc.Card(
    [
        dbc.ButtonGroup(
            [
                dbc.Button("Save Detection Track", id="button_save"),
                dbc.Button("Reset Tracker", id="button_reset", n_clicks=0),
                dbc.Button("Quit", id="button_quit_1", href='/apps/dashboard')
            ]
        ),
        html.Div(id="save_output")
    ])

# Layout
layout = html.Div(
    [
        #navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(id="video_card", md=7.5),
                        dbc.Col(children=[right_side, end_buttons], md=5),
                    ],
                ),
            ],
            fluid=True,
        ),
    ])

# CALLBACKS START HERE #########################################################################################################################

# Initialization Callback (should create the image annotation card)
@app.callback(
    Output("video_card", "children"),
    Input("start_frame_add", "data"),
    Input("final_frame_add", "data"),
    Input('player_id_add', 'data'))
def initalizer(start_frame, final_frame, player_id):
    print("INITIALIZER CALLED w/SF: {}".format(start_frame))
    print("chosen player_id: {}".format(player_id))

    # set up the fig and inital variables
    global frames
    frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))] 
    frames.sort(key=lambda x: int(x[5:-4]))
    frames = frames[start_frame:final_frame+1]

    global maxFrames
    maxFrames = len(frames)-1 # need to fix

    global dic
    dic = api_detections.get_partial_frame_detections(0, start_frame, final_frame)
    print(len(dic))

    fig = px.imshow(io.imread(pathIn+frames[0]), binary_backend="jpg")
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        dragmode="drawrect",
    )

    # and then the big one
    return dbc.Card(
        id="imagebox_add",
        children=[
            dbc.CardHeader(
                html.H2("Annotation Area")
            ),
            dbc.CardBody(
                [
                    dcc.Interval(
                        id='frame_interval_add',
                        interval=500,
                        disabled=True,
                        n_intervals=0,      # number of times the interval has passed
                        max_intervals=maxFrames
                    ),
                    dcc.Graph(
                        id="graph_box",
                        style={'width':'1000px', 'height':'600px'},
                        figure=fig,
                        config={"modeBarButtonsToAdd": ["drawrect", "eraseshape"]},
                    )
                ]
            ),
            dbc.CardFooter(
                [
                    # Slider Component
                    dcc.Slider(
                        id='frame-slider_add',
                        min=0,
                        max=maxFrames,
                        value=0,
                        step=1,
                        marks={round(i*maxFrames/4): '{}'.format(round(i*maxFrames/4))
                            for i in range(maxFrames)},
                    ),
                    html.Div(id='slider-output-container_add'),
                    # Pause/Player Buttons
                    dbc.ButtonGroup(
                        [   
                            dbc.Button("Go back 50", id="rewind_50", outline=True, style={
                                    "margin-right": "15px", "margin-bottom": "15px"}),
                            dbc.Button("Go back 10", id="rewind_10", outline=True, style={
                                    "margin-right": "15px", "margin-bottom": "15px"}),
                            dbc.Button("Previous", id="previous_add", outline=True, style={
                                    "margin-left": "50px", "margin-right": "15px", "margin-bottom": "15px"}),
                            dbc.Button("Play", id="playpause_add", outline=True,
                                    style={"margin-right": "15px", "margin-bottom": "15px"}),
                            dbc.Button("Next", id="next_add", outline=True, style={
                                    "margin-right": "15px", "margin-bottom": "15px"}),
                            dbc.Button("Go forward 10", id="fastforward_10", outline=True, style={
                                    "margin-right": "15px", "margin-bottom": "15px"}),
                            dbc.Button("Go forward 50", id="fastforward_50", outline=True, style={
                                    "margin-right": "15px", "margin-bottom": "15px"}),
                        ],
                        style={"width": "100%"}
                    ),
                ]
            ),
        ],
        style={"margin-top": "20px", "margin-bottom": "20px"}
    )


# Call back for video Player/Pause
@app.callback(
    Output('frame_interval_add', 'disabled'),
    Output('playpause_add', 'children'),
    Input('playpause_add', 'n_clicks'),
    State('frame_interval_add', 'disabled'),)
def togglePlay_add(play, isPaused):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    text = 'Play'

    if cbcontext == "playpause_add.n_clicks":
        if isPaused == False or state == 0:
            isPaused = True
        elif isPaused == True:
            isPaused = False
            text = 'Pause'
        else:
            raise PreventUpdate
    return (isPaused, text)


# Video Display Callback
@app.callback(
    Output('graph_box', 'figure'),
    Output('frame_interval_add', 'n_intervals'),
    Output('frame-slider_add', 'value'),
    Output('graph_box', 'relayoutData'),
    Input('frame_interval_add', 'n_intervals'),
    Input('frame-slider_add', 'value'),
    Input('previous_add', 'n_clicks'),
    Input('next_add', 'n_clicks'),
    Input ('rewind_10', 'n_clicks'),
    Input ('rewind_50', 'n_clicks'),
    Input ('fastforward_10', 'n_clicks'),
    Input ('fastforward_50', 'n_clicks'),
    State('frame_interval_add', 'disabled'),
    State('graph_box', 'relayoutData'),
    prevent_initial_call=True)
def update_figure_add(interval, slider, previousBut, nextBut,rewind10, rewind50, fastforward10, fastforward50, isPaused, graph_relayout):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    currentFrame = 0
    
    # check the state to stop the user from scrolling if they haven't input a new track
    if state != 0:
        if isPaused == False:
            if interval is None:
                interval = 0
            currentFrame = interval
        elif isPaused == True:
            currentFrame = interval
            if cbcontext == "previous_add.n_clicks":
                if(currentFrame != 0):
                    currentFrame += -1
            if cbcontext == "next_add.n_clicks":
                if(currentFrame != maxFrames):
                    currentFrame += 1
            if cbcontext == "rewind_10.n_clicks":
                if(currentFrame > 10):
                    currentFrame += -10
            if cbcontext == "rewind_50.n_clicks":
                if(currentFrame > 50):
                    currentFrame += -50
            if cbcontext == "fastforward_10.n_clicks":
                if(currentFrame < maxFrames-10):
                    currentFrame += 10
            if cbcontext == "fastforward_50.n_clicks":
                if(currentFrame < maxFrames-50):
                    currentFrame += 50
        if cbcontext == "frame-slider_add.value":
            currentFrame = slider
    
    fig = px.imshow(io.imread(pathIn+frames[currentFrame]), binary_backend="jpg") # OLD # fig = px.imshow(frames[currentFrame], binary_backend="jpg") # NEW
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        dragmode="drawrect",
    )
    
    # Need a new bit of code here to draw the singular new bounding box after it has been set up
    if state != 0: # draw the new bounding box
        x0 = detections_df.iloc[currentFrame]['x0']
        y0 = detections_df.iloc[currentFrame]['y0']
        x1 = detections_df.iloc[currentFrame]['x1']
        y1 = detections_df.iloc[currentFrame]['y1']
        track_id = detections_df.iloc[currentFrame]['track_id']
        add_editable_box(fig, track_id, x0, y0, x1, y1)

    # print("%%% Graph Relayout Length: {} %%%".format(len(graph_relayout['shapes'])))
    return (fig, currentFrame, currentFrame, {'shapes': []}) 
# the empty graph_relayout may cause problems later down the line when we actually want to draw the bounding box
# solution would be to pass the actual graph_relayout depending on the context/state


# Callback for Slider
@app.callback(
    dash.dependencies.Output('slider-output-container_add', 'children'),
    [dash.dependencies.Input('frame_interval_add', 'n_intervals')])
def update_output_add(value):
    return 'Current Frame "{}"'.format(value)


# Callback for the submit button
@app.callback(
    Output('button_output', 'children'),
    Input('next_page', 'n_clicks'),
    State('graph_box', 'relayoutData'),
    State("start_frame_add", "data"),
    State("final_frame_add", "data"),
    prevent_initial_call=True)
def submit_box(n_clicks, graph_relayout, start_frame, final_frame):
    global detections_df
    global state

    if (state == 99):
        return "The tracker is still running, please wait for it to be finished."

    if (state == 1):
        return "The tracker has already been run"
    
    if graph_relayout is None: return '' # stops the error
    
    if (not 'shapes' in graph_relayout):
        # this is for whenever the user adjusts their bounding box. the info contained in the graph_relayout is changed and doesn't have shapes inside it so we need to check for and read a new form of info
        # a possible error of sorts is that the user could have two (or more) bounding boxes, adjust the zeroth box (the first they drew) and then submit and it would run
        if 'shapes[0].x0' in graph_relayout: 
            state = 99
            detections_df = demo.rt_track(start_frame, final_frame, graph_relayout['shapes[0].x0'], graph_relayout['shapes[0].y0'], graph_relayout['shapes[0].x1'], graph_relayout['shapes[0].y1'])
            state = 1
            return "The tracking algorithm has now finished, you can review the output in the video player."
        # otherwise we just display that there is an improper bounding box configuration
        return "Improper bounding box configuration"
    elif (len(graph_relayout['shapes']) == 0):
        return "You have to draw one bounding box"
    elif (len(graph_relayout['shapes']) == 1): # this is the success case
        state = 99
        for box in graph_relayout['shapes']: # this will only have one iteration (b/c there should only be one bounding box)
            detections_df = demo.rt_track(start_frame, final_frame, box['x0'], box['y0'], box['x1'], box['y1'])
        state = 1
        return "The tracking algorithm has now finished, you can review the output in the video player."
    else:
        return "There are too many bounding boxes"
# end submit_box


# Set start frame callback
@app.callback(
    Output("input_start", "value"),
    Input("set_start_add", "n_clicks"),
    State("frame-slider_add", "value"),
    prevent_initial_call=True)
def set_start_add(n_clicks, frame):
    if n_clicks is not None:
        return frame


# Set final frame callback
@app.callback(
    Output("input_final", "value"),
    Input("set_final_add", "n_clicks"),
    State("frame-slider_add", "value"),
    prevent_initial_call=True)
def set_start_add(n_clicks, frame):
    if n_clicks is not None:
        return frame


# Save Detection Callback
@app.callback(
    Output("save_output", "children"),
    Input("button_save", "n_clicks"),
    Input("button_reset", "n_clicks"),
    State("input_start", "value"), # start_frame (represents the start value for a subset selection of frames)
    State("input_final", "value"), # final_frame 
    State("start_frame_add", "data"), # sf (represents the original start frame value)
    State("final_frame_add", "data"), # ff
    State('player_id_add', 'data'),
    prevent_initial_call=True)
def save_detection(save_clicks, reset_clicks, start_frame, final_frame, sf, ff, player_id):
    # STATES TO PRECEED CHECKING THE INPUT
    global state
    global detections_df

    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    print(cbcontext)

    # first check for if it was reset button
    if cbcontext == "button_reset.n_clicks":
        detections_df = []
        state = 0
        return "Reset Complete"

    # Check states to make sure we're ready to take the input
    if state == 0 or state == 99:
        return "The tracker needs to be run first"
    elif state == 2:
        return "Track already saved. Now click quit to return."
    elif state != 1:
        return "Unkown ERROR"

    # STATES FOR ACTUAL INPUT
    # Good State: user input nothing and wants the whole clip
    if (start_frame is None) and (final_frame is None):
        # need to check for player track overlap
        temp_frame = sf
        while temp_frame <= ff:
            if (int(player_id) in dic[temp_frame].player_id):
                return "This player already has a track assigned to them within this selection of frames."
            temp_frame += 1
        
        state = 2
        #api_detections.save_track(0, detections_df, frame_value, -1)
        return "Track saved. Now click quit to return."
    # Bad State: user input one but not the other
    elif (start_frame is None) or (final_frame is None): 
        return "Need either both inputs or neither"
    # Bad State: start is greater than or equal to final
    elif (start_frame >= final_frame):
        return "Start frame has to be less than final frame"
    # Good State: user input but and we need to use them
    else:
        # need to check for player track overlap
        temp_frame = start_frame+sf
        while temp_frame <= final_frame+sf:
            if (int(player_id) in dic[temp_frame].player_id):
                return "This player already has a track assigned to them within this selection of frames."
            temp_frame += 1

        state = 2
        detections_df = detections_df[start_frame:final_frame+1] # need to cut the df for the frame outline
        #api_detections.save_track(0, detections_df, sf+start_frame, -1)
        return "Track saved. Now click quit to return."
# End save_detection


# "Useless" Callbacks ########################################################


# Callback for the updated output
@app.callback(
    Output('output', 'children'),
    Input('graph_box', 'relayoutData'),
    prevent_initial_call=True)
def update_output(graph_relayout): # graph_relayout is a dictionary
    if graph_relayout is None: return '' # stops the error
    
    # print(graph_relayout)
    # print("")

    if (not 'shapes' in graph_relayout) or (len(graph_relayout['shapes']) == 0): # or shapes is empty 
        return 'no shapes'
    else:
        output_string = "List of boxes: "
        output_num = 0
        for box in graph_relayout['shapes']:
            output_num += 1
            output_string += "\nBox #{}: ".format(output_num)
            output_string += "X0: {}, ".format(box['x0'])
            output_string += "Y0: {}, ".format(box['y0'])
            output_string += "X1: {}, ".format(box['x1'])
            output_string += "Y1: {}".format(box['y1'])
            output_string += " ###### "
        #return 'Number of boxes: {0}'.format(output_num)
        return 'Number of boxes: {0} // Updated output: {1}'.format(output_num, output_string) # graph_relayout['shapes']
# end update_output

# Callback for state button
@app.callback(
    Output('state_output', 'children'),
    Input('state_button', 'n_clicks'))
def test_func(n_clicks):
    global state
    if state == 0:
        #state = 1
        return "State is 0"
    else:
        #state = 0
        return "State is 1"
