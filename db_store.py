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
import psycopg2


# FUNCTION DEFINITIONS ------------------------------------------------------------------------------------------------------------------------


dic = {}

def read_input():
    for i in range(maxFrames):
        fp = open("./detections/f" + str(i) + ".txt", "r") # grab new file
        df = read_file(fp, i)
        print("Finished frame #", i)
        dic[i] = df
        
    
def read_file(fp, frame): # returns complete dataframe
    df = pd.DataFrame([], columns = ['id', 'x0', 'y0', 'x1', 'y1'])
    fp.read(16) # get rid of dummy inputs
    for line in fp: # loop for the rest of the inputs
        start, end = line.split("[")
        nums, garbage = end.split("]")
        garbage2, id_num = garbage.split(":")
        
        x, y, w, h = nums.split()
        x0 = float(x)
        y0 = float(y)
        x1 = x0 + float(w)
        y1 = y0 + float(h)
        
        df_temp = pd.DataFrame([[int(id_num), x0, y0, x1, y1]], columns = ['id', 'x0', 'y0', 'x1', 'y1'])
        df = df.append(df_temp)
        
        # could put the storage function here
        db_insert(x0, y0, x1, y1, int(id_num), frame)
        
    return df

def db_insert(x0, y0, x1, y1, trackid, frame):
    sql = "INSERT INTO detections(game_id, frame, x0, y0, x1, y1, track_id, player_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);"
    try:
        cur.execute(sql, (0, frame, x0, y0, x1, y1, trackid, -1))
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)




#Start of "main"
print("Start of database program. This may take a moment.")

try:
    #Set up connections
    conn = psycopg2.connect(host="localhost", database="soccer", user="postgres", password="root")
    cur = conn.cursor()
    print("Successful Connection")
    
    pathIn = './vid2img/'
    frames = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))] 
    frames.sort(key=lambda x: int(x[5:-4]))
    maxFrames = len(frames)
    
    read_input()
    conn.commit()
    cur.close()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()
        print("Connections closed")

print("End of database program.")

