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


# GET FUNCTIONS

# Get All Game Detections
def get_game_detections(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    cur = conn.cursor()
    
    cur.execute('''SELECT * FROM detections''')
    data = cur.fetchall()
    
    cur.close()
    conn.close()
    
    cols = []
    for elt in cur.description:
        cols.append(elt[0])

    return pd.DataFrame(data=data, columns=cols)


# ----------------------------------------------------------------------------

# Get All Detections From a Frame
def get_frame_detections(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    cur = conn.cursor()
    
    cur.execute('''SELECT MAX(frame) FROM detections''')
    maxFrame = cur.fetchone()[0]
    
    dic = {}
    
    for frame in range(maxFrame+1):
        # create a temporary cursor and execute the get request for the detections of this frame
        cur_temp = conn.cursor()
        cur_temp.execute('''SELECT * FROM detections WHERE game_id=0 AND frame={0}'''.format(frame))
        data = cur_temp.fetchall()
        
        cols = []
        for elt in cur_temp.description:
            cols.append(elt[0])
        
        dic[frame] = pd.DataFrame(data=data, columns=cols)
        cur_temp.close()
    
    cur.close()
    conn.close()
    
    return dic

# ----------------------------------------------------------------------------

def get_tracks(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    
    cur = conn.cursor()
    cur.execute('''SELECT MAX(track_id) FROM detections WHERE game_id={0}'''.format(game_id))
    maxTrack = cur.fetchone()[0]
    cur.close()
    
    cur = conn.cursor()
    cur.execute('''SELECT COUNT(DISTINCT track_id) FROM detections WHERE game_id={0}'''.format(game_id))
    unique_tracks = cur.fetchone()[0]
    cur.close()
    
    dic = {}
    
    for track_id in range(maxTrack):
        # create a temporary cursor and execute the get request for the detections of this frame
        cur_temp = conn.cursor()
        cur_temp.execute('''SELECT * FROM detections WHERE game_id={0} AND track_id={1}'''.format(game_id, track_id))
        data = cur_temp.fetchall()
        
        cols = []
        for elt in cur_temp.description:
            cols.append(elt[0])
        
        dic[track_id] = pd.DataFrame(data=data, columns=cols)
        cur_temp.close()
    
    cur.close()
    conn.close()
    
    return dic, unique_tracks

# ----------------------------------------------------------------------------

def save_track(game_id, detections_df, frame, player_id, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    cur = conn.cursor()
    
    # Query/Commit Here
    for det in detections_df:
        cur.execute('''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})'''.format(game_id, frame, det.x0, det.y0, det.x1, det.y1, track_id, player_id))
        frame += 1

    cur.close()
    conn.close()
    
    # Return Here

# ----------------------------------------------------------------------------

def endpoint_framework(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    cur = conn.cursor()
    
    # Query/Commit Here
    
    cur.close()
    conn.close()
    
    # Return Here