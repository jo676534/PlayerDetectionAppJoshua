import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
import dash_table
import requests
from dash.exceptions import PreventUpdate
from app import app


completed_requests = html.Div(
    children=[
        dbc.CardHeader(
            children=[
                dbc.Label(
                    children="Completed Requests:",
                    style={"display": "inline-block", "margin-right": "150px"},
                ),
                dbc.Button(
                    id="go_to_search_engine",
                    children="Go to Search Engine",
                    color="success",
                ),
            ]
        ),
        dbc.CardBody(
            children=[
                dash_table.DataTable(
                    id="completed_games_table",
                    columns=[
                        {"name": "Completed on", "id": "your_game_completed_id"},
                        {"name": "Your Team", "id": "your_team_completed_id"},
                        {"name": "Your Opponent", "id": "opponent_completed_id"},
                        {"name": "View", "id": "view_match_completed_id"},
                    ],
                    page_current=0,
                    page_size=5,
                    style_as_list_view=True,
                    style_cell={
                        "padding-left": "5px",
                        "font_family": "Helvetica",
                    },
                    style_header={
                        "backgroundColor": "#000e44",
                        "fontWeight": "bold",
                        "color": "#00c2cb",
                    },
                ),
            ]
        ),
    ]
)


pending_request_card = html.Div(
    children=[
        dbc.CardHeader(
            children=[
                dbc.Label(
                    children="Pending Requests:",
                    style={"display": "inline-block", "margin-right": "100px"},
                ),
                dbc.Button(
                    id="new_request",
                    children="New Request",
                    color="primary",
                    href="/apps/upload",
                    style={"display": "inline-block", "margin-right": "10px"},
                ),
                dbc.Button(id="refresh_table", children="Refresh Table?", size="sm"),
            ]
        ),
        dbc.CardBody(
            children=[
                dash_table.DataTable(
                    id="pending_games_table",
                    columns=[
                        {"name": "Submitted on", "id": "game_requests_id"},
                        {"name": "Your Team", "id": "your_team_requests_id"},
                        {"name": "Your Opponent", "id": "your_opponent_id"},
                        {"name": "Stage", "id": "stage_request_id"},
                    ],
                    page_current=0,
                    page_size=5,
                    style_as_list_view=True,
                    style_cell={
                        "padding-left": "5px",
                        "font_family": "Helvetica",
                    },
                    style_header={
                        "backgroundColor": "#000e44",
                        "fontWeight": "bold",
                        "color": "#00c2cb",
                    },
                ),
            ]
        ),
    ]
)


dropdown_inside_header = dcc.Dropdown(
    id="view_select_team",
    options=[{"label": "N/A", "value": -1}],
    style={
        "width": "90%",
        "display": "inline-block",
    },
)

look_at_your_team_container = html.Div(
    children=[
        dbc.CardHeader(
            [
                dropdown_inside_header,
            ]
        ),
        dbc.CardBody(
            children=[
                dash_table.DataTable(
                    id="team_information_table",
                    columns=[
                        {"name": "Player ID", "id": "player_id_id"},
                        {"name": "Player Name", "id": "player_name_id"},
                        {"name": "Jersey Number", "id": "jersey_number_id"},
                        {"name": "Team ID", "id": "team_id_id"},
                    ],
                    page_current=0,
                    page_size=5,
                    style_as_list_view=True,
                    style_cell={
                        "padding-left": "5px",
                        "font_family": "Helvetica",
                    },
                    style_header={
                        "backgroundColor": "#000e44",
                        "fontWeight": "bold",
                        "color": "#00c2cb",
                    },
                ),
            ]
        ),
    ]
)


card_inside = dbc.Row(
    [
        dbc.Col(dbc.Card(completed_requests, color="dark", outline=True)),
        dbc.Col(dbc.Card(pending_request_card, color="dark", outline=True)),
    ]
)


main_card = dbc.Card(
    id="main_card_coach",
    children=[
        dbc.CardHeader(
            children=html.H3(
                children="Welcome to Sports Science AI!", style={"text-align": "center"}
            )
        ),
        dbc.CardBody([card_inside, html.Br(), look_at_your_team_container]),
    ],
    outline=True,
    color="dark",
)


layout = html.Div(
    children=main_card,
    style={"padding-top": "50px", "padding-left": "50px", "padding-right": "50px"},
)


def get_request(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        r = requests.get("http://127.0.0.1:5000/get")

        data = r.json()

        print(data)
        return "worked"
