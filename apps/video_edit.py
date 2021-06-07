# # INSTALL LIBRARIES ---------------------------------------------------------------------------------------------------------------------------
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

# # GET FRAMES FROM VIDEO OR STORAGE ############################################################################################################

# ########### NEW VID TO FRAMES###########

# # vidcap = cv2.VideoCapture('Sample Soccer Video.mp4')
# # frames = []

# # def getFrame(sec):
# #     vidcap.set(cv2.CAP_PROP_POS_MSEC, sec*1000)
# #     hasFrames, image = vidcap.read()
# #     if hasFrames:
# #         # Instead of writing to directory, save to an image array
# #         # cv2.imwrite(os.path.join(dirname,"image"+str(count) + ".jpg"), image)
# #         image2 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# #         frames.append(image2)
# #     return hasFrames

# # sec = 0
# # frameRate = 0.02  # 30 frames per second?
# # count = 1
# # success = getFrame(sec)
# # while success:
# #     count = count + 1
# #     sec = sec + frameRate
# #     sec = round(sec, 2)
# #     success = getFrame(sec)

# ########### END NEW VID TO FRAMES###########
# ########### OLD VID TO FRAMES###########

pathIn = './vid2img/'
framesVE = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
framesVE.sort(key=lambda x: int(x[5:-4]))

########### END OLD VID TO FRAMES###########
# GLOBAL VARIABLES #############################################################################################################################
framesBL = True * len(framesVE)
maxFrames = len(framesVE)-1
# # DASH COMPONENTS #######################################################################################################################################

fig = px.imshow(io.imread(pathIn+framesVE[0]), binary_backend="jpg")  # OLD
# # fig = px.imshow(frames[0], binary_backend="jpg")  NEW

# Video Player Card ===============================================================================================================================
image_annotation_cardVE = dbc.Card(
    id="imageboxVE",
    children=[
        dbc.CardBody(
            [
                dcc.Interval(
                    id='frame_intervalVE',
                    interval=500,
                    disabled=True,
                    n_intervals=0,      # number of times the interval has passed
                    max_intervals=maxFrames
                ),
                dcc.Graph(
                    id="graphVE",
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
                    id='frame-sliderVE',
                    min=0,
                    max=maxFrames,
                    value=0,
                    step=1,
                    marks={round(i*maxFrames/16): '{}'.format(round(i*maxFrames/16))
                           for i in range(maxFrames)},
                ),
                html.Div(id='slider-output-containerVE'),

                # Pause/Player Buttons
                dbc.ButtonGroup(
                    [
                        dbc.Button("Previous", id="previousVE", outline=True, style={
                                   "margin-left": "50px", "margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("Rewind", id="rewindVE", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("Play", id="playpauseVE", outline=True,
                                   style={"margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("Fastforward", id="fastforwardVE", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}),
                        dbc.Button("  Next  ", id="nextVE", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}),
                    ],
                    style={"width": "100%"}
                ),
            ]
        ),
    ],
    style={"margin-top": "20px", "margin-bottom": "20px"}
)


video_trimmer_card = dbc.Card(
    id="trimmer_card",
    children=[
        dbc.CardBody(
            [
                html.H2('Video Trimmer'),
                dcc.RangeSlider(
                    id='frame-trimmer',
                    min=0,
                    max=maxFrames,
                    marks={round(i*maxFrames/16): '{}'.format(round(i*maxFrames/16))
                           for i in range(maxFrames)},
                    step=1,
                    value=[0, round(maxFrames/16)]
                ),
                html.Div(id='trimmer-output-containerVE'),
                dbc.Button('Add to Trim', id='addToTrim')

            ]
        ),
        dbc.CardFooter(
            [
                html.Div(id='trimming-dropdown', children=[],
                         style={"maxHeight": "425px", "overflow": "auto"})
            ]
        ),
    ],
    style={"margin-top": "20px", "margin-bottom": "20px"}
)

state_one_card = dbc.Card(
    id="state_one_card",
    children=[
        dbc.ButtonGroup(
            [
                dcc.Link(dbc.Button('Discard Video', id='discard'), href='/apps/home'),
                dcc.Link(dbc.Button('Save and Quit', id='save-and-quit'), href='/home'),
                dcc.Link(dbc.Button('Save and Continue', id='save-and-continue'), href='/apps/dashboard'),
            ]
        ),
    ],
    style={"margin-top": "20px", "margin-bottom": "20px"}
)

# # App Layout ====================================================================================================================================
layout = html.Div(  # was app.layout
    [
        # navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(image_annotation_cardVE, md=7.5),
                        dbc.Col(children=[video_trimmer_card,
                                          state_one_card, ], md=5),
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)

# # layout = html.Div([
# #     "Dashboard"
# # ])VE


# Call back for video Player/Pause
@app.callback(
    Output('frame_intervalVE', 'disabled'),
    Output('playpauseVE', 'children'),
    Input('playpauseVE', 'n_clicks'),
    State('frame_intervalVE', 'disabled'),
)
def togglePlayVE(play, isPaused):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    text = 'Play'

    if cbcontext == "playpauseVE.n_clicks":
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
    Output('graphVE', 'figure'),
    Output('frame_intervalVE', 'n_intervals'),
    Output('frame-sliderVE', 'value'),
    Input('frame_intervalVE', 'n_intervals'),
    Input('frame-sliderVE', 'value'),
    Input('previousVE', 'n_clicks'),
    Input('nextVE', 'n_clicks'),
    State('frame_intervalVE', 'disabled'),
)
def update_figureVE(interval, slider, previousBut, nextBut, isPaused):
    # print(value)
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    currentFrame = 0

    if isPaused == False:
        if interval is None:
            interval = 0
        currentFrame = interval
    elif isPaused == True:
        currentFrame = interval
        if cbcontext == "previousVE.n_clicks":
            if(currentFrame != 0):
                currentFrame += -1
        if cbcontext == "nextVE.n_clicks":
            if(currentFrame != maxFrames):
                currentFrame += 1
    if cbcontext == "frame-sliderVE.value":
        currentFrame = slider

    fig = px.imshow(
        io.imread(pathIn+framesVE[currentFrame]), binary_backend="jpg")  # OLD
    # fig = px.imshow(frames[currentFrame], binary_backend="jpg") # NEW
    # print("\nCurrent Frame Bounding Boxes:")
    return (fig, currentFrame, currentFrame)

# # Callback for Slider


@app.callback(
    dash.dependencies.Output('slider-output-containerVE', 'children'),
    [dash.dependencies.Input('frame_intervalVE', 'n_intervals')])
def update_outputVE(value):
    return 'Current Frame "{}"'.format(value)


@app.callback(
    dash.dependencies.Output('trimmer-output-containerVE', 'children'),
    [dash.dependencies.Input('frame-trimmer', 'value')])
def update_trimmer(value):
    return 'Selected "{}"'.format(value)


@app.callback(
    Output('trimming-dropdown', 'children'),
    Input('addToTrim', 'n_clicks'),
    State('trimming-dropdown', 'children'),
    State('frame-trimmer', 'value'), prevent_initial_call=True)
def display_dropdowns(n_clicks, children, value):
    new_element = html.Div(
        dbc.Row(
            id={'type': 'dynamic-trim',
                'index': n_clicks
                },
            children=[
                html.Div('Trimming frames: {}'.format(value)),
                dbc.Button('Remove from Queue', id='delete-trim')]
        ),
        # html.Div(
        #     id={
        #         'type': 'dynamic-output',
        #         'index': n_clicks
        #     }
        # )
    )
    children.append(new_element)
    # print(len(children))
    return children

    #testing
