# # INSTALL LIBRARIES ---------------------------------------------------------------------------------------------------------------------------

# import pandas as pd
# import plotly.express as px  # (version 4.7.0)
# import plotly.graph_objects as go

# import dash  # (version 1.12.0) pip install dash
# import dash_core_components as dcc
# import dash_bootstrap_components as dbc
# import dash_html_components as html
# from dash.dependencies import Input, Output, State
# import os
# from os.path import isfile, join
# from skimage import io
# import numpy as np
# # import psycopg2 as pg2
# import pandas as pd
# from dash.exceptions import PreventUpdate
# import cv2  # from vid2frames

# from app import app

# from api import api_detections
# from api import api_team
# from api import api_player

# from .pysot.tools import josh_test
# from .pysot.tools import demo

# pathIn = './vid2img/'
# frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))] 
# frames.sort(key=lambda x: int(x[5:-4]))

# first_frame = 100
# final_frame = 120

# frames = frames[first_frame:final_frame]

# ########### END OLD VID TO FRAMES ###########


# # GLOBAL VARIABLES #############################################################################################################################

# maxFrames = len(frames)-1
# player_tracks_counter = 0
# all_tracks_counter = 0
# viewable_tracks_counter = 0
# dic = api_detections.get_frame_detections(0)
# current_frame = 0
# player_tracks = ["17", "12"] # Hardcoded until "assign track" is working

# detections_df = []

# state = 0 # 0 is not submitted yet, 1 is submitted 

# fig = px.imshow(io.imread(pathIn+frames[0]), binary_backend="jpg")
# fig.update_layout(
#     margin=dict(l=0, r=0, b=0, t=0, pad=4),
#     dragmode="drawrect",
# )

# # NORMAL FUNCTIONS #############################################################################################################################

# def add_editable_box(fig, id_num, x0, y0, x1, y1, name=None, color=None, opacity=1, group=None, text=None):
#     fig.add_shape(
#         editable=True,
#         x0=x0,
#         y0=y0,
#         x1=x1,
#         y1=y1,
#         line_color=color,
#         opacity=opacity,
#         line_width=3,
#         name=name,
#     )
#     fig.add_annotation( #((x0+x1)/2)
#         x=((x0+x1)/2),
#         y=y0-30,
#         text="{0}".format(id_num),
#         showarrow=False, #True
#         font=dict(
#             family="Courier New, monospace",
#             size=9,
#             color="#ffffff"
#             ),
#         align="center",
#         arrowhead=2,
#         arrowsize=1,
#         arrowwidth=2,
#         arrowcolor="#636363",
#         ax=0, #20
#         ay=0, #-30
#         bordercolor="#c7c7c7",
#         borderwidth=1, #2
#         borderpad=2, #4
#         bgcolor="#ff7f0e",
#         opacity=0.8
#     )

# # DASH COMPONENTS ##############################################################################################################################

# image_annotation_card_add = dbc.Card(
#     id="imagebox_add",
#     children=[
#         dbc.CardBody(
#             [
#                 dcc.Interval(
#                     id='frame_interval_add',
#                     interval=500,
#                     disabled=True,
#                     n_intervals=0,      # number of times the interval has passed
#                     max_intervals=maxFrames
#                 ),
#                 dcc.Graph(
#                     id="graph_box",
#                     style={'width':'1000px', 'height':'600px'},
#                     figure=fig,
#                     config={"modeBarButtonsToAdd": ["drawrect", "eraseshape"]},
#                 )
#             ]
#         ),
#         dbc.CardFooter(
#             [
#                 # Slider Component
#                 dcc.Slider(
#                     id='frame-slider_add',
#                     min=0,
#                     max=maxFrames,
#                     value=0,
#                     step=1,
#                     marks={round(i*maxFrames/16): '{}'.format(round(i*maxFrames/16))
#                            for i in range(maxFrames)},
#                 ),
#                 html.Div(id='slider-output-container_add'),
#                 # Pause/Player Buttons
#                 dbc.ButtonGroup(
#                     [
#                         dbc.Button("Previous", id="previous_add", outline=True, style={
#                                    "margin-left": "50px", "margin-right": "15px", "margin-bottom": "15px"}),
#                         dbc.Button("Rewind", id="rewind_add", outline=True, style={
#                                    "margin-right": "15px", "margin-bottom": "15px"}),
#                         dbc.Button("Play", id="playpause_add", outline=True,
#                                    style={"margin-right": "15px", "margin-bottom": "15px"}),
#                         dbc.Button("Fastforward", id="fastforward_add", outline=True, style={
#                                    "margin-right": "15px", "margin-bottom": "15px"}),
#                         dbc.Button("  Next  ", id="next_add", outline=True, style={
#                                    "margin-right": "15px", "margin-bottom": "15px"}),
#                     ],
#                     style={"width": "100%"}
#                 ),
#             ]
#         ),
#     ],
#     style={"margin-top": "20px", "margin-bottom": "20px"}
# )


# right_side = dbc.Card(
#     children=[
#         dbc.CardHeader(
#             html.H2("Header")
#         ),
#         dbc.CardBody(
#             [
#                 html.Div(id='output'),
#                 html.Br(),
#                 html.Button('Submit', id='next_page', n_clicks=0),
#                 html.Br(),
#                 html.Div(id='button_output')
#             ]
#         ),
#         dbc.CardFooter(
#             [
#                 html.H2("Footer"),
#                 html.Br(),
#                 html.Button("State Button", id='state_button', n_clicks=0),
#                 html.Br(),
#                 html.Div(id="state_output"),
#             ]
#         ),
#     ]
# )


# layout = html.Div( # was app.layout
#     [
#         #navbar,
#         dbc.Container(
#             [
#                 dbc.Row(
#                     [
#                         dbc.Col(image_annotation_card_add, md=7.5),
#                         dbc.Col(right_side)
#                     ],
#                 ),
#             ],
#             fluid=True,
#         ),
#     ]
# )

# # CALLBACKS START HERE #########################################################################################################################

# # Call back for video Player/Pause
# @app.callback(
#     Output('frame_interval_add', 'disabled'),
#     Output('playpause_add', 'children'),
#     Input('playpause_add', 'n_clicks'),
#     State('frame_interval_add', 'disabled'),
# )
# def togglePlay_add(play, isPaused):
#     cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
#     text = 'Play'

#     if cbcontext == "playpause_add.n_clicks":
#         if isPaused == True:
#             isPaused = False
#             text = 'Pause'
#         elif isPaused == False:
#             isPaused = True
#         else:
#             raise PreventUpdate
#     return (isPaused, text)


# # Video Display Callback
# @app.callback(
#     Output('graph_box', 'figure'),
#     Output('frame_interval_add', 'n_intervals'),
#     Output('frame-slider_add', 'value'),
#     Output('graph_box', 'relayoutData'), # testing
#     Input('frame_interval_add', 'n_intervals'),
#     Input('frame-slider_add', 'value'),
#     Input('previous_add', 'n_clicks'),
#     Input('next_add', 'n_clicks'),
#     State('frame_interval_add', 'disabled'),
#     State('graph_box', 'relayoutData'), # testing
# )
# def update_figure_add(interval, slider, previousBut, nextBut, isPaused, graph_relayout):
#     print(state)
#     cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
#     currentFrame = 0
    
#     # check the state to stop the user from scrolling if they haven't input a new track
#     if state != 0:
#         if isPaused == False:
#             if interval is None:
#                 interval = 0
#             currentFrame = interval
#         elif isPaused == True:
#             currentFrame = interval
#             if cbcontext == "previous_add.n_clicks":
#                 if(currentFrame != 0):
#                     currentFrame += -1
#             if cbcontext == "next_add.n_clicks":
#                 if(currentFrame != maxFrames):
#                     currentFrame += 1
#         if cbcontext == "frame-slider_add.value":
#             currentFrame = slider
    
#     fig = px.imshow(io.imread(pathIn+frames[currentFrame]), binary_backend="jpg") # OLD # fig = px.imshow(frames[currentFrame], binary_backend="jpg") # NEW
#     fig.update_layout(
#         margin=dict(l=0, r=0, b=0, t=0, pad=4),
#         dragmode="drawrect",
#     )
    
#     # Need a new bit of code here to draw the singular new bounding box after it has been set up
#     if state != 0: # draw the new bounding box
#         x0 = detections_df.iloc[currentFrame]['x0']
#         y0 = detections_df.iloc[currentFrame]['y0']
#         x1 = detections_df.iloc[currentFrame]['x1']
#         y1 = detections_df.iloc[currentFrame]['y1']
#         track_id = detections_df.iloc[currentFrame]['track_id']
#         add_editable_box(fig, track_id, x0, y0, x1, y1)

#     # print("%%% Graph Relayout Length: {} %%%".format(len(graph_relayout['shapes'])))
#     return (fig, currentFrame, currentFrame, {'shapes': []}) 
# # the empty graph_relayout may cause problems later down the line when we actually want to draw the bounding box
# # solution would be to pass the actual graph_relayout depending on the context/state


# # Callback for Slider
# @app.callback(
#     dash.dependencies.Output('slider-output-container_add', 'children'),
#     [dash.dependencies.Input('frame_interval_add', 'n_intervals')])
# def update_output_add(value):
#     return 'Current Frame "{}"'.format(value)


# # Callback for state button
# @app.callback(
#     Output('state_output', 'children'),
#     Input('state_button', 'n_clicks')
# )
# def test_func(n_clicks):
#     global state
#     if state == 0:
#         #state = 1
#         return "State is 0"
#     else:
#         #state = 0
#         return "State is 1"


# # Callback for the submit button
# @app.callback(
#     Output('button_output', 'children'),
#     Input('next_page', 'n_clicks'),
#     State('graph_box', 'relayoutData'),
# )
# def submit_box(n_clicks, graph_relayout):
#     global detections_df
#     global state

#     if graph_relayout is None: return '' # stops the error
    
#     if (not 'shapes' in graph_relayout):
#         return "No bounding box has been drawn yet"
#     elif (len(graph_relayout['shapes']) == 0):
#         return "You have to draw one bounding box"
#     elif (len(graph_relayout['shapes']) == 1): # this is the success case
#         print("in submit box 1")
#         print("in submit box 2")
#         for box in graph_relayout['shapes']:
#             x0 = box['x0']
#             y0 = box['y0']
#             x1 = box['x1']
#             y1 = box['y1']
#             detections_df = demo.rt_track(100, 120, x0, y0, x1, y1) # !!! this will have to recieve a dataframe to be used with the display !!! WORK HERE 
#             state = 1
#         return josh_test.josh_string() # "You have drawn one bounding box, next page goes here"
#     else:
#         return "There can only be one bounding box, please ensure there is only one"
# # end submit_box


# # Callback for the updated output
# @app.callback(
#     Output('output', 'children'),
#     Input('graph_box', 'relayoutData')
# )
# def update_output(graph_relayout): # graph_relayout is a dictionary
#     if graph_relayout is None: return '' # stops the error
    
#     if (not 'shapes' in graph_relayout) or (len(graph_relayout['shapes']) == 0): # or shapes is empty 
#         print(graph_relayout)
#         return 'no shapes'
#     else:
#         print("### TRYING TO DO THIS ###")
#         output_string = "List of boxes: "
#         output_num = 0
#         for box in graph_relayout['shapes']:
#             output_num += 1
#             output_string += "\nBox #{}: ".format(output_num)
#             output_string += "X0: {}, ".format(box['x0'])
#             output_string += "Y0: {}, ".format(box['y0'])
#             output_string += "X1: {}, ".format(box['x1'])
#             output_string += "Y1: {}".format(box['y1'])
#             output_string += " ###### "
        
#         print(graph_relayout)
#         return 'Number of boxes: {0}'.format(output_num)
#         #return 'Number of boxes: {0} "<br />" Updated output: {1}'.format(output_num, output_string) # graph_relayout['shapes']
# # end update_output