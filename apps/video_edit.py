import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import pathlib
# import ffmpeg_streaming
# import dash_player
# from moviepy.editor import *
from app import app

import cv2
import numpy as np

# clip = VideoFileClip("Sample Soccer Video.mp4")
# video = ffmpeg_streaming.input('./Sample Soccer Video.mp4')

# layout = html.Video(src="Sample Soccer Video.mp4")

layout = html.Div(children=[

    html.H1('VIDEO'),





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
