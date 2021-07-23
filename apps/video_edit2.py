# # INSTALL LIBRARIES ---------------------------------------------------------------------------------------------------------------------------
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pathlib
import cv2
import os
from os.path import isfile, join
from skimage import io
import numpy as np
import psycopg2 as pg2
import pandas as pd
import json
import math

from app import app

filename = "./Videos/game_0.mp4"
vidcap = cv2.VideoCapture(filename)

# OpenCV2 version 2 used "CV_CAP_PROP_FPS"
fps = vidcap.get(cv2.CAP_PROP_FPS)
frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
vidcap.release() 

duration = frame_count/fps
resolution = (1280, 720)
framesPerSection = 5000
sections = math.ceil(frame_count / framesPerSection)
maxFrames = frame_count-1


def processFramesToVid(blacklist):

    frame_array = []

    for i in range(len(maxFrames)):
        if(blacklist[i]):
            filename = pathIn + framesVE[i]

            # reading each files
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width, height)

            # inserting the frames into an image array
            frame_array.append(img)

    pathOut = 'NEW.avi'
    # fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')

    out = cv2.VideoWriter(pathOut, fourcc, fps, size)
    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()



def getSections(sections):
    sectionOptions = [
        {'label': 'Section {}'.format(i+1), 'value': i}
        for i in range(sections)
    ]
    return sectionOptions

info_storage_VE = html.Div([
    dcc.Store(id='section_VE', storage_type='local', data=0),
    dcc.Store(id='frame_VE', storage_type='local', data=1), 
    dcc.Store(id='video_state_VE', storage_type='session', data=False),
])

video_card_VE = dbc.Card(
    id="imagebox",
    children=[
        dbc.CardHeader(
            html.Div(
            [   dbc.Row( 
                   children = [ 
                        html.Div(
                        [
                            dcc.Dropdown(
                                id = 'dropdown_VE',
                                options=getSections(sections),
                                searchable=False,
                                clearable=False,
                            ),
                            html.Div(id="dd-output-container"),
                        ],
                        style={"width": "20%", 'margin-left':'200px', 'font-size': '14px'},  
                )])    
            ],style = {"margin-bottom":"-15px"}
        ),
        className= "player_card_header",
        ),
        dbc.CardBody(
            [
                html.Div(children=[ # needs to be properly initialized //////////////////////////////////////////////////////////////////////
                    dcc.Interval(
                        id='interval_VE',
                        disabled=False,
                        n_intervals=0,      # number of times the interval has passed
                        max_intervals=maxFrames # alternative way to do this = properly output the maxFrames to
                    ),
                ]),
                dcc.Graph( # WILL HAVE TO INITIALIZE THIS AS WELL //////////////////////////////////////////////////////////////////////////////////////////
                    id="canvas_VE",
                    style={'width': '1000px', 'height': '600px'},
                    config={"modeBarButtonsToAdd": ["drawrect", "eraseshape"]},
                )
            ]
        ),
        dbc.CardFooter(
            [
                # Slider Component
                dcc.Slider( # need to have a default slider w/pointless values and then have it replaced later during initialization ///////////////////////
                    id='slider_VE',
                    step=1,

                ),
                html.Div(id='frame_display_VE', className='current_frame'),
                # Pause/Player Buttons
                dbc.ButtonGroup(
                    [
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/PreviousSection.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="previousSec", outline=True, style={
                                   "margin-left": "50px", "margin-right": "15px", "margin-bottom": "15px"},color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/rw50.png?raw=true',
                                                 style={'height':'30px'})],  
                                    id="rewind-50_VE", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/rw10.png?raw=true',
                                                 style={'height':'30px'})],  
                                    id="rewind-10_VE", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/Prev.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="previous_VE", outline=True, style={
                                    "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/Play.png?raw=true',
                                                 style={'height':'30px'})],
                                   id="playpause_VE", outline=True,
                                   style={"margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/Next.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="next_VE", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/ff10.png?raw=true',
                                                 style={'height':'30px'})], 
                                    id="fastforward-10_VE", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/ff50.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="fastforward-50_VE", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/NextSection.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="nextSec", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                    ],
                    style={"width": "100%", 'margin-left':'-10px'}
                ),
            ]
        ),
    ],
    style={"margin-left": "5px","margin-top": "20px", "margin-bottom": "20px", "margin-right": "10px"}
)


video_trimmer_card = dbc.Card(
    id="trimmer_card",
    children=[
        dcc.Store(id='blacklist',
                  storage_type='memory'),
        dbc.CardHeader(
            html.H2('Video Trimmer', id='testing',),
        ),
        dbc.CardBody(
            [
                html.Div(id='trimming-container', children=[],
                         style={"maxHeight": "375px", "overflow": "auto", "height": "375px"})
            ]
        ),
        dbc.CardFooter(
            [
                dbc.Row(
                    children=[
                        dbc.Col(children=[
                                html.H6('Enter Start of Frames to Trim: '),
                                dcc.Input(id="startingFrame", type="number", debounce=True,
                                          placeholder="Start Frame", min=0,),
                                ]),
                        dbc.Col(children=[
                                html.H6('Enter End of Frames to Trim: '),
                                dcc.Input(id="endingFrame", type="number", debounce=True,
                                          placeholder="End Frame", min=0,),
                                ]),
                    ],
                    style={"margin-bottom": "20px", }
                ),

                html.Div(
                    children=[
                        dbc.ButtonGroup(
                            [
                                dbc.Button('Set Start Frame',
                                           id='setStart',),
                                dbc.Button('Set End Frame',
                                           id='setEnd',),
                                dbc.Button('Jump to Start',
                                           id='jumpStart',),
                                dbc.Button('Jump to End',
                                           id='jumpEnd',),
                            ],
                            style={"width": "100%"},
                        ),
                    ],
                    style={"margin-top": "20px", "margin-bottom": "10px", }
                ),
                dbc.Button('Save to Trim Queue',
                           id='addToTrim', color="primary", block=True),
            ]
        ),
    ],
    style={"margin-top": "20px", "margin-bottom": "20px"}
)


save_card = html.Div(
    id="state_one_card",
    children=[
        dbc.ButtonGroup(
            [
                dbc.Button('Discard Video', id='discard',
                           href='/apps/home', size="lg", color="danger"),
                dbc.Button('Save and Quit',
                           id='save-and-quit', href='/apps/home', size="lg"),
                # dbc.Button('Save and Continue',
                #            id='save-and-continue', href='/apps/dashboard', size="lg"),
                dbc.Button('Save and Continue',
                           id='save-and-continue', size="lg"),
            ],
            style={"width": "100%"},
        ),
        # dbc.Modal(
        #     [
        #         dbc.ModalHeader("Header"),
        #         dbc.ModalBody("This is the content of the modal"),
        #         dbc.ModalFooter(
        #             children=[dbc.Button("Close", id="close", className="ml-auto"),
        #                       dbc.Button("Close", id="close",
        #                                  className="ml-auto")
        #                       ]
        #         ),
        #     ]
        # )
    ],
)

layout = html.Div(
    [
        # navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(video_card_VE, md=7.5),
                        dbc.Col(children=[video_trimmer_card,
                                        save_card, ], md=5),
                    ],
                ),
            ],
            fluid=True,
        ),
        info_storage_VE
    ]
)






@app.callback(
    Output('frame_display_VE', 'children'),
    Input('frame_VE', 'data')
    )
def update_output(value):
    return (f'Current Frame Number: {value}')


@app.callback(
    Output('video_state_VE', 'data'),
    Output('playpause_VE', 'children'),
    Output('interval_VE', 'disabled'),
    Input('playpause_VE', 'n_clicks'),
    State('video_state_VE', 'data'),
    State('interval_VE', 'disabled'),
)
def player_state(play_button, video_state, interval_state):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    string = 'Pause' if interval_state else 'Play'
    text = html.Img(src = f'https://github.com/dianabisbe/Images/blob/main/{string}.png?raw=true',
                              style={'height':'30px'})
    

    video_state = not video_state 
    interval_state = not interval_state
    return video_state, text, interval_state

def get_frame(current_frame):

    vidcap = cv2.VideoCapture(filename)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    hasFrames, image = vidcap.read()
    if not hasFrames: return None 
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image  = cv2.resize(image, dsize=(resolution))
    vidcap.release()
    return image 


@app.callback(
    Output('canvas_VE', 'figure'),
    Input('frame_VE', 'data'),
    State('section_VE', 'data'),
    State('frame_VE', 'data'),)
def update_player(current_frame, section, frame_data):
    fig = px.imshow(get_frame(current_frame-1), binary_backend="jpg")
    fig.update_layout(
        xaxis= {
            'showgrid': False, # thin lines in the background
            'zeroline': False, # thick line at x=0
            'visible': False,  # numbers below
        },
        yaxis= {
            'showgrid': False, # thin lines in the background
            'zeroline': False, # thick line at x=0
            'visible': False,  # numbers below
        },
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        dragmode="drawrect",
    )
    return fig


@app.callback(
    Output('frame_VE', 'data'),
    Output('slider_VE', 'value'),
    Input('previous_VE', 'n_clicks'),
    Input('next_VE', 'n_clicks'),
    Input('fastforward-10_VE', 'n_clicks'),
    Input('fastforward-50_VE', 'n_clicks'),
    Input('rewind-10_VE', 'n_clicks'),
    Input('rewind-50_VE', 'n_clicks'),
    Input('interval_VE', 'n_intervals'),
    Input('slider_VE', 'value'),
    Input('section_VE', 'data'),

    Input('jumpStart', 'n_clicks'),
    Input('jumpEnd', 'n_clicks'),
    State('startingFrame', 'value'),
    State('endingFrame', 'value'),

    State('slider_VE', 'min'),
    State('slider_VE', 'max'),
    State('frame_VE', 'data'),
)
def update_frame(previous_VE, next_VE, ff10, ff50, rw10, rw50, interval, slider, section, startBut, endBut, start, end, slider_min, slider_max, data, ):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    print(cbcontext)
    if cbcontext == "previous_VE.n_clicks":
        data = data - 1 if data != slider_min else data 
        return data, data 
    elif cbcontext == "next_VE.n_clicks":
        data = data + 1 if data != slider_max else data 
        return data, data 
    elif cbcontext == "fastforward-10_VE.n_clicks":
        data = data + 10 if data < (slider_max - 10) else slider_max 
        return data, data 
    elif cbcontext == "fastforward-50_VE.n_clicks":
        data = data + 50 if data < (slider_max - 50) else slider_max 
        return data, data 
    elif cbcontext == "rewind-10_VE.n_clicks":
        data = data - 10 if data > (slider_min + 9) else slider_min 
        return data, data 
    elif cbcontext == "rewind-50_VE.n_clicks":
        data = data - 50 if data > (slider_min + 49) else slider_min 
        return data, data 
    elif cbcontext == "jumpStart.n_clicks":
        if(start >= slider_min and start <= slider_max):
            data = start
        return data, data 
    elif cbcontext == "jumpEnd.n_clicks":
        if(end >= slider_min and end <= slider_max):
            data = end
        return data, data 
    elif cbcontext == 'interval_VE.n_intervals': data += 1; return data, data
    elif cbcontext == 'section_VE.data': return slider_min, slider_min
    else: data = slider; return slider, slider


@app.callback(
    Output("slider_VE", 'min'),
    Output("slider_VE", 'max'),
    Output("slider_VE", 'marks'),
    Output('section_VE', 'data'),
    Input('dropdown_VE', 'value'),
    State('section_VE', 'data')
)
def initialize_section_and_slider(sectionValue, data):
    minFrame = (sectionValue * framesPerSection) + 1
    if (sectionValue+1) != sections:
        maxFrame = (sectionValue+1) * framesPerSection
    else:
        maxFrame = (frame_count % framesPerSection) + (minFrame-1)


    diff = round((maxFrame - minFrame)/20)
    marks = [(minFrame-1)+x*diff for x in range(21)]
    if marks[0] % framesPerSection == 0:
        marks[0] += 1
    sliderMarks = {}
    for i in marks:
        sliderMarks[f'{i}'] = f'{i}'

    data = sectionValue 
    return minFrame, maxFrame, sliderMarks, data

# initializes the states 
@app.callback(Output('dropdown_VE', 'value'),
                Input('section_VE', 'modified_timestamp'),
                State('section_VE', 'data'),
                State('frame_VE', 'data'),
                State('video_state_VE', 'data'),
)
def initial(section_ts, sectiondata, framedata, video_state):
    # if section_ts is None:
        # raise PreventUpdate
    sectiondata = sectiondata or 0
    framedata = framedata or 0
    video_state = False 
    return sectiondata

@app.callback(
    Output('trimmer-output-containerVE', 'children'),
    Input('frame-trimmer', 'value'))
def update_trimmer(value):
    return 'Selected "{}"'.format(value)

    
@app.callback(
    Output('trimming-container', 'children'),
    Input('addToTrim', 'n_clicks'),
    Input({'type': 'remove-trim', 'index': ALL}, 'n_clicks'),
    State('trimming-container', 'children'),
    State('startingFrame', 'value'),
    State('endingFrame', 'value'),
    prevent_initial_call=True)
def display_dropdown(n_clicks, _, children, start, end):
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if "index" in input_id:
        delete_trim = json.loads(input_id)["index"]
        children = [
            trim
            for trim in children
            if "'index': " + str(delete_trim) not in str(trim)
        ]
    else:
        new_trim = html.Div(
            dbc.Row(
                id='trimEntry',
                children=[
                    html.Div(f'Trimming Frame {start} through Frame {end}', className='current_frame'),
                    dcc.Store(
                        id={
                            'type': 'trim-start',
                            'index': n_clicks
                        },
                        storage_type='memory',  # change to session when in prod?
                        data=start
                    ),
                    dcc.Store(
                        id={
                            'type': 'trim-end',
                            'index': n_clicks
                        },
                        storage_type='memory',  # change to session when in prod?
                        data=end
                    ),
                    dbc.Button('Remove',
                                id={
                                    'type': 'remove-trim',
                                    'index': n_clicks
                                },
                                color='danger')], style={"display": "flex",  "justify-content": "space-between"}
            ), style={"width": "100%"}
        )
        children.append(new_trim)
    return children

@app.callback(
    Output('blacklist', 'data'),
    Input('save-and-continue', 'n_clicks'),
    State({'type': 'trim-start', 'index': ALL}, 'data'),
    State({'type': 'trim-end', 'index': ALL}, 'data'),
)
def blacklistFrames(n_clicks, start, end):
    if n_clicks is None:
        raise PreventUpdate
    else:
        # initialize array of True size of vid
        blacklist = np.ones(len(maxFrames), dtype=bool)
        for (i, data) in enumerate(start):
            for j in range(start[i], end[i]+1, 1):
                if(blacklist[j]):
                    blacklist[j] = False
        return blacklist

@app.callback(
    Output('testing', 'children'),
    Input('blacklist', 'data'),
)
def processVideo(blacklist):
    processFramesToVid(blacklist)
    return 'Donezo'

@app.callback(
    Output('startingFrame', 'max'),
    Output('endingFrame', 'max'),
    [Input('slider_VE', 'max')])
def set_maxVid(duration):
    return duration, duration

@app.callback(
    Output('startingFrame', 'value'),
    Input('setStart', 'n_clicks'),
    Input('addToTrim', 'n_clicks'),
    State('frame_VE', 'data'),
    prevent_initial_call=True
)
def setFrameToStart(set, add, value):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if cbcontext == "setStart.n_clicks":
        return value
    if cbcontext == "addToTrim.n_clicks":
        return None

@app.callback(
    Output('endingFrame', 'value'),
    Input('setEnd', 'n_clicks'),
    Input('addToTrim', 'n_clicks'),
    State('frame_VE', 'data'),
    prevent_initial_call=True
)
def setFrameToEnd(set, add, value):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if cbcontext == "setEnd.n_clicks":
        return value
    if cbcontext == "addToTrim.n_clicks":
        return None


