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
def get_players(game_id): # will need significant rework to find the players for each specific specific team
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    cur = conn.cursor()
    
    cur.execute('''SELECT * FROM player''')
    players_data = cur.fetchall()
    
    cur.close()
    conn.close() 
    
    pcols = []
    for elt in cur.description:
        pcols.append(elt[0])

    return pd.DataFrame(data=players_data, columns=pcols)

# ----------------------------------------------------------------------------

# assigning a track to a player
def assign_track(game_id, track_id, player_id):
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    cur = conn.cursor()
    
    # Query/Commit Here
    cur.execute('''UPDATE detections SET player_id = %s WHERE game_id = %s AND track_id = %s''', (player_id, game_id, track_id))
    
    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

# getting a player's tracks
def get_player_detections(game_id, player_id):
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    cur = conn.cursor()

    cur.execute('''SELECT * FROM detections WHERE game_id = %s AND player_id = %s''', (game_id, player_id))
    data = cur.fetchall()

    cols = []
    for elt in cur.description:
        cols.append(elt[0])
    
    cur.close()
    conn.close()

    return(data, cols)

# ----------------------------------------------------------------------------

def get_initials(player_id):
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    cur = conn.cursor()
    
    # Query/Commit Here
    cur.execute('''SELECT initials FROM players WHERE player_id={}'''.format(player_id))
    initials = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()

    return initials


# max = cur1.fetchone()[0]