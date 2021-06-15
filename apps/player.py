# INSTALL LIBRARIES ---------------------------------------------------------------------------------------------------------------------------

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

from app import app

vidcap = cv2.VideoCapture('Sample Soccer Video.mp4')
# fps = vidcap.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
# duration = frame_count/fps
# print('fps = ' + str(fps))
# print('number of frames = ' + str(frame_count))
# print('duration (S) = ' + str(duration))
frames = []

def getFrame(frame):
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    hasFrames, image = vidcap.read()
    if hasFrames:
        # Instead of writing to directory, save to an image array
        # cv2.imwrite(os.path.join(dirname,"image"+str(count) + ".jpg"), image)
        image2 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image2



# sec = 0
# frameRate = 0.02  # 30 frames per second?
# count = 1
# success = getFrame(sec)
# while success:
#     count = count + 1
#     sec = sec + frameRate
#     sec = round(sec, 2)
#     success = getFrame(sec)

# pathIn = './vid2img/'
# frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
# frames.sort(key=lambda x: int(x[5:-4]))


########### END OLD VID TO FRAMES###########


# GLOBAL VARIABLES #############################################################################################################################

maxFrames = frame_count-1

fig = px.imshow(getFrame(0), binary_backend="jpg")

# fig = px.imshow(io.imread(pathIn+frames[0]), binary_backend="jpg")
fig.update_layout(
    margin=dict(l=0, r=0, b=0, t=0, pad=4),
)

image_annotation_card_player = dbc.Card(
    id="imagebox_player",
    children=[
        dbc.CardBody(
            [
                dcc.Interval(
                    id='frame_interval_player',
                    interval=500,
                    disabled=True,
                    n_intervals=0,      # number of times the interval has passed
                    max_intervals=maxFrames
                ),
                dcc.Graph(
                    id="graph_player",
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
                    id='frame-slider_player',
                    min=0,
                    max=maxFrames,
                    value=0,
                    step=1,
                    marks={round(i*maxFrames/16): '{}'.format(round(i*maxFrames/16))
                           for i in range(maxFrames)},
                ),
                html.Div(id='slider-output-container_player'),
                # Pause/Player Buttons
                dbc.ButtonGroup(
                    [
                        dbc.Button("Previous", id="previous_player", outline=True, style={
                                   "margin-left": "50px", "margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("Rewind", id="rewind_player", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("Play", id="playpause_player", outline=True,
                                   style={"margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("Fastforward", id="fastforward_player", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("  Next  ", id="next_player", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}),
                    ],
                    style={"width": "100%"}
                ),
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
                        dbc.Col(image_annotation_card_player, md=7.5)
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)


# Call back for video Player/Pause
@app.callback(
    Output('frame_interval_player', 'disabled'),
    Output('playpause_player', 'children'),
    Input('playpause_player', 'n_clicks'),
    State('frame_interval_player', 'disabled'),
)
def togglePlay_player(play, isPaused):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    text = 'Play'

    if cbcontext == "playpause_player.n_clicks":
        if isPaused == True:
            isPaused = False
            text = 'Pause'
        elif isPaused == False:
            isPaused = True
        else:
            raise PreventUpdate
    return (isPaused, text)


# Video Display Callback
@app.callback(
    Output('graph_player', 'figure'),
    Output('frame_interval_player', 'n_intervals'),
    Output('frame-slider_player', 'value'),
    Input('frame_interval_player', 'n_intervals'),
    Input('frame-slider_player', 'value'),
    Input('previous_player', 'n_clicks'),
    Input('next_player', 'n_clicks'),
    State('frame_interval_player', 'disabled'),
)
def update_figure_player(interval, slider, previousBut, nextBut, isPaused):
    # print(value)
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    currentFrame = 0

    if isPaused == False:
        if interval is None:
            interval = 0
        currentFrame = interval
    elif isPaused == True:
        currentFrame = interval
        if cbcontext == "previous_player.n_clicks":
            if(currentFrame != 0):
                currentFrame += -1
        if cbcontext == "next_player.n_clicks":
            if(currentFrame != maxFrames):
                currentFrame += 1
    if cbcontext == "frame-slider_player.value":
        currentFrame = slider

    # fig = px.imshow(io.imread(pathIn+frames[currentFrame]), binary_backend="jpg")  # OLD
    fig = px.imshow(getFrame(currentFrame), binary_backend="jpg") # NEW
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        dragmode="drawrect",
    )
    return (fig, currentFrame, currentFrame)


# Callback for Slider
@app.callback(
    dash.dependencies.Output('slider-output-container_player', 'children'),
    [dash.dependencies.Input('frame_interval_player', 'n_intervals')])
def update_output_player(value):
    return 'Current Frame "{}"'.format(value)
