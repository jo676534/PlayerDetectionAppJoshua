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
<<<<<<< HEAD
import plotly.express as px
import pandas as pd
import pathlib
# import ffmpeg_streaming
# import dash_player
<<<<<<< HEAD
=======

>>>>>>> d2a5a0c7d46d9b79a835f62bfa4f76ba0c595ccc
# from moviepy.editor import *
from app import app

import cv2
import numpy as np

# clip = VideoFileClip("Sample Soccer Video.mp4")
# video = ffmpeg_streaming.input('./Sample Soccer Video.mp4')

# layout = html.Video(src="Sample Soccer Video.mp4")

layout = html.Div(children=[

    html.H1('VIDEO'),
=======
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
        dbc.CardHeader(
            html.H2('Video Trimmer'),
        ),
        dbc.CardBody(
            [
                # dcc.RangeSlider(
                #     id='frame-trimmer',
                #     min=0,
                #     max=maxFrames,
                #     marks={round(i*maxFrames/16): '{}'.format(round(i*maxFrames/16))
                #            for i in range(maxFrames)},
                #     step=1,
                #     value=[0, round(maxFrames/16)]
                # ),
                # html.Div(id='trimmer-output-containerVE'),
                # dbc.Button('Add to Trim', id='addToTrim')
                dbc.Row(
                    children=[
                        dbc.Col(children=[
                            html.H6('Enter Start of Frames to Trim: '),
                            dcc.Input(id="startingFrame", type="number", debounce=True,
                                      placeholder="Start Frame", min=0,),
                        ]),
                        dbc.Col(children=[
                            html.H6('Enter End of Frames to Trim: '),
                            dcc.Input(id="endingFrame", type="number", debounce=True,
                                      placeholder="End Frame", min=0,),
                        ]),
                    ],
                    style={"margin-bottom": "20px", }
                ),

                html.Div(
                    children=[
                        dbc.ButtonGroup(
                            [
                                dbc.Button('Set Start Frame',
                                           id='setStart',),
                                dbc.Button('Set End Frame',
                                           id='setEnd',),
                                dbc.Button('Jump to Start',
                                           id='jumpStart',),
                                dbc.Button('Jump to End',
                                           id='jumpEnd',),
                            ],
                            style={"width": "100%"},
                        ),

                    ],
                    style={"margin-top": "20px", "margin-bottom": "10px", }
                ),
                dbc.Button('Save to Trim Queue',
                           id='addToTrim', color="primary", block=True),

            ]
        ),
        dbc.CardFooter(
            [
                html.Div(id='trimming-dropdown', children=[],
                         style={"maxHeight": "410px", "overflow": "auto", "height": "410px"})
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
                dbc.Button('Discard Video', id='discard',
                           href='/apps/home', size="lg", color="danger"),
                dbc.Button('Save and Quit',
                           id='save-and-quit', href='/apps/home', size="lg"),
                dbc.Button('Save and Continue',
                           id='save-and-continue', href='/apps/dashboard', size="lg"),
            ],
        ),
    ],
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
    Input('jumpStart', 'n_clicks'),
    Input('jumpEnd', 'n_clicks'),
    State('startingFrame', 'value'),
    State('endingFrame', 'value'),
    State('frame_intervalVE', 'disabled'),
)
def update_figureVE(interval, slider, previousBut, nextBut, startBut, endBut, start, end, isPaused):
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
        if cbcontext == "jumpStart.n_clicks":
            if(start >= 0 and start <= maxFrames):
                currentFrame = start
        if cbcontext == "jumpEnd.n_clicks":
            if(end >= 0 and end <= maxFrames):
                currentFrame = end
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


# @app.callback(
#     Output('trimming-dropdown', 'children'),
#     Input('addToTrim', 'n_clicks'),
#     State('trimming-dropdown', 'children'),
#     State('frame-trimmer', 'value'), prevent_initial_call=True)
# def display_dropdowns(n_clicks, children, value):
#     new_element = html.Div(
#         dbc.Row(
#             id={'type': 'dynamic-trim',
#                 'index': n_clicks
#                 },
#             children=[
#                 html.Div('Trimming frames: {}'.format(value)),
#                 dbc.Button('Remove from Queue', id='delete-trim')]
#         ),
#         # html.Div(
#         #     id={
#         #         'type': 'dynamic-output',
#         #         'index': n_clicks
#         #     }
#         # )
#     )
#     children.append(new_element)
#     # print(len(children))
#     return children
>>>>>>> mark-multiapp


@app.callback(
    Output('trimming-dropdown', 'children'),
    Input('addToTrim', 'n_clicks'),
    State('trimming-dropdown', 'children'),
    State('startingFrame', 'value'),
    State('endingFrame', 'value'),
    prevent_initial_call=True)
def display_dropdowns(n_clicks, children, start, end):
    new_element = html.Div(
        dbc.Row(
            id={'type': 'dynamic-trim',
                'index': n_clicks
                },
            children=[
                html.Div('Trimming frames: {}, {}'.format(start, end)),
                dbc.Button('Remove', id='delete-trim', color='danger')]
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


<<<<<<< HEAD

    # dash_player.DashPlayer(
    #     id='video',
    #     url="https://trinidaddemobucket.s3.amazonaws.com/Sample+Soccer+Video.mp4",
    #     controls=True,
    # ),
    # html.Div(id='div-current-time', children=[]),
    # html.Div(id='div-method-output', children=[]),



    # html.Button('Set seekTo to 10', id='button-seek-to'),
    dcc.Input(id="startingTime", type="number", debounce=True,
              placeholder="Enter Trim Start Time"),
    dcc.Input(id="EndingTime", type="number", debounce=True,
              placeholder="Enter Trim End Time"),
])
# pull video from s3 bucket ffmpeg_streaming
# give queries to where to clip video
# reupload video as copy but keep the original


# @app.callback(Output('div-current-time', 'children'),
#               [Input('video', 'currentTime')])
# def update_time(currentTime):
#     print(currentTime)
#     return 'Current Time: {}'.format(currentTime)


# @app.callback(Output('div-method-output', 'children'),
#               [Input('video', 'secondsLoaded')],
#               [State('video', 'duration')])
# def update_methods(secondsLoaded, duration):
#     return 'Second Loaded: {}, Duration: {}'.format(secondsLoaded, duration)


# @app.callback(Output('video', 'seekTo'),
#               [Input('button-seek-to', 'n_clicks')])
# def set_seekTo(n_clicks):
#     return 10
=======
@app.callback(
    Output('startingFrame', 'max'),
    Output('endingFrame', 'max'),
    [Input('frame-sliderVE', 'max')])
def set_maxVid(duration):
    return duration, duration

@app.callback(
    Output('startingFrame', 'value'),
    Input('setStart', 'n_clicks'),
    State('frame_intervalVE', 'n_intervals'),
    prevent_initial_call=True
)
def setFrameToStart(n_clicks, value):
    return value

@app.callback(
    Output('endingFrame', 'value'),
    Input('setEnd', 'n_clicks'),
    State('frame_intervalVE', 'n_intervals'),
    prevent_initial_call=True
)
def setFrameToEnd(n_clicks, value):
    return value

# @app.callback(
#     Output('frame_intervalVE', 'n_intervals'),
#     Input('jumpStart', 'n_clicks'),
#     State('startingFrame', 'value'),
# )
# def setFrameToEnd(n_clicks, value):
#     return value
>>>>>>> mark-multiapp
