
import plotly.express as px  # (version 4.7.0)


import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import cv2  # from vid2frames
from app import app

from api import api_detections
from api import api_team
from api import api_player

from .pysot.tools import demo

filename = "./Videos/game_0.mp4"
vidcap = cv2.VideoCapture(filename)

# OpenCV2 version 2 used "CV_CAP_PROP_FPS"
fps = vidcap.get(cv2.CAP_PROP_FPS)

# NEED BOTH FRAMES FROM STORE

frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
vidcap.release() 

duration = frame_count/fps
resolution = (1280, 720)

framesPerSection = 5000
maxFrames = frame_count-1
state = 0 # 0 is not submitted yet, 1 is submitted 
state_save = 0 # 0 is not run, 1 is run, 2 is run and saved, 99 is currently running and disables functionality
initials = ''
start = 0 
end = 0 

dic = {}
detections_df = []


# Start of dash components ===================================================================================================================


def add_editable_box(fig, track_id, x0, y0, x1, y1, name=None, color=None, opacity=1, group=None, text=None):
    global initials
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
    fig.add_annotation( #((x0+x1)/2)
        x=((x0+x1)/2),
        y=y0-30,
        text="{0}".format(initials),
        showarrow=False, #True
        font=dict(
            family="Courier New, monospace",
            size=9,
            color="#ffffff"
            ),
        align="center",
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#636363",
        ax=0, #20
        ay=0, #-30
        bordercolor="#c7c7c7",
        borderwidth=1, #2
        borderpad=2, #4
        bgcolor="#ff7f0e",
        opacity=0.8
    )


info_storage_add = html.Div([
    dcc.Store(id='frame_add', storage_type='local', data=1), 
    dcc.Store(id='video_state_add', storage_type='session', data=False),
    ])


right_side = dbc.Card(
    id = 'right_side_card',
    children = [
        dbc.CardHeader(
            [
                html.H2("Bounding Box Submit Area"),
                html.Div(id="which_player")
            ]
        ),
        dbc.CardBody(
            [
                html.H5("Instructions (Part 1):"),
                #html.Div("By default you can click and drag to draw an annotation bounding box on the image to the left. Once you draw a box around the player you are intending to track click on the submit box button to start the tracking."),
                html.Div("1. The video player is locked at the start frame until the tracker is finished running."),
                html.Div("2. Click and drag to draw an annotation bounding box around the intented player on the image."),
                html.Div("3. An already existing box can be interacted with by clicking on it's edges."),
                html.Div("  3a. It can then be modified by draging one of the corners."),
                html.Div("  3b. It can then be deleted by clicking \"Erase active shape\" in the top right corner above the image."),
                html.Div("4. Ensure there is only one bounding box around the intended player."),
                html.Div("5. Click \"Start Tracker\" below and wait for it to finish running."),
                html.Div("6. Don't press the button while the tracker is running."),
                html.Div("7. Once the tracker is finished, proceed to the area below."),
                #html.Br(),
                dbc.Button('Start Tracker', id='next_page', n_clicks=0, style = {'margin':'12px'}),
                html.Br(),
                dbc.Spinner(html.Div(id='button_output'))
            ]
        ),
        dbc.CardFooter(
            [
                html.H5("Instructions (Part 2):"),
                html.Div("There are now three primary options for using the detection track:"),
                html.Div("1. If there are no errors with the detections you can click \"Save Detection Track\" to finish."),
                html.Div("2. If part of the track is correct you can input a start and end frame below before saving the detection track to only save the frames within that window."),
                html.Div("3. If you'd like to remove the detections all together and start over you can reset the tracker and try again."),
                html.Div(""),
                #html.Br(),
                html.Div(
                    [
                        dbc.Input(id="input_start", placeholder="Start", type="number", min=0, step=1, style={'width': '25%', 'display': 'inline-block', "margin-left": "0px", "margin-right": "15px",}, className= 'add_track_input',),
                        dbc.Input(id="input_final", placeholder="Final", type="number", min=0, step=1, style={'width': '25%', 'display': 'inline-block', "margin-left": "15px", "margin-right": "15px",}, className= 'add_track_input',),
                    ]
                ),
                html.Div(
                    [
                        dbc.Button("Set Start Frame", id="set_start_add", style={'width': '25%', 'display': 'inline-block', "margin-left": "0px", "margin-right": "15px",}),
                        dbc.Button("Set Final Frame", id="set_final_add", style={'width': '25%', 'display': 'inline-block', "margin-left": "15px", "margin-right": "15px",}),
                    ]
                ),
            ]
        )
    ],
    style={"margin-top": "20px", "margin-bottom": "20px", "margin-right": "10px"})


end_buttons = dbc.Card(
    [
        dbc.ButtonGroup(
            [
                dbc.Button("Save Detection Track", id="button_save"),
                dbc.Button("Reset Tracker", id="button_reset", n_clicks=0),
                dbc.Button("Quit", id="button_quit_1", href='/apps/dashboard')
            ]
        ),
        html.Div(id="save_output"),
        html.Div(id="hidden_div_reset"),
    ])


video_card_add = dbc.Card(
    id="imagebox",
    children=[
        dbc.CardHeader(
        className= "player_card_header",
        ),
        dbc.CardBody(
            [
                html.Div(id="manual_annotation_output"),
                html.Div(children=[ # needs to be properly initialized //////////////////////////////////////////////////////////////////////
                    dcc.Interval(
                        id='interval_add',
                        disabled=False,
                        n_intervals=0,      # number of times the interval has passed
                        max_intervals=maxFrames # alternative way to do this = properly output the maxFrames to
                    ),
                ]),
                dcc.Graph( # WILL HAVE TO INITIALIZE THIS AS WELL //////////////////////////////////////////////////////////////////////////////////////////
                    id="canvas_add",
                    style={'width': '970px', 'height': '600px'},
                    config={"modeBarButtonsToAdd": ["drawrect", "eraseshape"]},
                )
            ]
        ),
        dbc.CardFooter(
            [
                # Slider Component
                dcc.Slider( # need to have a default slider w/pointless values and then have it replaced later during initialization ///////////////////////
                    id='slider_add',
                    step=1,

                ),
                html.Div(id='frame_display_add', className='current_frame'),
                # Pause/Player Buttons
                dbc.ButtonGroup(
                    [
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/rw50.png?raw=true',
                                                 style={'height':'30px'})],  
                                    id="rewind-50_add", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/rw10.png?raw=true',
                                                 style={'height':'30px'})],  
                                    id="rewind-10_add", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/Prev.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="previous_add", outline=True, style={
                                    "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/Play.png?raw=true',
                                                 style={'height':'30px'})],
                                   id="playpause_add", outline=True,
                                   style={"margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/Next.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="next_add", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/ff10.png?raw=true',
                                                 style={'height':'30px'})], 
                                    id="fastforward-10_add", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                        dbc.Button(children=[html.Img
                                                (src = 'https://github.com/dianabisbe/Images/blob/main/ff50.png?raw=true',
                                                 style={'height':'30px'})],
                                    id="fastforward-50_add", outline=True, style={
                                   "margin-right": "15px", "margin-bottom": "15px"}, color="light"),
                    ],
                    style={"width": "100%", 'margin-left':'-10px'}
                ),
            ]
        ),
    ],
    style={"margin-left": "5px","margin-top": "20px", "margin-bottom": "20px", "margin-right": "10px"}
    )


layout = html.Div(
    [
        #navbar,
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(video_card_add, md=7),
                        dbc.Col(children=[right_side, end_buttons], md=5),
                    ],
                ),
            ],
            fluid=True,
        ),
        info_storage_add
    ])


# Start of callbacks =========================================================================================================================


# Callback for the start tracker button
@app.callback(
    Output('button_output', 'children'),
    Input('next_page', 'n_clicks'),
    State('canvas_add', 'relayoutData'),
    State("start_frame_add", "data"),
    State("final_frame_add", "data"),
    prevent_initial_call=True)
def submit_box(n_clicks, graph_relayout, start_frame, final_frame):
    global detections_df
    global state

    if (state == 99):
        return "The tracker is still running, please wait for it to be finished."

    if (state == 1):
        return "The tracker has already been run"
    
    if graph_relayout is None: return '' # stops the error
    
    if (not 'shapes' in graph_relayout):
        # this is for whenever the user adjusts their bounding box. the info contained in the graph_relayout is changed and doesn't have shapes inside it so we need to check for and read a new form of info
        # a possible error of sorts is that the user could have two (or more) bounding boxes, adjust the zeroth box (the first they drew) and then submit and it would run
        if 'shapes[0].x0' in graph_relayout: 
            state = 99
            detections_df = demo.rt_track(start_frame, final_frame, graph_relayout['shapes[0].x0'], graph_relayout['shapes[0].y0'], graph_relayout['shapes[0].x1'], graph_relayout['shapes[0].y1'])
            state = 1
            return "The tracking algorithm has now finished, you can review the output in the video player."
        # otherwise we just display that there is an improper bounding box configuration
        return "Improper bounding box configuration"
    elif (len(graph_relayout['shapes']) == 0):
        return "You have to draw one bounding box"
    elif (len(graph_relayout['shapes']) == 1): # this is the success case
        state = 99
        for box in graph_relayout['shapes']: # this will only have one iteration (b/c there should only be one bounding box)
            detections_df = demo.rt_track(start_frame, final_frame, box['x0'], box['y0'], box['x1'], box['y1'])
        state = 1
        return "The tracking algorithm has now finished, you can review the output in the video player."
    else:
        return "There are too many bounding boxes"


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
    Output('canvas_add', 'figure'),
    Input('frame_add', 'data'),
    State('frame_add', 'data'),
    State('start_frame_add', 'data'),
    State("input_start", "value"),
    State("input_final", "value"),)
def update_player(current_frame, frame_data, start_frame, start_input, end_input):
    fig = px.imshow(get_frame(current_frame-1), binary_backend="jpg") # should subtract 1 b/c the video's frames are zero indexed while the slider is 1 indexed 
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

    # Need a new bit of code here to draw the singular new bounding box after it has been set up
    if state != 0: # draw the new bounding box
        x0 = detections_df.iloc[current_frame - start_frame]['x0'] 
        y0 = detections_df.iloc[current_frame - start_frame]['y0']
        x1 = detections_df.iloc[current_frame - start_frame]['x1']
        y1 = detections_df.iloc[current_frame - start_frame]['y1']
        track_id = detections_df.iloc[current_frame - start_frame]['track_id']
        add_editable_box(fig, track_id, x0, y0, x1, y1)
    return fig


# Callback to update the play button visual state
@app.callback(
    Output('video_state_add', 'data'),
    Output('playpause_add', 'children'),
    Output('interval_add', 'disabled'),
    Input('playpause_add', 'n_clicks'),
    State('video_state_add', 'data'),
    State('interval_add', 'disabled'),)
def player_state(play_button, video_state, interval_state):
    string = 'Pause' if interval_state else 'Play'
    text = html.Img(src = f'https://github.com/dianabisbe/Images/blob/main/{string}.png?raw=true', style={'height':'30px'})
    
    video_state = not video_state 
    interval_state = not interval_state
    return video_state, text, interval_state


# Update frame callback
@app.callback(
    Output('frame_add', 'data'),
    Output('slider_add', 'value'),
    Input('previous_add', 'n_clicks'),
    Input('next_add', 'n_clicks'),
    Input('fastforward-10_add', 'n_clicks'),
    Input('fastforward-50_add', 'n_clicks'),
    Input('rewind-10_add', 'n_clicks'),
    Input('rewind-50_add', 'n_clicks'),
    Input('interval_add', 'n_intervals'),
    Input('slider_add', 'value'),
    Input("hidden_div_reset", "children"),
    Input('slider_add', 'min'),
    Input('slider_add', 'max'),
    State('frame_add', 'data'),
    State('start_frame_add', 'data'),)
def update_frame(previous_add, next_add, ff10, ff50, rw10, rw50, interval, slider, hidden_div, slider_min, slider_max, data, start_frame):
    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]

    # check the state to stop the user from scrolling if they haven't input a new track
    if state == 2: 
        raise PreventUpdate

    if state != 0:
        if cbcontext == "previous_add.n_clicks":
            data = data - 1 if data != slider_min else data 
            return data, data
        elif cbcontext == "next_add.n_clicks":
            data = data + 1 if data != slider_max else data 
            return data, data
        elif cbcontext == "fastforward-10_add.n_clicks":
            data = data + 10 if data < (slider_max - 10) else slider_max
            return data, data
        elif cbcontext == "fastforward-50_add.n_clicks":
            data = data + 50 if data < (slider_max - 50) else slider_max
            return data, data
        elif cbcontext == "rewind-10_add.n_clicks":
            data = data - 10 if data > (slider_min + 9) else slider_min
            return data, data
        elif cbcontext == "rewind-50_add.n_clicks":
            data = data - 50 if data > (slider_min + 49) else slider_min
            return data, data
        elif cbcontext == 'interval_add.n_intervals': 
            data = data + 1 if data < slider_max else slider_max
            return data, data
        elif cbcontext == "hidden_div_reset.children":
            data = slider_min
            return data, data
        elif cbcontext == 'slider_add.min':
            data = start_frame
            return start_frame, start_frame
        else: data = slider; return slider, slider
    else:
        return slider_min, slider_min


# Callback to initialize the states and other variables 
@app.callback(    
    Output("slider_add", 'min'),
    Output("slider_add", 'max'),
    Output("slider_add", 'marks'),
    Input('start_frame_add', 'data'),
    Input('final_frame_add', 'data'),
    Input('player_id_add', 'data'),
    State('frame_add', 'data'),
    State('video_state_add', 'data'),
    State("game_id", "data"),)
def initial(startNum, endNum, player_id, framedata, video_state, game_id):
    global start
    global end
    global dic
    global initials
    global state
    global detections_df

    start, end = startNum, endNum
    framedata = startNum or 0
    video_state = False 

    state = 0
    detections_df = []

    diff = round((endNum - startNum)/20)
    marks = [(startNum-1)+x*diff for x in range(21)]
    sliderMarks = {}
    for i in marks:
        sliderMarks[f'{i}'] = f'{i}'

    dic = api_detections.get_partial_frame_detections(game_id, startNum, endNum)
    initials = api_detections.get_player_initials(player_id)

    return start, end, sliderMarks


# Set start frame callback
@app.callback(
    Output("input_start", "value"),
    Input("set_start_add", "n_clicks"),
    State("slider_add", "value"),
    prevent_initial_call=True)
def set_start_add(n_clicks, frame):
    if n_clicks is not None:
        return frame


# Set final frame callback
@app.callback(
    Output("input_final", "value"),
    Input("set_final_add", "n_clicks"),
    State("slider_add", "value"),
    prevent_initial_call=True)
def set_start_add(n_clicks, frame):
    if n_clicks is not None:
        return frame


# Player output callback
@app.callback(
    Output("which_player", "children"),
    Input('player_id_add', 'data'),
    Input("game_id", "data"),)
def which_player(player_id, game_id):
    df = api_player.get_player(game_id, player_id)
    name = df.iloc[0]["name"]
    jersey = df.iloc[0]["jersey"]
    return "Intended player is {} with jersey #{}".format(name, jersey)


# Current frame display callback
@app.callback(
    Output('frame_display_add', 'children'),
    Input('frame_add', 'data'),)
def update_output(value):
    return (f'  Current Frame Number: {value}')

    
# Save Detection & Reset Tracker Callback
@app.callback(
    Output("save_output", "children"),
    Output("hidden_div_reset", "children"),
    Input("button_save", "n_clicks"),
    Input("button_reset", "n_clicks"),
    State("input_start", "value"), # start_frame (represents the start value for a subset selection of frames)
    State("input_final", "value"), # final_frame 
    State("start_frame_add", "data"), # sf (represents the original start frame value)
    State("final_frame_add", "data"), # ff
    State('player_id_add', 'data'),
    State('frame_add', 'data'),
    State("game_id", "data"),
    prevent_initial_call=True)
def save_detection(save_clicks, reset_clicks, start_input, final_input, start_frame, final_frame, player_id, current_frame, game_id):
    # STATES TO PRECEED CHECKING THE INPUT
    global state
    global detections_df

    cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
    print(cbcontext)

    # first check for if it was reset button
    if cbcontext == "button_reset.n_clicks":
        detections_df = []
        state = 0
        return "Reset Complete", None

    # Check states to make sure we're ready to take the input
    if state == 0 or state == 99:
        return "The tracker needs to be run first", None
    elif state == 2:
        return "Track already saved. Now click quit to return.", None
    elif state != 1:
        return "Unknown ERROR", None

    # STATES FOR ACTUAL INPUT
    # Good State: user input nothing and wants the whole clip
    if (start_input is None) and (final_input is None):
        state = 2
        # need to check for player track overlap
        # save the detection track first (but not assigned the player quite yet)
        track_id = api_detections.unique_track_id(game_id)
        api_detections.save_track(game_id, detections_df, start_frame, track_id, -1) # Do NOT change -1. It NEEDS to be -1 for this

        # then get the three arrays for the intersection of the track and player
        player_frames = api_detections.get_player_frames(game_id, player_id)
        track_frames = api_detections.get_track_frames(game_id, track_id)
        intersection = [val for val in track_frames if val in player_frames]

        # now delete the detections of the track where there is intersection
        if intersection:
            api_detections.delete_detection_list(game_id, track_id, intersection)

        # finally change the player_id to the proper player_id
        api_detections.assign_track(game_id, player_id, track_id)
        
        return "Track saved. Now click quit to return.", None
    # Bad State: user input one but not the other
    elif (start_input is None) or (final_input is None): 
        return "Need either both inputs or neither", None
    # Bad State: start is greater than or equal to final
    elif (start_input >= final_input):
        return "Start frame has to be less than final frame", None
    # Good State: user input but and we need to use them
    else:
        state = 2
        # need to check for player track overlap
        # need to cut the df for the frame outline

        # test
        detections_df = detections_df[start_input-start_frame:final_input-final_frame+1] 
        # new form of overlap detection
        # save the detection track first (but not assigned the player quite yet)
        track_id = api_detections.unique_track_id(game_id)
        api_detections.save_track(game_id, detections_df, start_frame, track_id, -1)

        # then get the three arrays for the intersection of the track and player
        player_frames = api_detections.get_player_frames(game_id, player_id)
        track_frames = api_detections.get_track_frames(game_id, track_id)
        intersection = [val for val in track_frames if val in player_frames]

        # now delete the detections of the track where there is intersection
        api_detections.delete_detection_list(game_id, track_id, intersection)

        # finally change the player_id to the proper player_id
        api_detections.assign_track(game_id, player_id, track_id)
        
        return "Track saved. Now click quit to return.", None
