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

def get_unfinished_games():
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='root')
    cur = conn.cursor()
    
    cur.execute('''SELECT * FROM game WHERE process_state < 7''')
    data = cur.fetchall()
        
    cols = []
    for elt in cur.description:
        cols.append(elt[0])
        
    df = pd.DataFrame(data=data, columns=cols)
    
    cur.close()
    conn.close()
    
    return df

def get_team_names(game_id):
     # Team Names
    conn = pg2.connect(database='soccer',
            user='postgres',
            host='localhost',  # localhost-------------------!
            password='root')
    cur = conn.cursor()
    cur.execute(f'''SELECT * FROM game WHERE game_id={game_id}''')
    data = cur.fetchall()

    cols = []
    for elt in cur.description:
        cols.append(elt[0])

    conn.commit()
    cur.close()
    conn.close()

    game = pd.DataFrame(data=data, columns=cols)
    a_name = game.iloc[0]["team1_name"]
    b_name = game.iloc[0]["team2_name"]

    return a_name, b_name