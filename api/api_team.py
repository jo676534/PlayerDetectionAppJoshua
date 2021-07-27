import pandas as pd
import psycopg2 as pg2
import pandas as pd
# GET FUNCTIONS
def get_teams(game_id): # will need significant rework to find the two specific teams
    conn = pg2.connect(database='soccer', user='postgres', host='localhost', password='brendan')
    cur = conn.cursor()
    
    cur.execute('''SELECT * FROM team''')
    teams_data = cur.fetchall()
    
    cur.close()
    conn.close() 
    
    tcols = []
    for elt in cur.description:
        tcols.append(elt[0])

    return pd.DataFrame(data=teams_data, columns=tcols)



