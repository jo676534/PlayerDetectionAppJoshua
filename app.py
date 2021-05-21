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


# connect to database-----------------------------------------------------------------------------------------------------------------------
conn = pg2.connect(database='soccerdb',
                   user='postgres',
                   host='localhost', 
                   password='root')

cur = conn.cursor()

# execute SQL query
cur.execute('''SELECT *
                FROM detections''')
data = cur.fetchall()

# Create Data Frame
cols = []
for elt in cur.description:
    cols.append(elt[0])

df = pd.DataFrame(data=data, columns=cols)

# Do it all again for teams
# teams

cur = conn.cursor()

cur.execute('''SELECT *
                FROM team''')

teams_data = cur.fetchall()
tcols = []
for elt in cur.description:
    tcols.append(elt[0])

df_teams = pd.DataFrame(data=teams_data, columns=tcols)

# Do it all again for players
# players

cur = conn.cursor()
cur.execute('''SELECT *
                FROM player''')
players_data = cur.fetchall()
pcols = []
for elt in cur.description:
    pcols.append(elt[0])

df_players = pd.DataFrame(data=players_data, columns=pcols)

# Close Connection after we are done
cur.close()
conn.close()

# FUNCTION DEFINITIONS ------------------------------------------------------------------------------------------------------------------------
# Start of Mark components



########### NEW VID TO FRAMES###########
# vidcap = cv2.VideoCapture('Sample Soccer Video.mp4')
# frames = []

# def getFrame(sec):
#     vidcap.set(cv2.CAP_PROP_POS_MSEC, sec*1000)
#     hasFrames, image = vidcap.read()
#     if hasFrames:
#         # Instead of writing to directory, save to an image array
#         # cv2.imwrite(os.path.join(dirname,"image"+str(count) + ".jpg"), image)
#         image2 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#         frames.append(image2)
#     return hasFrames

# sec = 0
# frameRate = 0.02  # 30 frames per second?
# count = 1
# success = getFrame(sec)
# while success:
#     count = count + 1
#     sec = sec + frameRate
#     sec = round(sec, 2)
#     success = getFrame(sec)
########### END NEW VID TO FRAMES###########


########### OLD VID TO FRAMES###########

pathIn = './vid2img/'
frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
frames.sort(key=lambda x: int(x[5:-4]))



########### END OLD VID TO FRAMES###########


maxFrames = len(frames)-1

# End of Mark components

# Global Variables Definitions
player_tracks_counter = 0
all_tracks_counter = 0
viewable_tracks_counter = 0
dic = {}
current_frame = 0
player_tracks = ["17", "12"] # Hardcoded until "assign track" is working

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
    for i in range(maxFrames):
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


def updateSection(button_id):
    global section
    if button_id == "but7":
        section = "A"
    if button_id == "but8":
        section = "B"

# This function queries the database and gets the current
# frame value stored 
def getFrame():
    conn = pg2.connect(database='soccerdb',
            user='postgres',
            host='localhost',  
            password='root')
    cur = conn.cursor()
    cur.execute('''SELECT frame FROM variables''')
    currentFrame = cur.fetchall()
    print(currentFrame)
    # conn.commit()
    cur.close()
    conn.close()
    return currentFrame

# START APP / DASH COMPONENTS -----------------------------------------------------------------------------------------------------------------

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
fig = px.imshow(io.imread(pathIn+frames[0]), binary_backend="jpg") # OLD
# fig = px.imshow(frames[0], binary_backend="jpg")  NEW


# Button Sections for teams:
# Retrive value for each team
a_row = df_players[df_players["team_id"] == 0]
sectionA = html.Div(
    [
        dbc.Row(
            dbc.Col([
                dbc.Button(
                    str(a_row.iloc[0]["name"]),
                    id="collapse-button3",
                    className="mb-3",
                    color="secondary",
                    style={"font-size": "12px"}
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody([
                        dbc.Row(dcc.Markdown(
                            "Number of Tracks: 0", style={"font-size": "10px"}),),
                        dbc.Row(dbc.Button("Add Selected Track", id="add_track", color="black", style={
                            "font-size": "10px"}),),
                        dbc.Row(dbc.Button("Create New Track", color="black", style={
                            "font-size": "10px"}),),
                        dbc.Row(dbc.Button("View Player Tracks", color="black", style={
                            "font-size": "10px"}),),
                    ])),
                    id="collapse3",
                    style={"font-size": "12px"}
                ),
            ])),
        dbc.Row(
            dbc.Col([
                dbc.Button(
                    str(a_row.iloc[1]["name"]),
                    id="collapse-button4",
                    className="mb-3",
                    color="secondary",
                    style={"font-size": "12px"}
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody([
                        dbc.Row(dcc.Markdown(
                                          "Number of Tracks: 0", style={"font-size": "10px"}),),
                        dbc.Row(dbc.Button("Add Selected Track", color="black", style={
                            "font-size": "10px"}),),
                        dbc.Row(dbc.Button("Create New Track", color="black", style={
                            "font-size": "10px"}),),
                        dbc.Row(dbc.Button("View Player Tracks", color="black", style={
                            "font-size": "10px"}),),
                    ])),
                    id="collapse4",
                    style={"font-size": "12px"}
                ),
            ]))
    ])
b_row = df_players[df_players["team_id"] == 1]
sectionB = html.Div(
    [
        dbc.Row(
            dbc.Col([
                dbc.Button(
                    str(b_row.iloc[3]["name"]),
                    id="collapse-button3",
                    className="mb-3",
                    color="secondary",
                    style={"font-size": "12px"}
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody([
                        dbc.Row(dcc.Markdown(
                            "Number of Tracks: 0", style={"font-size": "10px"}),),
                        dbc.Row(dbc.Button("Add Selected Track", color="black", style={
                            "font-size": "10px"}),),
                        dbc.Row(dbc.Button("Create New Track", color="black", style={
                            "font-size": "10px"}),),
                        dbc.Row(dbc.Button("View Player Tracks", color="black", style={
                            "font-size": "10px"}),),
                    ])),
                    id="collapse3",
                    style={"font-size": "12px"},
                ),
            ])),
        dbc.Row(
            dbc.Col([
                dbc.Button(
                    str(b_row.iloc[4]["name"]),
                    id="collapse-button4",
                    className="mb-3",
                    color="secondary",
                    style={"font-size": "12px"}
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody([
                        dbc.Row(dcc.Markdown(
                            "Number of Tracks: 0", style={"font-size": "10px"}),),
                        dbc.Row(dbc.Button("Add Selected Track", color="black", style={
                            "font-size": "10px"}),),
                        dbc.Row(dbc.Button("Create New Track", color="black", style={
                            "font-size": "10px"}),),
                        dbc.Row(dbc.Button("View Player Tracks", color="black", style={
                            "font-size": "10px"}),),
                    ])),
                    id="collapse4",
                    style={"font-size": "12px"}
                ),
            ]))
    ])

# Button Sections for Tracks:

# Generate button for each Track
def generate_allTracks_row(i):
    global all_tracks_counter
    all_tracks_counter += 1

    if all_tracks_counter == 3 or all_tracks_counter == 4:
        all_tracks_counter += 2

    return dbc.Row(
        dbc.Col([
            dcc.Checklist(id="checkbox"+str(i), options=[
                          {'label': ' ', 'value': 'false', 'disabled': False}, ], value=['true']),
            dbc.Button(
                str(df.iloc[all_tracks_counter]
                    ['track_id']),
                id="collapse-button" +
                str(all_tracks_counter),
                className="mb-3",
                color="secondary",
                style={"font-size": "12px"},
            ),
            dbc.Collapse(
                dbc.Card(dbc.CardBody([
                    dbc.Row(dbc.Button("Modify Track: Go to Start("+str(
                        all_tracks_counter)+")", color="black", style={"font-size": "12px"}),),
                    dbc.Row(dbc.Button("Delete Track: Go to End("+str(
                        all_tracks_counter+1)+")", color="black", style={"font-size": "12px"}),),
                ])),
                id="collapse"+str(all_tracks_counter),
                style={"font-size": "12px"}
            ),
        ]))

# All Track Section Component
allTrackSection = html.Div([
    html.Div(children=[generate_allTracks_row(i) for i in range(1, 7)]),
])


# Old AllTrackSectionComponent
'''
allTrackSection = html.Div(
                    [
                        dbc.Row(
                         dbc.Col([
                            html.P("ID #: " + str(df.iloc[0]['track_id']), style={"font-size": "12px"}),
                            html.P("Start: "+all_uniqueTracks[allids[0]]["start"], style={"font-size": "12px"}),
                            html.P("End: "+all_uniqueTracks[allids[0]]["end"], style={"font-size": "12px"}),
                            #dcc.Store(id='store1',value = str(df.iloc[0]['track_id'])),
                            dbc.Button(
                                "Expand ",
                                id="collapse-button1",
                                className="mb-3",
                                color="secondary",
                                style={ "font-size": "12px"},
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody([
                                dcc.Markdown("Modify Track:   " "**Go to Start**"),
                                dcc.Markdown("Delete Track:   " "**Go to End**")
                                ])),
                                id="collapse1",
                                style={ "font-size": "12px"}
                            ),
                        ])),
                        dbc.Row(
                          dbc.Col([
                             html.P("ID #: "+str(df.iloc[1]['track_id']), style={"font-size": "12px"}),
                            html.P("Start: "+all_uniqueTracks[allids[1]]["start"], style={"font-size": "12px"}),
                            html.P("End: "+all_uniqueTracks[allids[1]]["end"], style={"font-size": "12px"}),
                            dbc.Button(
                                "Expand ",
                                id="collapse-button2",
                                className="mb-3",
                                color="secondary",
                                style={"font-size": "12px"}
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody([
                                dcc.Markdown("Modify Track:   " "**Go to Start**"),
                                dcc.Markdown("Delete Track:   " "**Go to End**")
                                ])),
                                id="collapse2",
                                style={ "font-size": "12px"}
                            ),
                        ])),
                         dbc.Row(
                          dbc.Col([
                            html.P("ID #: "+str(df.iloc[2]['track_id']), style={"font-size": "12px"}),
                            html.P("Start: "+all_uniqueTracks[allids[2]]["start"], style={"font-size": "12px"}),
                            html.P("End: "+all_uniqueTracks[allids[2]]["end"], style={"font-size": "12px"}),
                            dbc.Button(
                                "Expand ",
                                id="collapse-button5",
                                className="mb-3",
                                color="secondary",
                                style={"font-size": "12px"}
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody([
                                dcc.Markdown("Modify Track:   " "**Go to Start**"),
                                dcc.Markdown("Delete Track:   " "**Go to End**")
                                ])),
                                id="collapse5",
                                style={ "font-size": "12px"}
                            ),
                        ])),
                         dbc.Row(
                          dbc.Col([
                             html.P("ID #: "+str(df.iloc[3]['track_id']), style={"font-size": "12px"}),
                            html.P("Start: "+all_uniqueTracks[allids[3]]["start"], style={"font-size": "12px"}),
                            html.P("End: "+all_uniqueTracks[allids[3]]["end"], style={"font-size": "12px"}),
                            dbc.Button(
                                "Expand ",
                                className="mb-3",
                                id="collapse-button6",
                                color="secondary",
                                style={"font-size": "12px"}
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody([
                                dcc.Markdown("Modify Track:   " "**Go to Start**"),
                                dcc.Markdown("Delete Track:   " "**Go to End**")
                                ])),
                                id="collapse6",
                                style={ "font-size": "12px"}
                            ),
                        ])),
                         dbc.Row(
                          dbc.Col([
                             html.P("ID #: "+str(df.iloc[4]['track_id']), style={"font-size": "12px"}),
                            html.P("Start: "+all_uniqueTracks[allids[4]]["start"], style={"font-size": "12px"}),
                            html.P("End: "+all_uniqueTracks[allids[4]]["end"], style={"font-size": "12px"}),
                            dbc.Button(
                                "Expand ",
                                id="collapse-button7",
                                className="mb-3",
                                color="secondary",
                                style={"font-size": "12px"}
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody([
                                dcc.Markdown("Modify Track:   " "**Go to Start**"),
                                dcc.Markdown("Delete Track:   " "**Go to End**")
                                ])),
                                id="collapse7",
                                style={ "font-size": "12px"}
                            ),
                        ])),
                         dbc.Row(
                          dbc.Col([
                            html.P("ID #: "+str(df.iloc[5]['track_id']), style={"font-size": "12px"}),
                            html.P("Start: "+all_uniqueTracks[allids[5]]["start"], style={"font-size": "12px"}),
                            html.P("End: "+all_uniqueTracks[allids[5]]["end"], style={"font-size": "12px"}),
                            dbc.Button(
                                "Expand ",
                                id="collapse-button8",
                                className="mb-3",
                                color="secondary",
                                style={"font-size": "12px"}
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody([
                                dcc.Markdown("Modify Track:   " "**Go to Start**"),
                                dcc.Markdown("Delete Track:   " "**Go to End**")
                                ])),
                                id="collapse8",
                                style={ "font-size": "12px"}
                            ),
                        ])),
                         dbc.Row(
                          dbc.Col([
                            html.P("ID #: "+str(df.iloc[6]['track_id']), style={"font-size": "12px"}),
                            html.P("Start: "+all_uniqueTracks[allids[6]]["start"], style={"font-size": "12px"}),
                            html.P("End: "+all_uniqueTracks[allids[6]]["end"], style={"font-size": "12px"}),
                            dbc.Button(
                                "Expand ",
                                id="collapse-button9",
                                className="mb-3",
                                color="secondary",
                                style={"font-size": "12px"}
                            ),
                            dbc.Collapse(
                                dbc.Card(dbc.CardBody([
                                dcc.Markdown("Modify Track:   " "**Go to Start**"),
                                dcc.Markdown("Delete Track:   " "**Go to End**")
                                ])),
                                id="collapse9",
                                style={ "font-size": "12px"}
                            ),
                        ])),  
                    ])
'''
# viewableTrackSection = html.Div([
#     dcc.Markdown(str(getFrame()))
# ])

# Old Viewable Track Section Component
# viewableTrackSection = html.Div(children=[
#     dbc.Row(
#         dbc.Col([
#                                 html.P(
#                                     "ID #: "+viewableTracksList[0], style={"font-size": "12px"}),
#                                 html.P(
#                                     "Start: "+all_uniqueTracks[viewableTracksList[0]]["start"], style={"font-size": "12px"}),
#                                 html.P(
#                                     "End: "+all_uniqueTracks[viewableTracksList[0]]["end"], style={"font-size": "12px"}),
#                                 dbc.Button(
#                                     "Expand ",
#                                     id="collapse-button1",
#                                     className="mb-3",
#                                     color="secondary",
#                                     style={"font-size": "12px"}
#                                 ),
#                                 dbc.Collapse(
#                                     dbc.Card(dbc.CardBody([
#                                         dcc.Markdown(
#                                             "Modify Track:   " "**Go to Start**"),
#                                         dcc.Markdown(
#                                             "Delete Track:   " "**Go to End**")
#                                     ])),
#                                     id="collapse1",
#                                     style={"font-size": "12px"}
#                                 ),
#                                 ])),
#     dbc.Row(
#         dbc.Col([
#             html.P("ID #: "+viewableTracksList[1],
#                    style={"font-size": "12px"}),
#             html.P(
#                 "Start: "+all_uniqueTracks[viewableTracksList[1]]["start"], style={"font-size": "12px"}),
#             html.P(
#                 "End: "+all_uniqueTracks[viewableTracksList[1]]["end"], style={"font-size": "12px"}),
#             dbc.Button(
#                 "Expand ",
#                 id="collapse-button2",
#                 className="mb-3",
#                 color="secondary",
#                 style={"font-size": "12px"}
#             ),
#             dbc.Collapse(
#                 dbc.Card(dbc.CardBody([
#                     dcc.Markdown(
#                         "Modify Track:   " "**Go to Start**"),
#                     dcc.Markdown(
#                         "Delete Track:   " "**Go to End**")
#                 ])),
#                 id="collapse2",
#                 style={"font-size": "12px"}
#             ),
#         ])),
#     dbc.Row(
#         dbc.Col([
#             html.P("ID #: "+allids[2], style={"font-size": "12px"}),
#             html.P(
#                 "Start: "+all_uniqueTracks[viewableTracksList[2]]["start"], style={"font-size": "12px"}),
#             html.P(
#                 "End: "+all_uniqueTracks[viewableTracksList[2]]["end"], style={"font-size": "12px"}),
#             dbc.Button(
#                 "Expand ",
#                 id="collapse-button5",
#                 className="mb-3",
#                 color="secondary",
#                 style={"font-size": "12px"}
#             ),
#             dbc.Collapse(
#                 dbc.Card(dbc.CardBody([
#                     dcc.Markdown(
#                         "Modify Track:   " "**Go to Start**"),
#                     dcc.Markdown(
#                         "Delete Track:   " "**Go to End**")
#                 ])),
#                 id="collapse5",
#                 style={"font-size": "12px"}
#             ),
#         ])),
# ])



# Generates ea/ button for the viewable tracks
# viewable tracks = tracks that have as frame #, the current frame
def generate_viewableTracks_row(i, value):
    global viewable_tracks_counter
    viewable_row = df[df["frame"] == value]
    viewable_tracks_counter += 1
    if viewable_tracks_counter == 3 or viewable_tracks_counter == 4:
        viewable_tracks_counter += 2

    return  dbc.Row(
                            dbc.Col([
                                dcc.Checklist(id= "checkbox"+str(i), options=[ {'label': ' ', 'value': 'false', 'disabled':False}, ], value=['true']),
                                dbc.Button(
                                    str(viewable_row.iloc[viewable_tracks_counter]['track_id']),
                                    id="collapse-button"+str(viewable_tracks_counter),
                                    className="mb-3",
                                    color="secondary",
                                    style={ "font-size": "12px"},
                                ),
                                dbc.Collapse(
                                    dbc.Card(dbc.CardBody([
                                    dbc.Row( dbc.Button("Modify Track: Go to Start("+str(viewable_tracks_counter)+")", color="black", style={ "font-size": "12px"}),),
                                    dbc.Row( dbc.Button("Delete Track: Go to End("+str(viewable_tracks_counter+1)+")", color="black", style={ "font-size": "12px"}),),
                                    ])),
                                    id="collapse"+str(viewable_tracks_counter),
                                    style={ "font-size": "12px"}
                                ),
                            ]))
# Viewable Track Component                            
# viewableTrackSection = html.Div([
#                             html.Div(children=[generate_viewableTracks_row(i, value) for i in range(1,7)]),
#                             ])

# Generate Function for ea/ track (player track)
def generate_playertracks_row(i):
    global player_tracks_counter
    player_tracks_counter += 1

    if player_tracks_counter == 3:
        player_tracks_counter += 2
    if player_tracks_counter == 4:
        player_tracks_counter += 2
    return dbc.Row(
        dbc.Col([
            dcc.Checklist(id="checkbox"+str(i), options=[
                          {'label': ' ', 'value': 'false', 'disabled': False}, ], value=['true']),
            dbc.Button(
                i,
                id="collbutt_playertrack" +
                str(player_tracks_counter),
                className="mb-3",
                color="secondary",
                style={"font-size": "12px"},
            ),
            dbc.Collapse(
                dbc.Card(dbc.CardBody([
                    dbc.Row(dbc.Button("Modify Track: Go to Start("+str(
                        player_tracks_counter)+")", color="black", style={"font-size": "12px"}),),
                    dbc.Row(dbc.Button("Delete Track: Go to End("+str(
                        player_tracks_counter+1)+")", color="black", style={"font-size": "12px"}),),
                ])),
                id="coll_playertrack" +
                str(player_tracks_counter),
                style={"font-size": "12px"}
            ),
        ]))

# Player Tracks Component
viewPlayerTracks = html.Div([
                            html.Div(children=[generate_playertracks_row(
                                i) for i in player_tracks]),
                            ])

# Navbar Component
navbar = dbc.NavbarSimple(
    children=[

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

# Card with video player
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
                    interval=500,
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
                # Slider Component
                dcc.Slider(
                    id='frame-slider',
                    min=0,
                    max=maxFrames,
                    value=0,
                    step=1,
                    marks={round(i*maxFrames/16): '{}'.format(round(i*maxFrames/16))
                           for i in range(maxFrames)},
                ),
                html.Div(id='slider-output-container'),
                # Pause/Player Buttons
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

# Card with Track Lists
annotated_data_card = dbc.Card(
    [
        dbc.CardHeader(html.Div(
            [
                dbc.Button("All Tracks", id="all_tracks_bt", outline=True, style={
                       "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("ViewableTracks", id="viewable_tracks_bt", outline=True, style={
                    "margin-right": "4px", "font-size": "12px"}),
                dbc.Button("Player Tracks", id="player_tracks_bt",
                           outline=True, style={"font-size": "12px"}),
            ])),
        dbc.CardBody(
            [
                html.Div(id='track_container')
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

# Card with PLayer Lists
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
                html.Div(id='container')
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

# App layout 
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

# Collapse Callback for player tracks collapses
# Create inputs

# @app.callback(
# [Output(f"coll_playertrack"+str(i),"is_open") for i in range(1, player_tracks_counter)],
# [Input(f"collbutt_playertrack"+str(i),"n_clicks") for i in range(1, player_tracks_counter)],
# [State(f"coll_playertrack"+str(i),"is_open") for i in range(1, player_tracks_counter)],
# )
# def toggle_collapse(n, is_open):
#     if n:
#         return not is_open
#     selected_track = df.iloc[0]['track_id']
#     return is_open


# Call Back for player Tracks
# 1
@app.callback(
    Output("coll_playertrack1", "is_open"),
    [Input("collbutt_playertrack1", "n_clicks")],
    [State("coll_playertrack1", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    selected_track = df.iloc[0]['track_id']
    return is_open
# 2
@app.callback(
    Output("coll_playertrack2", "is_open"),
    [Input("collbutt_playertrack2", "n_clicks")],
    [State("coll_playertrack2", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    selected_track = df.iloc[0]['track_id']
    return is_open

# Callback for all Tracks
@app.callback(
    Output("collapse1", "is_open"),
    [Input("collapse-button1", "n_clicks")],
    [State("collapse1", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    selected_track = df.iloc[0]['track_id']
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
    Output("collapse5", "is_open"),
    [Input("collapse-button5", "n_clicks")],
    [State("collapse5", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse6", "is_open"),
    [Input("collapse-button6", "n_clicks")],
    [State("collapse6", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse7", "is_open"),
    [Input("collapse-button7", "n_clicks")],
    [State("collapse7", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse8", "is_open"),
    [Input("collapse-button8", "n_clicks")],
    [State("collapse8", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse9", "is_open"),
    [Input("collapse-button9", "n_clicks")],
    [State("collapse9", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# Call back that toggles between Team A and Team B
@app.callback(Output('container', 'children'),
              Input("but7", 'n_clicks'),
              Input("but8", 'n_clicks'))
def display(btn1, btn2):

    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    updateSection(button_id)

    if button_id == "but7":
        return sectionA

    if button_id == "but8":
        return sectionB

    else:
        return "Select a Team"


# Callback that toggles between track buttons:
# all tracks, viewable tracks, player tracks
@app.callback(Output('track_container', 'children'),
              Input("all_tracks_bt", 'n_clicks'),
              Input("viewable_tracks_bt", 'n_clicks'),
              Input("player_tracks_bt", 'n_clicks'),
              Input("frame-slider", 'value'))
def display(btn1, btn2, btn3, value):
    ctx = dash.callback_context
    global current_frame

    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "all_tracks_bt":
        return allTrackSection

    if button_id == "viewable_tracks_bt":
        print("callback called")
        return html.Div(children=[generate_viewableTracks_row(i, value) for i in range(1,2)])
    if button_id == "player_tracks_bt":
        return viewPlayerTracks
    else:
        return "Select Tracks"


# Call back for video Player/Pause
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

# Video Display Callback
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
    currentFrame = 0

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

    fig = px.imshow(io.imread(pathIn+frames[currentFrame]), binary_backend="jpg") # OLD
    # fig = px.imshow(frames[currentFrame], binary_backend="jpg") # NEW
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

# Callback for Slider
# It also stores on the db the current frame slider
# ea/ time the slider is updated
@app.callback(
    dash.dependencies.Output('slider-output-container', 'children'),
    [dash.dependencies.Input('frame-slider', 'value')])
def update_output(value):
    # print("Start of the callback")
    # print("Start of the callback")
    # print("Start of the callback")
    conn = pg2.connect(database='soccerdb',
        user='postgres',
        host='localhost',  # localhost-------------------!
        password='root')
    cur = conn.cursor()
    cur.execute('''UPDATE variables SET frame = %s''' % value)
    conn.commit()
    cur.close()
    conn.close()
    # print("End of the callback")
    return 'Current Frame "{}"'.format(value)



# MAIN STARTS HERE -----------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    read_input()
    print("---Input done---")
    app.run_server()
