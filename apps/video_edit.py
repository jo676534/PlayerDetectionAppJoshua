import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib
import ffmpeg_streaming
import dash_player

from moviepy.editor import *
from app import app


import cv2
import numpy as np

cap = cv2.VideoCapture('Sample Soccer Video.mp4')
frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

buf = np.empty((frameCount, frameHeight, frameWidth, 3), np.dtype('uint8'))

fc = 0
ret = True

while (fc < frameCount  and ret):
    ret, buf[fc] = cap.read()
    fc += 1

cap.release()


cv2.waitKey(0)

# clip = VideoFileClip("Sample Soccer Video.mp4")
# video = ffmpeg_streaming.input('./Sample Soccer Video.mp4')

# layout = html.Video(src="Sample Soccer Video.mp4")

layout = html.Div(children=[

    html.H1('VIDEO'),
    # dash_player.DashPlayer(url="https://trinidaddemobucket.s3.amazonaws.com/Sample+Soccer+Video.mp4",
    #                        controls=True,
    #                        ),
    dash_player.DashPlayer(url=buf,
                           controls=True,
                           ),
])
# pull video from s3 bucket ffmpeg_streaming
# give queries to where to clip video
# reupload video as copy but keep the original
