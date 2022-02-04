from flask import Flask
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from app import app
from aws import aws_cognito



hidden_div_email = html.Div(id='hidden_email',children='')
hidden_div_password = html.Div(id='hidden_password',children='')


email_component = html.Div(
        [
                dbc.Input(type='email',id='user_email',placeholder='Enter email'),
                html.Br()
        ],style={'padding-left':'200px','padding-right':'200px'}
      
)




password_component = html.Div(
        [
                dbc.Input(type='password',id='user_password', placeholder='Enter password'),
                html.Br()
        ],style={'padding-left':'200px','padding-right':'200px'}
)



#sign up as a coach hyperlink?
coach_sign_up_component = html.Div(
                dcc.Link(children='Sign Up as a Coach User?',id='coach_sign_up', href='/apps/sign_up_coach',refresh=True))

#sign up as a sports science member hyperlink?
sportscience_member_sign_up_component = html.Div(
                dcc.Link(children='Sign Up as a Sports Science AI User?',id='sportscience_member_sign_up', href='/apps/sign_up_sportscience',refresh=True))


forgot_password_button = html.Div(
                dbc.Button('Forgot Password?', color='danger', className='me-1',href='/apps/forgot_password'),
                style={'padding-bottom':'80px'},
                
                
)


sign_in_button_coach = html.Div(
    dbc.Button(id='sign_in_button_coach_id',children='Sign In as a Coach User',color='primary'),
    style={'padding-bottom':'5px'}
)

sign_in_button_sportscience = html.Div(
        dbc.Button(id='sign_in_button_sportscience_id',children='Sign In as a Sports Science AI User'),
        style={'padding-bottom':'5px'}
)


about_us_hyperlink = html.Div(dcc.Link(children='About Us',id='about_us', href='/apps/about_us',refresh=True))

#support text and email hyperlink
customer_support_text = html.Div([dbc.Label(children='Need customer support?')])
contact_us_text = dbc.Label(children='Contact us at:')

email_hyperlink_component = dcc.Link(children='sportscienceai@gmail.com',href='google.com')


##Errors or alerts UI:

incorrect_password_alert_1 = html.Div(
                                id='incorrect_password_alert_1',
                                children=
                                [dbc.Alert(id='incorrect_password_alert_id_1',
                                children=
                                [
                                    html.Div('Invalid Email or Password!'),
                                    dcc.Link(children='Reset Password?',
                                             href='/apps/forgot_password',
                                             style={'color':'#800000','text-decoration':'underline'},
                                             refresh=True)
                                ],
                                is_open=False,
                                color='danger',
                                dismissable=True)
                                ],style={'padding-left':'200px','padding-right':'200px'}
)


incorrect_password_alert_2 = html.Div(
                                id='incorrect_password_alert_2',
                                children=
                                [dbc.Alert(id='incorrect_password_alert_id_2',
                                children=
                                [
                                    html.Div('Invalid Email or Password!'),
                                    dcc.Link(children='Reset Password?',
                                             href='/apps/forgot_password',
                                             style={'color':'#800000','text-decoration':'underline'},
                                             refresh=True)
                                ],
                                is_open=False,
                                color='danger',
                                dismissable=True)
                                ],style={'padding-left':'200px','padding-right':'200px'}
)





card_container = dbc.Card(
        id='card_container',
        children= 
        [
                dbc.CardHeader(
                        children=[html.Img(
                                        id='logo_login',
                                        src='https://github.com/dianabisbe/Images/blob/main/SportScienceLogo.png?raw=true')],
                                style={'background-color':'#000e44'}),
                
                dbc.CardBody(
                        [       
                                html.Br(),   
                                email_component,
                                password_component,
                                html.Div(id='incorrect_password_div',children=None,style={'color':'red'}),
                                incorrect_password_alert_1,
                                incorrect_password_alert_2,
                                html.Br(),
                                sign_in_button_coach,
                                html.Div(),
                                coach_sign_up_component,
                                html.Br(),
                                sign_in_button_sportscience,
                                sportscience_member_sign_up_component,
                                html.Br(),
                                
                                html.Div(id='test_div'),
                                html.Br(),
                                forgot_password_button

                        ]
                ),
                dbc.CardFooter([
                                customer_support_text,
                                contact_us_text,
                                html.Br(),
                                email_hyperlink_component,
                                dcc.Location(id='enter_home_path',refresh=True),
                                dcc.Location(id='sportscience_home_path',refresh=True)
                                ])
        ],
)


layout = html.Div(children= [    
                                card_container
                            ]
        ,style={'textAlign': 'center', 
                'padding-left':'50px', 
                'padding-right':'50px',
                'padding-top':'10px',
                'padding-bottom':'20px'})



""" class User(UserMixin):
    def __init__(self,username):
        self.id = username """
   

#checks if user password is correct, signs in as a coach user
@app.callback(
    Output('incorrect_password_alert_id_1','is_open'),
    Output('sign_in_button_coach_id','n_clicks'),
    Output('enter_home_path','pathname'),

    Input('sign_in_button_coach_id','n_clicks'),
    Input('user_email','value'),
    Input('user_password','value'),
    State('incorrect_password_alert_id_1','is_open')
)

def attempt_to_sign_in_coach_user(n_clicks, user_email, user_password,is_open,):

    if n_clicks is None:
        raise PreventUpdate
     

    else:

            #make an api call to the backend
            #if successful sign in 
            res = aws_cognito.login_coach_user(user_email=user_email,user_password=user_password)

            if res == 'success':
                    is_open = False
                    return is_open, None, '/apps/coach_home'
            else:
                    is_open = True
                    return is_open, None, '/'




@app.callback(
    Output('incorrect_password_alert_id_2','is_open'),
    Output('sign_in_button_sportscience_id','n_clicks'),
    Output('sportscience_home_path','pathname'),

    Input('sign_in_button_sportscience_id','n_clicks'),
    Input('user_email','value'),
    Input('user_password','value'),
    State('incorrect_password_alert_id_2','is_open')
)

def attempt_to_sign_in_sportscience_ai_user(n_clicks,user_email,user_password,alert_is_open):

        if n_clicks is None:
                raise PreventUpdate
        else:
                res = aws_cognito.login_sportscience_ai(user_email=user_email,password=user_password)

                if res == 'NEW_PASSWORD_REQUIRED':
                        if aws_cognito.admin_sets_user_password(user_email,user_password) == 'success':
                                alert_is_open = False
                                return alert_is_open,None, '/apps/home'
                elif res == 'success':
                        alert_is_open = False
                        return alert_is_open, None, '/apps/home'
                else:
                        is_open = True
                        return is_open,None,'/'


            

