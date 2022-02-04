# Imports
from http import server
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from matplotlib import use


# Connect to main app.py file
from app import app
# from app import server

# Connect apps here
from apps import home
from apps import initial_review
from apps import video_edit
from apps import dashboard
from apps import add_track
from apps import upload
from apps import login
from apps import sign_up_coach
from apps import sign_up_sportscience
from apps import forgot_password
from apps import coach_home

#from flask_login import LoginManager, UserMixin, login_fresh, logout_user, login_user, current_user
#from dash_flask_login import FlaskLoginAuth
# ------------------------------------------------------------------

""" login_manager = LoginManager()
login_manager.init_app(flask_server)
login_manager.login_view = '/apps/login'


a_user = {'foo@bar.tld':{'password':'Ricardo@1020'}} """


""" global_username = None

@login_manager.user_loader
def load_user(username):

    global_username = login.User(username=username)
    #loads the user from aws
    #authenticate the user from aws
    #logic...
    #return User.get_id(login.User(username=username,password=password))
    return login.User(username)


@flask_server.route('/login',methods=['GET','POST'])
def login():
    return '' """
# ------------------------------------------------------------------



# make a reuseable dropdown for the different examples
""" dropdown = dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(dcc.Link('Home', href='/apps/home')),
                dbc.DropdownMenuItem(dcc.Link('Initial Review', href='/apps/initial_review')),
                dbc.DropdownMenuItem(dcc.Link('Video Editor', href='/apps/video_edit')),
                dbc.DropdownMenuItem(dcc.Link('Dashboard', href='/apps/dashboard')),
                dbc.DropdownMenuItem(dcc.Link('Add Track', href='/apps/add_track')),
                # dbc.DropdownMenuItem(dcc.Link('Upload', href='/apps/upload')),
            ],
            nav=True,
            in_navbar=True,
            label="HOME",
        ),
 """
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            id="logo",
                            src='https://github.com/dianabisbe/Images/blob/main/SportScienceLogo.png?raw=true',
                            height="30px",
                        ),
                        md="auto",
                    ),
                ],
                align="center",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.NavbarToggler(id="navbar-toggler"),
                            dbc.Collapse(
                                dbc.Nav(
                                    [
                                       dbc.DropdownMenu(
                                                children=[
                                                    dbc.DropdownMenuItem(dcc.Link('Home', href='/apps/home')),
                                                    dbc.DropdownMenuItem(dcc.Link('Initial Review', href='/apps/initial_review')),
                                                    dbc.DropdownMenuItem(dcc.Link('Video Editor', href='/apps/video_edit')),
                                                    dbc.DropdownMenuItem(dcc.Link('Dashboard', href='/apps/dashboard')),
                                                    dbc.DropdownMenuItem(dcc.Link('Add Track', href='/apps/add_track')),
                                                    dbc.DropdownMenuItem(dcc.Link('Upload', href='/apps/upload')),
                                                ],
                                                nav=True,
                                                in_navbar=True,
                                                label="HOME",
                                                direction="left"
                                            ),
                                    ],
                                    navbar=True,
                                ),
                                id="navbar-collapse",
                                navbar=True,
                            ),
                        ],
                        md=2,
                    ),
                ],
                align="center",
            ),
        ],
        fluid=True,
    ),
    dark=True,
    color="#000e44",
    sticky="top",
)

info_storage = html.Div([
    dcc.Store(id="game_id", storage_type='session', data=0),
    dcc.Store(id="video_path", storage_type='session'),
    dcc.Store(id='start_frame_add', storage_type='session'),
    dcc.Store(id='final_frame_add', storage_type='session'),
    dcc.Store(id='player_id_add', storage_type='session'),

    #dcc.Store(id='login-status',storage_type='session')
])







app.layout = html.Div(
    children = [
        dcc.Location(id='url', refresh=False),
        navbar,
        html.Div(id='page-content', children=[], style= {'height':'100%'}),
        info_storage,
    ])






@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):


    if pathname == '/apps/home':
            return home.layout

  
    if pathname == '/apps/initial_review':
            return initial_review.layout
  
       
    
    if pathname == '/apps/video_edit':
            return video_edit.layout

    if pathname == '/apps/coach_home':
        return coach_home.layout

    if pathname == '/apps/dashboard':
        return dashboard.layout

    if pathname == '/apps/add_track':
        return add_track.layout

    if pathname == '/apps/upload':
        return upload.layout
    
    if pathname == '/apps/sign_up_coach':
        return sign_up_coach.layout
    if pathname == '/apps/sign_up_sportscience':
        return sign_up_sportscience.layout

    if pathname == '/':
        return login.layout

    if pathname == '/apps/forgot_password':
        return forgot_password.layout
    else:
        return login.layout


""" auth = FlaskLoginAuth(app) """

application = app.server 
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080)
    #app.run_server(debug=True, port=8080) # Have this line active to debug (Choose one or other)
    # application.run(debug=True, host='0.0.0.0', port=8080) # Have this line active to run actual application
