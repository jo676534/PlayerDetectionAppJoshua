import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL


import dash_player as player

video_card_VE = dbc.Card(
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
                            href='/apps/home', size="md", color="danger",),
                    dbc.Button('Accept Video',
                            id='accept-video', size="md",),
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
                        dbc.Col(video_card_VE, md=8),
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)
