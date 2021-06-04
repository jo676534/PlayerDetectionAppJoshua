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

from .pysot.tools import josh_test
from .pysot.tools import demo

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
            [
                html.Button('Submit', id='next_page', n_clicks=0),
                html.Br(),
                html.Div(id='button_output')
            ]
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
    Output('button_output', 'children'),
    Input('next_page', 'n_clicks'),
    State('graph_box', 'relayoutData'),
)
def submit_box(n_clicks, graph_relayout):
    if graph_relayout is None: return '' # stops the error
    
    if (not 'shapes' in graph_relayout):
        return "No bounding box has been drawn yet"
    elif (len(graph_relayout['shapes']) == 0):
        return "You have to draw one bounding box"
    elif (len(graph_relayout['shapes']) == 1): # this is the success case
        print("in submit box 1")
        print("in submit box 2")
        for box in graph_relayout['shapes']:
            x0 = box['x0']
            y0 = box['y0']
            x1 = box['x1']
            y1 = box['y1']
            demo.rt_track(100, 120, x0, y0, x1, y1)
        return josh_test.josh_string() # "You have drawn one bounding box, next page goes here"
    else:
        return "There can only be one bounding box, please ensure there is only one"
# end submit_box


@app.callback(
    Output('output', 'children'),
    Input('graph_box', 'relayoutData')
)
def update_output(graph_relayout): # graph_relayout is a dictionary
    if graph_relayout is None: return '' # stops the error
    
    if (not 'shapes' in graph_relayout) or (len(graph_relayout['shapes']) == 0): # or shapes is empty 
        return 'no shapes'
    else:
        output_string = "List of boxes: "
        output_num = 0
        for box in graph_relayout['shapes']:
            output_num += 1
            output_string += "\nBox #{}: ".format(output_num)
            output_string += "X0: {}, ".format(box['x0'])
            output_string += "Y0: {}, ".format(box['y0'])
            output_string += "X1: {}, ".format(box['x1'])
            output_string += "Y1: {}".format(box['y1'])
            output_string += " ###### "
        
        return 'Number of boxes: {0} "<br />" Updated output: {1}'.format(output_num, output_string) # graph_relayout['shapes']
# end update_output