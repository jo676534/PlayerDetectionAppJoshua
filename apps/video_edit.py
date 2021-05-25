import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pathlib

from moviepy.editor import *
from app import app


clip = VideoFileClip("Sample Soccer Video.mp4")


# pull video from s3 bucket ffmpeg_streaming
# give queries to where to clip video
# reupload video 
