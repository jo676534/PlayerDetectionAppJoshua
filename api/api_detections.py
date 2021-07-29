import pandas as pd
import psycopg2 as pg2
import pandas as pd


# Get All Game Detections
def get_game_detections(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    cur.execute(f'''SELECT * FROM detections where game_id={game_id}''')
    data = cur.fetchall()
    
    cur.close()
    conn.close()
    
    cols = []
    for elt in cur.description:
        cols.append(elt[0])

    return pd.DataFrame(data=data, columns=cols)

# ----------------------------------------------------------------------------

# database name is soccer
# password is rootroot
# username is postgres
# host is database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com

# Get All Detections From a Frame
def get_frame_detections(game_id, start, end):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    # cur.execute(f'''SELECT MAX(frame) FROM detections where game_id={game_id}''')
    # maxFrame = cur.fetchone()[0]
    

    dic = {}
    

    from tqdm import tqdm 
    print(f'grabbing frames {start} to {end} from database:')
    for frame in tqdm(range(start, end+1)):
        
        # create a temporary cursor and execute the get request for the detections of this frame
        cur_temp = conn.cursor()
        cur_temp.execute(f'''SELECT * FROM detections WHERE game_id={game_id} AND frame={frame}''')
        data = cur_temp.fetchall()
        
        cols = []
        for elt in cur_temp.description:
            cols.append(elt[0])
        
        dic[frame] = pd.DataFrame(data=data, columns=cols)
        cur_temp.close()
    
    cur.close()
    conn.close()

    # game_id = 0 

    # dic = {} 

    # with con:
    #     with con.cursor() as curs:
    #             sql = f'SELECT * FROM detections WHERE game_id={game_id}'
    #             curs.execute(sql)
    #             rows = curs.fetchall()
    #             rows.sort(key = lambda x: x[1])

    #             cols = []
    #             for elt in curs.description:
    #                 cols.append(elt[0])

    #             for i in rows: # i[1] is just frame number
    #                 # print("Fetching frame data {} of {}".format(i, len(rows)))
    #                 l = [[i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8]]]
    #                 if i[1] in dic: 
    #                     df = dic[i[1]]
    #                     df2 = pd.DataFrame(data=l, columns=cols)
    #                     dic[i[1]] = df.append(df2)
    #                 else: 
    #                     dic[i[1]] = pd.DataFrame(data=l, columns=cols) # [l]
    
    return dic


def gfd(game_id, frame):
    con = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')

    with con:
        with con.cursor() as curs:
            curs.execute(f'''SELECT * FROM detections WHERE game_id={game_id} AND frame={frame}''')
            data = curs.fetchall()
            
            cols = []
            for elt in curs.description:
                cols.append(elt[0])
            
            return pd.DataFrame(data=data, columns=cols)

# ----------------------------------------------------------------------------

def get_tracks(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')

    cur = conn.cursor()
    cur.execute(f'''SELECT MAX(track_id) FROM detections WHERE game_id={game_id}''')
    maxTrack = cur.fetchone()[0]
    cur.close()

    cur = conn.cursor()
    cur.execute(f'''SELECT COUNT(DISTINCT track_id) FROM detections WHERE game_id={game_id}''')
    unique_tracks = cur.fetchone()[0]
    cur.close()

    dic = {}
    ctr = 0

    for track_id in range(maxTrack+1):
        # create a temporary cursor and execute the get request for the detections of this frame
        # print("Fetching track {} of {}".format(track_id, maxTrack))
        cur_temp = conn.cursor()
        cur_temp.execute(f'''SELECT * FROM detections WHERE game_id={game_id} AND track_id={track_id}''')
        data = cur_temp.fetchall()

        if data:
            cols = []
            for elt in cur_temp.description:
                cols.append(elt[0])

            dic[ctr] = pd.DataFrame(data=data, columns=cols)
            ctr += 1

        cur_temp.close()

    cur.close()
    conn.close()

    return dic, len(dic)

# ----------------------------------------------------------------------------

def save_track(game_id, detections_df, frame, track_id, player_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    # Query/Commit Here
    for index, det in detections_df.iterrows():
        # cur.execute('''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})'''.format(game_id, frame, det['x0'], det['y0'], det['x1'], det['y1'], track_id, player_id))
        cur.execute(f'''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id) VALUES ({game_id}, {frame}, {det['x0']}, {det['y0']}, {det['x1']}, {det['y1']}, {track_id}, {player_id})''')
        #print('''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})'''.format(game_id, frame, det['x0'], det['y0'], det['x1'], det['y1'], track_id, player_id))
        frame += 1

    conn.commit()
    cur.close()
    conn.close()
    
    # Return Here

# ----------------------------------------------------------------------------

def unique_track_id(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    # Query/Commit Here
    cur.execute(f'''SELECT MAX(track_id) FROM detections WHERE game_id={game_id}''')
    data = cur.fetchall()

    cur.close()
    conn.close()
    
    # Return Here
    return data[0][0] + 1

# ----------------------------------------------------------------------------

def delete_detection(game_id, frame, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    # Query/Commit Here
    cur.execute(f'''DELETE FROM detections WHERE game_id={game_id} AND frame={frame} AND track_id={track_id}''')
    
    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

def delete_detection_section(game_id, start_frame, final_frame, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    # Query/Commit Here
    cur.execute(f'''DELETE FROM detections WHERE game_id={game_id} AND track_id={track_id} AND frame >= {start_frame} AND frame <= {final_frame}''')
    
    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

def delete_detection_list(game_id, track_id, arr):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()

    print("4")

    st = set(arr)
    
    print("5")

    # Query/Commit Here
    cur.execute(f'''DELETE FROM detections WHERE game_id={game_id} AND track_id={track_id} AND frame=ANY('{st}')''')
    #cur.execute('''SELECT * FROM detections WHERE game_id=0 AND frame=ANY('{0}')'''.format(st))

    print("6")

    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

def add_detection(game_id, frame, x0, y0, x1, y1, track_id, player_id, initials):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    
    # cur1 = conn.cursor()
    # cur1.execute('''SELECT initials FROM player WHERE player_id={0}'''.format(player_id))
    # initials = cur1.fetchone()[0]
    # cur1.close()
    
    # print("A")
    # print(initials)
    # initials = str(initials)

    cur = conn.cursor()
    # cur.execute('''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id, initials) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})'''.format(game_id, frame, x0, y0, x1, y1, track_id, player_id, initials))
    # cur.execute('''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id, initials) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', (game_id, frame, x0, y0, x1, y1, track_id, player_id, initials))
    cur.execute(f'''INSERT INTO detections (game_id, frame, x0, y0, x1, y1, track_id, player_id, initials) VALUES ({game_id}, {frame}, {x0}, {y0}, {x1}, {y1}, {track_id}, {player_id}, {initials})''')
    cur.close()

    print("B")

    # cur2 = conn.cursor()
    # cur2.execute('''UPDATE detections SET initials = {0} WHERE game_id={1} AND frame={2} AND track_id={3}'''.format(initials, game_id, frame, track_id))
    # cur2.close()

    print("C")

    conn.commit()
    
    conn.close()
    
    # Return Here

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
    cur.execute(f'''UPDATE detections SET player_id={player_id}, initials={initials} WHERE track_id={track_id} AND game_id={game_id}''')

    conn.commit()
    cur.close()
    conn.close()
    
    # Return Here

# ----------------------------------------------------------------------------

def delete_track(game_id, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    cur.execute(f'''DELETE FROM detections WHERE track_id={track_id} and game_id={game_id}''')
    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

def min_max_track_frame(game_id, track_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur1 = conn.cursor()
    cur2 = conn.cursor()
    
    cur1.execute(f'''SELECT MAX(frame) FROM detections WHERE track_id={track_id} and game_id={game_id}''')
    max = cur1.fetchone()[0]
    
    cur2.execute(f'''SELECT MIN(frame) FROM detections WHERE track_id={track_id} and game_id={game_id}''')
    min = cur2.fetchone()[0]

    cur1.close()
    cur2.close()
    conn.close()
    
    return max, min

# ----------------------------------------------------------------------------

def get_player_frames(game_id, player_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    cur.execute(f'''SELECT frame FROM detections WHERE game_id={game_id} AND player_id={player_id}''')
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

def endpoint_framework(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()
    
    # Query/Commit Here
    
    cur.close()
    conn.close()
    
    # Return Here