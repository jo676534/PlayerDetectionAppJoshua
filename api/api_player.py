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
