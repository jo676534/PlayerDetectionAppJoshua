import pandas as pd
import psycopg2 as pg2

database = 'soccer'
user = 'postgres'
host = 'database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com'
password = 'rootroot'

# GET FUNCTIONS
def get_players():
    conn = pg2.connect(database=database, user=user, host=host, password=password)
    cur = conn.cursor()
    
    cur.execute('''SELECT * FROM player''')
    players_data = cur.fetchall()
    
    cur.close()
    conn.close() 
    
    pcols = []
    for elt in cur.description:
        pcols.append(elt[0])

    return pd.DataFrame(data=players_data, columns=pcols)


def get_players_roster(game_id):
    conn = pg2.connect(database=database, user=user, host=host, password=password)
    cur = conn.cursor()
        
    cur.execute(f'''SELECT * FROM roster WHERE game_id={game_id}''')
    players_data = cur.fetchall()
        
    cur.close()
    conn.close() 
        
    pcols = []
    for elt in cur.description:
        pcols.append(elt[0])

    return pd.DataFrame(data=players_data, columns=pcols)


# ----------------------------------------------------------------------------

def get_player(game_id, player_id):
    conn = pg2.connect(database=database, user=user, host=host, password=password)
    cur = conn.cursor()
    
    cur.execute(f'''SELECT * FROM roster where game_id={game_id} and player_id={player_id}''')
    players_data = cur.fetchall()
    
    cur.close()
    conn.close() 
    
    pcols = []
    for elt in cur.description:
        pcols.append(elt[0])

    return pd.DataFrame(data=players_data, columns=pcols)

# ----------------------------------------------------------------------------

# assigning a track to a player
# USE the one in api_detections instead
def assign_track(game_id, track_id, player_id):
    conn = pg2.connect(database=database, user=user, host=host, password=password)
    cur = conn.cursor()
    
    # Query/Commit Here
    cur.execute(f'''UPDATE detections SET player_id={player_id} WHERE game_id={game_id} AND track_id ={track_id}''')
    
    conn.commit()
    cur.close()
    conn.close()

# ----------------------------------------------------------------------------

# getting a player's tracks
def get_player_detections(game_id, player_id):
    conn = pg2.connect(database=database, user=user, host=host, password=password)
    cur = conn.cursor()

    cur.execute(f'''SELECT * FROM detections WHERE game_id={game_id} AND player_id={player_id}''')
    data = cur.fetchall()

    cols = []
    for elt in cur.description:
        cols.append(elt[0])
    
    cur.close()
    conn.close()

    return(data, cols)

# ----------------------------------------------------------------------------

def get_initials(player_id):
    conn = pg2.connect(database=database, user=user, host=host, password=password)
    cur = conn.cursor()
    
    # Query/Commit Here
    cur.execute(f'''SELECT initials FROM players WHERE player_id={player_id}''')
    initials = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()

    return initials


# max = cur1.fetchone()[0]