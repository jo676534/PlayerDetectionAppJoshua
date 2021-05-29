import dash_core_components as dcc
import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import pathlib
# import ffmpeg_streaming
import dash_player
# from moviepy.editor import *
from app import app

import cv2
import numpy as np

# clip = VideoFileClip("Sample Soccer Video.mp4")
# video = ffmpeg_streaming.input('./Sample Soccer Video.mp4')

# layout = html.Video(src="Sample Soccer Video.mp4")

layout = html.Div(children=[

    dash_player.DashPlayer(
        id='video',
        url="https://trinidaddemobucket.s3.amazonaws.com/Sample+Soccer+Video.mp4",
        controls=True,
    ),
    # html.Button('Set seekTo to 10', id='button-seek-to'),
    html.Div(id='div-current-time', children=[]),
    # html.Div(id='div-method-output', children=[]),
    dcc.Input(id="fine", type="number",
                placeholder="FindTime", min=0),


    # html.Button('Set seekTo to 10', id='button-seek-to'),
    html.Div(children=[
        dcc.Input(id="startingTime", type="number", debounce=True,
                  placeholder="Enter Trim Start Time", min=0),
        dcc.Input(id="endingTime", type="number", debounce=True,
                  placeholder="Enter Trim End Time", min=0),
        html.Button('Add to Start', id='startButton'),
        html.Button('Add to End', id='endButton'),
        html.Button('Save to Trim Queue', id='addToTrim'),
    ]),
    html.Div(id='dynamic-dropdown', children=[]),

    html.Button('Discard', id='discardButton'),
    html.Button('Save and Continue', id='saveButton'),

])
# pull video from s3 bucket ffmpeg_streaming
# give queries to where to clip video
# reupload video as copy but keep the original


@app.callback(
    Output('startingTime', 'max'),
    Output('endingTime', 'max'),
    Output('fine', 'max'),
    [Input('video', 'duration')])
def set_maxVid(duration):
    return duration, duration, duration


@app.callback(Output('div-current-time', 'children'),
              [Input('video', 'currentTime')])
def update_time(currentTime):
    # print(currentTime)
    return 'Current Time: {}'.format(currentTime)


# @app.callback(Output('div-method-output', 'children'),
#               [Input('video', 'secondsLoaded')],
#               [State('video', 'duration')])
# def update_methods(secondsLoaded, duration):
#     return 'Second Loaded: {}, Duration: {}'.format(secondsLoaded, duration)


@app.callback(Output('video', 'seekTo'),
              [Input('fine', 'value')])
def set_seekTo(value):
    return value


@app.callback(Output('startingTime', 'value'),
              Input('startButton', 'n_clicks'),
              State('video', 'currentTime'),)
def set_startTime(n_clicks, currentTime):
    return currentTime



@app.callback(Output('endingTime', 'value'),
              Input('endButton', 'n_clicks'),
              State('video', 'currentTime'),)
def set_endTime(n_clicks, currentTime):
    return currentTime

@app.callback(
    Output('dynamic-dropdown', 'children'),
    Input('addToTrim', 'n_clicks'),
    State('dynamic-dropdown', 'children'),
    State('startingTime', 'value'),
    State('endingTime', 'value'), prevent_initial_call=True)
def display_dropdowns(n_clicks, children, start, end):
    new_element = html.Div([
        html.Div('Start Time: {}     End Time: {}'.format(start, end))
        # html.Div(
        #     id={
        #         'type': 'dynamic-output',
        #         'index': n_clicks
        #     }
        # )
    ])
    children.append(new_element)
    # print(len(children))
    return children