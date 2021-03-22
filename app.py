# INSTALL LIBRARIES
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


# START APP
external_stylesheets = [dbc.themes.BOOTSTRAP,
                        "assets/image_annotation_style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
pathIn = './vid2img/'
files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]

# for sorting the file names properly
files.sort(key=lambda x: int(x[5:-4]))

fig = px.imshow(io.imread(pathIn+files[0]), binary_backend="jpg")
fig.update_layout(
    margin=dict(l=0, r=0, b=0, t=0, pad=4),
    dragmode="drawrect",
)

image_annotation_card = dbc.Card(
    id="imagebox",
    children=[
        dbc.CardHeader(html.H2("Video Player")),
        dbc.CardBody(
            [
                dcc.Graph(
                    id="graph",
                    figure=fig,
                    config={"modeBarButtonsToAdd": ["drawrect", "eraseshape"]},
                )
            ]
        ),
        dbc.CardFooter(
            [
                dcc.Slider(
                    id='frame-slider',
                    min=0,
                    max=len(files)-1,
                    value=0,
                    step=1
                )

            ]
        ),
    ],
)

app.layout = html.Div(
    [
        html.H1("Web Application Dashboards with Dash",
                style={'text-align': 'center'}),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(image_annotation_card, md=7),
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)


@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('frame-slider', 'value')])
def update_output(value):
    print(value)
    fig = px.imshow(io.imread(pathIn+files[value]), binary_backend="jpg")
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        dragmode="drawrect",
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
