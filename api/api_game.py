import pandas as pd
import psycopg2 as pg2

def get_unfinished_games():
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
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
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
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


def get_team_ids(game_id):
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
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
    a_id = game.iloc[0]["team1_id"]
    b_id = game.iloc[0]["team2_id"]

    return a_id, b_id


def get_new_game_id():
    conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
    cur = conn.cursor()

    cur.execute('''SELECT MAX(game_id) FROM game''')
    new_id = int(cur.fetchone()[0]) + 1
    
    cur.close()
    conn.close()
    
    return new_id


# conn = pg2.connect(database='soccer', user='postgres', host='database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com', password='rootroot')
# cur = conn.cursor()
# cur.execute('''UPDATE game SET process_state=%s WHERE game_id=%s''', (str(4), game_id)) # 4 for the start of the algo, 5 for the end of the algo
# conn.commit()
# cur.close()
# conn.close()