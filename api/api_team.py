import pandas as pd
import psycopg2 as pg2
import pandas as pd

database = "soccer"
user = "postgres"
host = "database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com"
password = "rootroot"

# GET FUNCTIONS
def get_teams():  # will need significant rework to find the two specific teams
    conn = pg2.connect(database=database, user=user, host=host, password=password)
    cur = conn.cursor()

    cur.execute("""SELECT * FROM team""")
    teams_data = cur.fetchall()

    cur.close()
    conn.close()

    tcols = []
    for elt in cur.description:
        tcols.append(elt[0])

    return pd.DataFrame(data=teams_data, columns=tcols)


def get_new_team_id():
    conn = pg2.connect(
        database="soccer",
        user="postgres",
        host="database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com",
        password="rootroot",
    )
    cur = conn.cursor()

    cur.execute("""SELECT MAX(team_id) FROM team""")
    new_id = int(cur.fetchone()[0]) + 1

    cur.close()
    conn.close()

    return new_id


def create_new_team(team_id, team_name):
    conn = pg2.connect(
        database="soccer",
        user="postgres",
        host="database-1.cbumbixir8o8.us-east-1.rds.amazonaws.com",
        password="rootroot",
    )
    cur = conn.cursor()

    cur.execute(
        """INSERT INTO team (team_id, name) VALUES (%s, %s)""", (team_id, team_name)
    )

    conn.commit()
    cur.close()
    conn.close()
