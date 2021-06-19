# # INSTALL LIBRARIES ---------------------------------------------------------------------------------------------------------------------------
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pathlib
import cv2
import os
from os.path import isfile, join
from skimage import io
import numpy as np
import psycopg2 as pg2
import pandas as pd

# FILE FUNCTION IMPORTS ----------------------------------------------------------------------------------------------------------------------
from app import app

# # GET FRAMES FROM VIDEO OR STORAGE ############################################################################################################

# ########### NEW VID TO FRAMES###########

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

# ########### END NEW VID TO FRAMES#######
# ########### OLD VID TO FRAMES###########

pathIn = './vid2img/'
framesVE = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
framesVE.sort(key=lambda x: int(x[5:-4]))

########### END OLD VID TO FRAMES###########


def processFramesToVid(blacklist):

    frame_array = []

    for i in range(len(framesVE)):
        if(blacklist[i]):
            filename = pathIn + framesVE[i]

            # reading each files
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width, height)

            # inserting the frames into an image array
            frame_array.append(img)

    pathOut = 'NEW.avi'
    # fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')

    out = cv2.VideoWriter(pathOut, fourcc, 50, size)
    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()


# GLOBAL VARIABLES #############################################################################################################################
maxFrames = len(framesVE)-1
# DASH COMPONENTS #######################################################################################################################################

fig = px.imshow(io.imread(pathIn+framesVE[0]), binary_backend="jpg")  # OLD
# fig = px.imshow(frames[0], binary_backend="jpg")  NEW

fig.update_layout(
    margin=dict(l=0, r=0, b=0, t=0, pad=4),
    dragmode="drawrect",
)

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
        dcc.Store(id='blacklist',
        storage_type='memory'),
        dbc.CardHeader(
            html.H2('Video Trimmer', id='testing',),
        ),
        dbc.CardBody(
            [
                html.Div(id='trimming-container', children=[],
                         style={"maxHeight": "375px", "overflow": "auto", "height": "375px"})
            ]
        ),
        dbc.CardFooter(
            [
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
    ],
    style={"margin-top": "20px", "margin-bottom": "20px"}
)

state_one_card = html.Div(
    id="state_one_card",
    children=[
        dbc.ButtonGroup(
            [
                dbc.Button('Discard Video', id='discard',
                           href='/apps/home', size="lg", color="danger"),
                dbc.Button('Save and Quit',
                           id='save-and-quit', href='/apps/home', size="lg"),
                # dbc.Button('Save and Continue',
                #            id='save-and-continue', href='/apps/dashboard', size="lg"),
                dbc.Button('Save and Continue',
                            id='save-and-continue', size="lg"),
            ],
            style={"width": "100%"},
        ),
        # dbc.Modal(
        #     [
        #         dbc.ModalHeader("Header"),
        #         dbc.ModalBody("This is the content of the modal"),
        #         dbc.ModalFooter(
        #             children=[dbc.Button("Close", id="close", className="ml-auto"),
        #                       dbc.Button("Close", id="close",
        #                                  className="ml-auto")
        #                       ]
        #         ),
        #     ]
        # )
    ],
)

# # App Layout ====================================================================================================================================
layout = html.Div(
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
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        dragmode="drawrect",
    )
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

@app.callback(
    Output('trimming-container', 'children'),
    Input('addToTrim', 'n_clicks'),
    State('trimming-container', 'children'),
    State('startingFrame', 'value'),
    State('endingFrame', 'value'),
    prevent_initial_call=True)
def display_dropdown(n_clicks, children, start, end):
    new_trim = html.Div(
        dbc.Row(
            id='trimEntry',
            children=[
                html.Div('Trimming frames: {}, {}'.format(start, end)),
                dcc.Store(
                    id={
                        'type': 'trim-start',
                        'index': n_clicks
                    },
                    storage_type='memory', # change to session when in prod?
                    data=start
                ),
                dcc.Store(
                    id={
                        'type': 'trim-end',
                        'index': n_clicks
                    },
                    storage_type='memory', # change to session when in prod?
                    data=end
                ),
                dbc.Button('Remove',                    
                    id={
                        'type': 'remove-trim',
                        'index': n_clicks
                    }, 
                    color='danger')]
        ),
        # html.Div(
        #     id={
        #         'type': 'dynamic-output',
        #         'index': n_clicks
        #     }
        # )
    )
    children.append(new_trim)
    # print(len(children))
    return children

# @app.callback(
#     # Output('') store?
#     #Input save and continue
#     #Input save and quit
#     State('trimming-dropdown', 'children'),
# )
# def processFrames(trimmings):
@app.callback(
    Output('blacklist', 'data'),
    Input('save-and-continue', 'n_clicks'),
    State({'type': 'trim-start', 'index': ALL}, 'data'),
    State({'type': 'trim-end', 'index': ALL}, 'data'),
)
def blacklistFrames(n_clicks, start, end):
    if n_clicks is None:
        raise PreventUpdate
    else:
        blacklist = np.ones(len(framesVE), dtype=bool) # initialize array of True size of vid
        for (i, data) in enumerate(start):
            for j in range(start[i], end[i]+1, 1):
                if(blacklist[j]):
                    blacklist[j] = False
        return blacklist

@app.callback(
    Output('testing', 'children'),
    Input('blacklist', 'data'),
)
def processVideo(blacklist):
    processFramesToVid(blacklist)
    print(blacklist)
    return 'Donezo'

@app.callback(
    Output('startingFrame', 'max'),
    Output('endingFrame', 'max'),
    [Input('frame-sliderVE', 'max')])
def set_maxVid(duration):
    return duration, duration

@app.callback(
    Output('startingFrame', 'value'),
    Input('setStart', 'n_clicks'),
    Input('addToTrim', 'n_clicks'),
    State('frame_intervalVE', 'n_intervals'),
    prevent_initial_call=True
)
def setFrameToStart(set, add, value):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if cbcontext == "setStart.n_clicks":
        return value
    if cbcontext == "addToTrim.n_clicks":
        return None


@app.callback(
    Output('endingFrame', 'value'),
    Input('setEnd', 'n_clicks'),
    Input('addToTrim', 'n_clicks'),
    State('frame_intervalVE', 'n_intervals'),
    prevent_initial_call=True
)
def setFrameToEnd(set, add, value):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if cbcontext == "setEnd.n_clicks":
        return value
    if cbcontext == "addToTrim.n_clicks":
        return None

# @app.callback(
#     Output('frame_intervalVE', 'n_intervals'),
#     Input('jumpStart', 'n_clicks'),
#     State('startingFrame', 'value'),
# )
# def setFrameToEnd(n_clicks, value):
#     return value
