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


pathIn = './vid2img/'
frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))] 
frames.sort(key=lambda x: int(x[5:-4]))

########### END OLD VID TO FRAMES###########


# GLOBAL VARIABLES #############################################################################################################################

maxFrames = len(frames)-1
player_tracks_counter = 0
all_tracks_counter = 0
viewable_tracks_counter = 0
dic = {}
current_frame = 0
player_tracks = ["17", "12"] # Hardcoded until "assign track" is working

fig = px.imshow(io.imread(pathIn+frames[0]), binary_backend="jpg")


image_annotation_card = dbc.Card(
    id="imagebox_add",
    children=[
        dbc.CardBody(
            [
                dcc.Interval(
                    id='frame_interval',
                    interval=500,
                    disabled=True,
                    n_intervals=0,      # number of times the interval has passed
                    max_intervals=maxFrames
                ),
                dcc.Graph(
                    id="graph",
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
                    id='frame-slider',
                    min=0,
                    max=maxFrames,
                    value=0,
                    step=1,
                    marks={round(i*maxFrames/16): '{}'.format(round(i*maxFrames/16))
                           for i in range(maxFrames)},
                ),
                html.Div(id='slider-output-container_add'),
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
    style={"margin-top": "20px", "margin-bottom": "20px"}
)


layout = html.Div( # was app.layout
    [
        #navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(image_annotation_card, md=7.5)
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)

