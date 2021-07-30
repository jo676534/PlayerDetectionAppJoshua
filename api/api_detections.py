import pandas as pd
import psycopg2 as pg2

# database name is soccer
# password is rootroot
# username is postgres
# host is database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com

def get_detection_data(game_id, start, end):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot') # ctrl + d
    cur = conn.cursor()

    cur.execute(f'''SELECT * FROM detections WHERE game_id={game_id} AND frame>={start} AND frame<={end}''') # fstrings confirmed to work
    data = cur.fetchall()

    cols = []
    for elt in cur.description: cols.append(elt[0])
    
    df = pd.DataFrame(data=data, columns=cols, dtype=object)
    
    return df

# ----------------------------------------------------------------------------

def save_track(game_id, detections_df, frame, track_id, player_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    for index, det in detections_df.iterrows():
        cur.execute(f'''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id) VALUES ({game_id}, {frame}, {det['x0']}, {det['y0']}, {det['x1']}, {det['y1']}, {track_id}, {player_id})''')
        frame += 1

    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

def unique_track_id(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    cur.execute(f'''SELECT MAX(track_id) FROM detections WHERE game_id={game_id}''') # fstrings confirmed to work
    data = cur.fetchall()

    cur.close()
    conn.close()

    return data[0][0] + 1

# ----------------------------------------------------------------------------

def delete_detection(game_id, frame, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    cur.execute(f'''DELETE FROM detections WHERE game_id={game_id} AND frame={frame} AND track_id={track_id}''')
    
    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

def delete_detection_section(game_id, start_frame, final_frame, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    cur.execute(f'''DELETE FROM detections WHERE game_id={game_id} AND track_id={track_id} AND frame >= {start_frame} AND frame <= {final_frame}''')
    
    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

def delete_detection_list(game_id, track_id, arr):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()

    st = set(arr)
    cur.execute(f'''DELETE FROM detections WHERE game_id={game_id} AND track_id={track_id} AND frame=ANY('{st}')''')

    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

def add_detection(game_id, frame, x0, y0, x1, y1, track_id, player_id, initials):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')  
    cur = conn.cursor()
    
    # fstrings don't work here for some reason # cur.execute(f'''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id, initials) VALUES ({game_id}, {frame}, {x0}, {y0}, {x1}, {y1}, {track_id}, {player_id}, {initials})''')
    cur.execute('''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id, initials) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', (game_id, frame, x0, y0, x1, y1, track_id, player_id, initials))

    cur.close()
    conn.commit()
    conn.close()

# ----------------------------------------------------------------------------

def get_player_initials(player_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    
    cur1 = conn.cursor()
    cur1.execute(f'''SELECT initials FROM player WHERE player_id={player_id}''')
    initials = cur1.fetchone()[0]
    cur1.close()

    conn.commit()
    conn.close()
    
    return initials

# ----------------------------------------------------------------------------

def get_partial_frame_detections(game_id, start_frame, final_frame):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()

    cur.execute('''SELECT MAX(frame) FROM detections''')
    maxFrame = cur.fetchone()[0]
    
    dic = {}
    frame = start_frame

    while frame <= final_frame:
        cur_temp = conn.cursor()
        cur_temp.execute(f'''SELECT * FROM detections WHERE game_id={game_id} AND frame={frame}''')
        data = cur_temp.fetchall()
        
        cols = []
        for elt in cur_temp.description:
            cols.append(elt[0])
        
        dic[frame] = pd.DataFrame(data=data, columns=cols)

        cur_temp.close()
        frame += 1
    
    cur.close()
    conn.close()
    
    return dic

# ----------------------------------------------------------------------------

def assign_track(game_id, player_id, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')

    cur1 = conn.cursor()
    cur1.execute(f'''SELECT initials FROM player WHERE player_id={player_id}''')
    initials = cur1.fetchone()[0]
    cur1.close()

    cur = conn.cursor()
    cur.execute('''UPDATE detections SET player_id=%s, initials=%s WHERE track_id=%s AND game_id=%s''', (player_id, initials, track_id, game_id))

    conn.commit()
    cur.close()
    conn.close()
# ----------------------------------------------------------------------------

def unassign_track(game_id, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')

    cur = conn.cursor()
    cur.execute(f'''UPDATE detections SET player_id=-1 WHERE track_id={track_id} AND game_id={game_id}''')

    conn.commit()
    cur.close()
    conn.close()



# ----------------------------------------------------------------------------

def delete_track(game_id, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    cur.execute(f'''DELETE FROM detections WHERE track_id={track_id} and game_id={game_id}''')
    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

def get_player_frames(game_id, player_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    cur.execute('''SELECT frame FROM detections WHERE game_id=%s AND player_id=%s''', (game_id, player_id))
    data = cur.fetchall()
        
    cols = []
    for elt in cur.description:
        cols.append(elt[0])
        
    df = pd.DataFrame(data=data, columns=cols)

    frame_list = df['frame'].tolist()

    cur.close()
    conn.close()
    
    return frame_list

# ----------------------------------------------------------------------------

def get_track_frames(game_id, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    cur.execute(f'''SELECT frame FROM detections WHERE game_id={game_id} AND track_id={track_id}''')
    data = cur.fetchall()
        
    cols = []
    for elt in cur.description:
        cols.append(elt[0])
        
    df = pd.DataFrame(data=data, columns=cols)

    frame_list = df['frame'].tolist()

    cur.close()
    conn.close()
    
    return frame_list

# ----------------------------------------------------------------------------

def example_endpoint_framework(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    # Query/Commit Here
    
    cur.close()
    conn.close()
    
    # Return Here