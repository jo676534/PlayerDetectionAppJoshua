# INSTALL LIBRARIES
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import cv2  # from vid2frames

# PROCESS VIDEO INTO FRAMES ARRAY
vidcap = cv2.VideoCapture('Sample Soccer Video.mp4')
frames = []


def getFrame(sec):
    vidcap.set(cv2.CAP_PROP_POS_MSEC, sec*1000)
    hasFrames, image = vidcap.read()
    if hasFrames:
        # Instead of writing to directory, save to an image array
        # cv2.imwrite(os.path.join(dirname,"image"+str(count) + ".jpg"), image)
        image2 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        frames.append(image2)
    return hasFrames


sec = 0
frameRate = 0.05  # 30 frames per second?
count = 1
success = getFrame(sec)
while success:
    count = count + 1
    sec = sec + frameRate
    sec = round(sec, 2)
    success = getFrame(sec)
maxTime = len(frames)-1

# START APP
external_stylesheets = [dbc.themes.BOOTSTRAP,
                        "assets/image_annotation_style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig = px.imshow(frames[0], binary_backend="jpg")

# lAYOUT COMPONENTS
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
                    max=maxTime,
                    value=0,
                    step=1,
                    marks={round(i*maxTime/16): '{}'.format(round(i*maxTime/16))
                           for i in range(maxTime)},
                ),
                dbc.ButtonGroup(
                    [
                        dbc.Button("Previous image", id="previous",
                                   outline=True, size="lg",),
                        dbc.Button("Play", id="play",
                                   outline=True, size="lg",),
                        dbc.Button("Next image", id="next",
                                   outline=True, size="lg",),
                    ],
                    style={"width": "100%"}
                ),
            ]
        ),
    ],
)

app.layout = html.Div(
    [
        dcc.Interval(
            id='frame_interval',
            # disabled=True,     # if True, the counter will no longer update
            # increment the counter n_intervals every interval milliseconds
            # interval=frameRate*10000,
            interval=350,
            n_intervals=0,      # number of times the interval has passed
            # number of times the interval will be fired.
            max_intervals=0
            # if -1, then the interval has no limit (the default)
            # and if 0 then the interval stops running.
            # SHOULD BE THE VID MAX LENGTH
        ),
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
    Output('frame_interval', 'max_intervals'),
    Output('play', 'children'),
    Input('play', 'n_clicks'),
    State('frame_interval', 'max_intervals'),
)
def togglePlay(play, maxInt):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    # print(cbcontext)
    text = 'Play'

    if cbcontext == "play.n_clicks":
        if maxInt == 0:  # STOP
            maxInt = maxTime
            text = 'Stop'
        elif maxInt == maxTime:  # PLAYING
            maxInt = 0
        else:
            raise PreventUpdate

    return (maxInt, text)


@app.callback(
    Output('graph', 'figure'),
    Output('frame_interval', 'n_intervals'),
    Output('frame-slider', 'value'),
    Input('frame_interval', 'n_intervals'),
    Input('frame-slider', 'value'),
    Input('previous', 'n_clicks'),
    Input('next', 'n_clicks'),
    State('frame_interval', 'max_intervals'),
)
def update_figure(interval, slider, previousBut, nextBut, playing):
    # print(value)
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    # print(cbcontext)

    if playing == maxTime:  # is playing
        if interval is None:
            interval = 0
        fig = px.imshow(frames[interval], binary_backend="jpg")
        return (fig, interval, interval)
    elif playing != maxTime:  # is paused
        if cbcontext == "previous.n_clicks":
            if(interval != 0):
                interval += -1
        if cbcontext == "next.n_clicks":
            if(interval != maxTime):
                interval += 1

    if cbcontext == "frame-slider.value":
        fig = px.imshow(frames[slider], binary_backend="jpg")
        return (fig, slider, slider)

    fig = px.imshow(frames[interval], binary_backend="jpg")
    return (fig, interval, interval)


if __name__ == '__main__':
    app.run_server(debug=True)
