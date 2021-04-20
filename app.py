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
from dash.exceptions import PreventUpdate
import cv2  # from vid2frames


# FUNCTION DEFINITIONS ------------------------------------------------------------------------------------------------------------------------


dic = {}


def add_editable_box(
    fig, x0, y0, x1, y1, name=None, color=None, opacity=1, group=None, text=None
):
    fig.add_shape(
        editable=True,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        line_color=color,
        opacity=opacity,
        line_width=3,
        name=name,
    )


def read_input():
    for i in range(1000):
        fp = open("./detections/f" + str(i) + ".txt", "r")  # grab new file
        df = read_file(fp)
        dic[i] = df


def read_file(fp):  # returns complete dataframe
    df = pd.DataFrame([], columns=['id', 'x0', 'y0', 'x1', 'y1'])
    fp.read(16)  # get rid of dummy inputs
    for line in fp:  # loop for the rest of the inputs
        start, end = line.split("[")
        nums, garbage = end.split("]")
        garbage2, id_num = garbage.split(":")

        x, y, w, h = nums.split()
        x0 = float(x)
        y0 = float(y)
        x1 = x0 + float(w)
        y1 = y0 + float(h)

        df_temp = pd.DataFrame([[int(id_num), x0, y0, x1, y1]], columns=[
                               'id', 'x0', 'y0', 'x1', 'y1'])
        df = df.append(df_temp)
    return df


# Start of Mark components
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
frameRate = 0.02  # 30 frames per second?
count = 1
success = getFrame(sec)
while success:
    count = count + 1
    sec = sec + frameRate
    sec = round(sec, 2)
    success = getFrame(sec)
maxFrames = len(frames)-1
# End of Mark components

# START APP / DASH COMPONENTS -----------------------------------------------------------------------------------------------------------------


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

fig = px.imshow(frames[0], binary_backend="jpg")


colors = {'background': '#111111', 'text': '#7fdbff'}

# slider = html.Div([
#     dcc.RangeSlider(
#         id='my-range-slider',
#         min=0,
#         max=1000,
#         step=1,
#         value=[50, 120]
#     ),
#     html.Div(id='output-container-range-slider')
# ])

navbar = dbc.NavbarSimple(
    children=[
        # dbc.NavItem(dbc.NavLink("Hide/Unhide all track overlays", style = {"font-size": "12px"}, href="#")),
        # dbc.NavItem(dbc.NavLink("Hide/Unhide track overlay in scene", style = {"font-size": "12px"}, href="#")),
        # dbc.NavItem(dbc.NavLink("Toggle Assigned Tracks View", style = {"font-size": "12px"}, href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Home josh", header=True),
                dbc.DropdownMenuItem("Video Trimming", href="#"),
                dbc.DropdownMenuItem("Next Phase", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="HOME",
        ),
    ],
    brand="General NavBar",
    brand_href="#",
    color="#6A6A6A",
    dark=True,
    brand_style={"margin-left": "-160px"},
)

image_annotation_card = dbc.Card(
    id="imagebox",
    children=[
        dbc.CardHeader(html.Div(
            [
                dbc.Button("Hide/Unhide all track overlays", id="but1", outline=True, style={
                           "margin-left": "50px", "margin-right": "15px", "font-size": "12px"}),
                dbc.Button("Hide/Unhide track overlay in scene", id="but2",
                           outline=True, style={"margin-right": "15px", "font-size": "12px"}),
                dbc.Button("Toggle Assigned Tracks View", id="but3", outline=True, style={
                    "margin-right": "15px", "font-size": "12px"}),
            ]
        )),
        dbc.CardBody(
            [
                dcc.Interval(
                    id='frame_interval',
                    interval=350,
                    disabled=True,
                    n_intervals=0,      # number of times the interval has passed
                    max_intervals=maxFrames
                ),
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
                    max=maxFrames,
                    value=0,
                    step=1,
                    marks={round(i*maxFrames/16): '{}'.format(round(i*maxFrames/16))
                           for i in range(maxFrames)},
                ),
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

annotated_data_card = dbc.Card(
    [
        dbc.CardHeader(html.Div(
            [
                dbc.Button("All Tracks", id="but4", outline=True, style={
                       "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("ViewableTracks", id="but5", outline=True, style={
                    "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("Player Tracks", id="but6", outline=True,
                           style={"font-size": "12px"}),
            ])),
        dbc.CardBody(
            [
                html.Div(
                    [
                        dbc.Row(
                            dbc.Col([
                                dbc.Button(
                                    "ID #: 3456",
                                    id="collapse-button1",
                                    className="mb-3",
                                    color="secondary",
                                    style={"font-size": "12px"}
                                ),
                                dbc.Collapse(
                                    dbc.Card(dbc.CardBody([
                                        dcc.Markdown("Start Time:"),
                                        dcc.Markdown("End Time:"),
                                        dcc.Markdown(
                                            "Modify Track:   " "**Go to Start**"),
                                        dcc.Markdown(
                                            "Delete Track:   " "**Go to End**")
                                    ])),
                                    id="collapse1",
                                    style={"font-size": "12px"}
                                ),
                            ])),
                        dbc.Row(
                            dbc.Col([
                                dbc.Button(
                                    "ID #: 1290",
                                    id="collapse-button2",
                                    className="mb-3",
                                    color="secondary",
                                    style={"font-size": "12px"}
                                ),
                                dbc.Collapse(
                                    dbc.Card(dbc.CardBody([
                                        dcc.Markdown("Start Time:"),
                                        dcc.Markdown("End Time:"),
                                        dcc.Markdown(
                                            "Modify Track:   " "**Go to Start**"),
                                        dcc.Markdown(
                                            "Delete Track:   " "**Go to End**")
                                    ])),
                                    id="collapse2",
                                    style={"font-size": "12px"}
                                ),
                            ]))
                    ])
            ]
        ),
        dbc.CardFooter(
            [
                html.Div()
            ]
        ),
    ],
    style={"margin-top": "20px", "margin-bottom": "20px", "margin-right": "10px"}
)

annotated_data_card2 = dbc.Card(
    [
        dbc.CardHeader(html.Div(
            [
                dbc.Button("Team A", id="but7", outline=True, style={
                       "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("Team B", id="but8", outline=True,
                           style={"font-size": "12px"}),
            ])),
        dbc.CardBody(
            [
                html.Div(
                    [
                        dbc.Row(
                            dbc.Col([
                                dbc.Button(
                                    "Player Name: Josh",
                                    id="collapse-button3",
                                    className="mb-3",
                                    color="secondary",
                                    style={"font-size": "12px"}
                                ),
                                dbc.Collapse(
                                    dbc.Card(dbc.CardBody([
                                        dcc.Markdown("Jersey Number:"),
                                        dcc.Markdown(
                                            "**Add Selected Track:**"),
                                        dcc.Markdown("Number of Tracks: "),
                                        dcc.Markdown("**Create New Track**"),
                                        dcc.Markdown("**View Player Tracks**")
                                    ])),
                                    id="collapse3",
                                    style={"font-size": "12px"}
                                ),
                            ])),
                        dbc.Row(
                            dbc.Col([
                                dbc.Button(
                                    "Player Name: Mark",
                                    id="collapse-button4",
                                    className="mb-3",
                                    color="secondary",
                                    style={"font-size": "12px"}
                                ),
                                dbc.Collapse(
                                    dbc.Card(dbc.CardBody([
                                        dcc.Markdown("Jersey Number:"),
                                        dcc.Markdown(
                                            "**Add Selected Track:**"),
                                        dcc.Markdown("Number of Tracks: "),
                                        dcc.Markdown("**Create New Track**"),
                                        dcc.Markdown("**View Player Tracks**")
                                    ])),
                                    id="collapse4",
                                    style={"font-size": "12px"}
                                ),
                            ]))
                    ])
            ]
        ),
        dbc.CardFooter(
            [
                html.Div()
            ]
        ),
    ],
    style={"margin-top": "20px", "margin-bottom": "20px"}
)
app.layout = app.layout = html.Div(
    [
        navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(image_annotation_card, md=6),
                        dbc.Col(annotated_data_card, md=2.5),
                        dbc.Col(annotated_data_card2, md=2.5),
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)


# CALLBACK FUNCTION DEFINITIONS -----------------------------------------------------------------------------------------------------------------

@app.callback(
    Output('frame_interval', 'disabled'),
    Output('playpause', 'children'),
    Input('playpause', 'n_clicks'),
    State('frame_interval', 'disabled'),
)
def togglePlay(play, isPaused):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    # print(cbcontext)
    text = 'Play'

    if cbcontext == "playpause.n_clicks":
        if isPaused == True:
            isPaused = False
            text = 'Pause'
        elif isPaused == False:
            isPaused = True
        else:
            raise PreventUpdate

    return (isPaused, text)


# @app.callback(
#     dash.dependencies.Output('output-container-range-slider', 'children'),
#     [dash.dependencies.Input('my-range-slider', 'value')])
# def update_output(value):
#     return 'You have selected frames {}'.format(value)


@app.callback(
    Output("collapse1", "is_open"),
    [Input("collapse-button1", "n_clicks")],
    [State("collapse1", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse2", "is_open"),
    [Input("collapse-button2", "n_clicks")],
    [State("collapse2", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse3", "is_open"),
    [Input("collapse-button3", "n_clicks")],
    [State("collapse3", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse4", "is_open"),
    [Input("collapse-button4", "n_clicks")],
    [State("collapse4", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('graph', 'figure'),
    Output('frame_interval', 'n_intervals'),
    Output('frame-slider', 'value'),
    Input('frame_interval', 'n_intervals'),
    Input('frame-slider', 'value'),
    Input('previous', 'n_clicks'),
    Input('next', 'n_clicks'),
    State('frame_interval', 'disabled'),
)
def update_figure(interval, slider, previousBut, nextBut, isPaused):
    # print(value)
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    currentFrame = 0;

    if isPaused == False:
        if interval is None:
            interval = 0
        currentFrame = interval
    elif isPaused == True:
        currentFrame = interval
        if cbcontext == "previous.n_clicks":
            if(currentFrame != 0):
                currentFrame += -1
        if cbcontext == "next.n_clicks":
            if(currentFrame != maxFrames):
                currentFrame += 1
    if cbcontext == "frame-slider.value":
        currentFrame = slider

    fig = px.imshow(frames[currentFrame], binary_backend="jpg")
    frame_df = dic[currentFrame]
    print("\nCurrent Frame Bounding Boxes:")
    for i in range(len(frame_df)):
        x0 = frame_df.iloc[i]['x0']
        y0 = frame_df.iloc[i]['y0']
        x1 = frame_df.iloc[i]['x1']
        y1 = frame_df.iloc[i]['y1']
        print(x0, y0, x1, y1)
        add_editable_box(fig, x0, y0, x1, y1)
    return (fig, currentFrame, currentFrame)
    
# MAIN STARTS HERE -----------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    read_input()
    print("---Input done---")
    app.run_server(debug=True)


'''    dcc.Graph(id='example',
            figure={'data':[
            {'x':[1,2,3], 'y':[4,1,2],'type':'bar','name':'SF'},
            {'x':[1,2,3], 'y':[2,4,5],'type':'bar','name':'NYC'}
            ],
                    'layout':{
                    'title':'BAR PLOTS!'
                    }})'''
