import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_player as player
from app import app

video_card_IR = dbc.Card(
    children=[
        dbc.CardHeader(
            html.Div(
                [
                    dbc.Row(
                    children=[
                        html.Div(
                            [
                                html.H1('Initial Review')
                            ],
                            # style={"width": "20%", 'margin-left': '10px',
                            #        'font-size': '14px'},
                        )])
                 ], style={"margin-bottom": "0px"}
            ),
            className="player_card_header",
        ),
        dbc.CardBody(
            [
                player.DashPlayer(
                    id='video-player',
                    url='https://mainbucketsd2.s3.amazonaws.com/Sample+Soccer+Video.mp4',
                    controls=True,
                    height='100%',
                    width='100%'
                )
            ]
        ),
        dbc.CardFooter(
            dbc.ButtonGroup(
                [
                    dbc.Button('Deny Video', id='deny-video',
                            size="md", color="danger",),
                    dbc.Modal(
                        [
                            dbc.ModalHeader("Deny Video"),
                            dbc.ModalBody(
                                "Denying the video will delete the video entry and its corresponding data. Are you sure you want to continue?"
                            ),
                            dbc.ModalFooter(
                                children=[
                                    dbc.Button(
                                        "Back",
                                        id="deny-back-modal",
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        "Continue",
                                        id="deny-continue-modal",
                                        n_clicks=0,
                                    ),
                                ]
                            ),
                        ], 
                        id="deny-modal",
                        is_open=False,
                        backdrop='static',
                    ), 
                    dbc.Button('Accept Video',
                            id='accept-video', size="md",),
                    dbc.Modal(
                        [
                            dbc.ModalHeader("Accept Video"),
                            dbc.ModalBody(
                                "Accepting the video will begin the preprocessing state of converting the video to 15 FPS. Are you sure you want to continue?"
                            ),
                            dbc.ModalFooter(
                                children=[
                                    dbc.Button(
                                        "Back",
                                        id="accept-back-modal",
                                        n_clicks=0,
                                    ),
                                    dbc.Button(
                                        "Continue",
                                        id="accept-continue-modal",
                                        n_clicks=0,
                                    ),
                                ]
                            ),
                        ], 
                        id="accept-modal",
                        is_open=False,
                        backdrop='static',
                    ), 
                    
                ],
                style={"width": "100%"},
            ),
        )
    ],
    style={"margin-left": "5px", "margin-top": "20px",
           "margin-bottom": "20px", "margin-right": "10px"}
)


layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(video_card_IR, md=8),
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)

@app.callback(
    Output("deny-modal", "is_open"),
    [Input("deny-video", "n_clicks"), Input("deny-back-modal", "n_clicks"), Input("deny-continue-modal", "n_clicks")],
    [State("deny-modal", "is_open")],
)
def toggle_deny_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open

@app.callback(
    Output("accept-modal", "is_open"),
    [Input("accept-video", "n_clicks"), Input("accept-back-modal", "n_clicks"), Input("accept-continue-modal", "n_clicks")],
    [State("accept-modal", "is_open")],
)
def toggle_accept_modal(n1, n2, n3, is_open):
    if n1 or n2 or n3:
        return not is_open
    return is_open
