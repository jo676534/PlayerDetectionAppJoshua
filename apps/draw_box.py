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

from api import api_detections
from api import api_team
from api import api_player

pathIn = './vid2img/'
frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))] 
frames.sort(key=lambda x: int(x[5:-4]))

first_frame = 100
final_frame = 200

########### END OLD VID TO FRAMES###########


# GLOBAL VARIABLES #############################################################################################################################


fig = px.imshow(io.imread(pathIn+frames[first_frame]), binary_backend="jpg")
fig.update_layout(
    margin=dict(l=0, r=0, b=0, t=0, pad=4),
    dragmode="drawrect",
)


bounding_box_image = dbc.Card(
    id="imagebox",
    children=[
        dbc.CardHeader(html.H2("Header")),
        dcc.Graph(
            id="graph_box",
            style={'width':'1000px', 'height':'600px'},
            figure=fig,
            config={"modeBarButtonsToAdd": ["drawrect", "eraseshape"]},
        ),
        dbc.CardFooter(
            html.H3("Footer")
        )
    ]
)


data_table = dbc.Card(
    children=[
        dbc.CardHeader(
            html.H2("Header")
        ),
        dbc.CardBody(
            [
                html.H2("Body"),
                html.Br(),
                html.Div(id='output')
            ]
        ),
        dbc.CardFooter(
            html.H3("Footer")
        ),
    ]
)


layout = html.Div( 
    [
        #navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(bounding_box_image, md=7.5),
                        dbc.Col(data_table, md=5)
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)


@app.callback(
    Output('output', 'children'),
    Input('graph_box', 'relayoutData')
)
def update_output(graph_relayout): # graph_relayout is a dictionary
    if graph_relayout is None: return '' # stops the error
    
    if (not 'shapes' in graph_relayout) or (len(graph_relayout['shapes']) == 0): # or shapes is empty 
        return 'no shapes'
    else:
        return 'Updated output: {}'.format(graph_relayout['shapes'])