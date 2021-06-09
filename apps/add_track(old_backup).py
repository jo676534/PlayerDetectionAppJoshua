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
# import psycopg2 as pg2
# import pandas as pd
# from dash.exceptions import PreventUpdate
# import cv2  # from vid2frames

# from app import app

# from api import api_detections
# from api import api_team
# from api import api_player

# pathIn = './vid2img/'
# frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))] 
# frames.sort(key=lambda x: int(x[5:-4]))

# first_frame = 100
# final_frame = 200

# frames = frames[first_frame:final_frame]

# ########### END OLD VID TO FRAMES###########


# # GLOBAL VARIABLES #############################################################################################################################

# maxFrames = len(frames)-1
# player_tracks_counter = 0
# all_tracks_counter = 0
# viewable_tracks_counter = 0
# dic = api_detections.get_frame_detections(0)
# current_frame = 0
# player_tracks = ["17", "12"] # Hardcoded until "assign track" is working

# fig = px.imshow(io.imread(pathIn+frames[0]), binary_backend="jpg")


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
#                     id="graph_add",
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


# layout = html.Div( # was app.layout
#     [
#         #navbar,
#         dbc.Container(
#             [
#                 dbc.Row(
#                     [
#                         dbc.Col(image_annotation_card_add, md=7.5)
#                     ],
#                 ),
#             ],
#             fluid=True,
#         ),
#     ]
# )


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
#     Output('graph_add', 'figure'),
#     Output('frame_interval_add', 'n_intervals'),
#     Output('frame-slider_add', 'value'),
#     Input('frame_interval_add', 'n_intervals'),
#     Input('frame-slider_add', 'value'),
#     Input('previous_add', 'n_clicks'),
#     Input('next_add', 'n_clicks'),
#     State('frame_interval_add', 'disabled'),
# )
# def update_figure_add(interval, slider, previousBut, nextBut, isPaused):
#     # print(value)
#     cbcontext = [p["prop_id"] for p in dash.callback_context.triggered][0]
#     currentFrame = 0

#     if isPaused == False:
#         if interval is None:
#             interval = 0
#         currentFrame = interval
#     elif isPaused == True:
#         currentFrame = interval
#         if cbcontext == "previous_add.n_clicks":
#             if(currentFrame != 0):
#                 currentFrame += -1
#         if cbcontext == "next_add.n_clicks":
#             if(currentFrame != maxFrames):
#                 currentFrame += 1
#     if cbcontext == "frame-slider_add.value":
#         currentFrame = slider

#     fig = px.imshow(io.imread(pathIn+frames[currentFrame]), binary_backend="jpg") # OLD
#     # fig = px.imshow(frames[currentFrame], binary_backend="jpg") # NEW
#     frame_df = dic[currentFrame]
#     # print("\nCurrent Frame Bounding Boxes:")
#     for i in range(len(frame_df)):
#         x0 = frame_df.iloc[i]['x0']
#         y0 = frame_df.iloc[i]['y0']
#         x1 = frame_df.iloc[i]['x1']
#         y1 = frame_df.iloc[i]['y1']
#         id_num = frame_df.iloc[i]['track_id']
#         # print(id_num, x0, y0, x1, y1)
#     return (fig, currentFrame, currentFrame)


# # Callback for Slider
# @app.callback(
#     dash.dependencies.Output('slider-output-container_add', 'children'),
#     [dash.dependencies.Input('frame_interval_add', 'n_intervals')])
# def update_output_add(value):
#     return 'Current Frame "{}"'.format(value)
