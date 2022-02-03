from dash_bootstrap_components._components.FormFeedback import FormFeedback
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from app import app
from aws import aws_email






first_name = html.Div(
        dbc.Input(id='user_first_name',placeholder='First Name')
)

last_name = html.Div(
        dbc.Input(id='user_last_name',placeholder='Last Name')
)



email_input_component = html.Div(
    [
        dbc.Input(id='user_email',type='email',placeholder='Enter email'),
        dbc.FormText('Your email will also be your username'),
        dbc.FormFeedback('Please enter a valid email address',valid='false')
    ]
)





phone_number_input_component = html.Div(
    [
        dbc.Input(id='phone_number_sportscience',placeholder='Phone Number',type='tel',pattern='[0-9]{3}-[0-9]{3}-[0-9]{4}'),
        dbc.FormFeedback('Invalid Phone Number',valid='false')
    ]

)

sign_up_button = html.Div(
    [
        dbc.Button(id='sign_up_button_id_sports_science_ai',children='Sign Up',color='primary',disabled=True),
        dbc.FormText(id='test_id',children=None)  
    ]
    
)

card = dbc.Card(
    [
        dbc.CardImg(src='https://github.com/dianabisbe/Images/blob/main/SportScienceLogo.png?raw=true',style={'background-color':'#000e44'}),
        dbc.CardBody(
            id='sign_up_sportscience_ai_cardbody',
            children=
            [
                html.H4('Sign Up as a Sports Science AI User!'),
                html.Br(),
                first_name,
                html.Br(),
                last_name,
                html.Br(),
                email_input_component,
                html.Br(),
                phone_number_input_component

            ]
        ),
        dbc.CardFooter(
            id='card_footer_id',
           children=sign_up_button,style={'textAlign':'center'}
            
        )
    ]
)

after_request_to_sign_up = html.Div(
                            html.H5('Your request has been made and the admin has been notified to create your account. \
                            Please check your email for a temporary password and login. Your temporary password will expire in 7 days.')
)

button_return_login = html.Div(dbc.Button(id='return_login_button_id',children='Return to Login',color='primary',href='/apps/login'),)

layout = html.Div(children=card,style={'padding-top':'50px','padding-left':'300px','padding-right':'300px'})



@app.callback(Output('card_footer_id','children'),
              Output('sign_up_sportscience_ai_cardbody','children'),
              Input('sign_up_button_id_sports_science_ai','n_clicks'),
              Input('user_first_name','value'),
              Input('user_last_name','value'),
              Input('user_email','value'),
              Input('phone_number_sportscience','value')
                )

def ask_admin_to_sign_up(n_clicks,user_first_name,user_last_name,user_email,phone_number):

    if n_clicks is None:
        raise PreventUpdate
    
    else:
        aws_email.send_email_to_admin(user_first_name,user_last_name,user_email,phone_number)
   

        return button_return_login,after_request_to_sign_up


@app.callback(
              Output('sign_up_button_id_sports_science_ai','disabled'),

              Input('user_first_name','value'),
              Input('user_last_name','value'),
              Input('user_email','value'),
              Input('phone_number_sportscience','value'))

def enable_button(user_first_name,user_last_name,user_email,phone_number):



        if user_first_name != None and user_last_name != None and user_email != None and phone_number != None:
            return False
        else:
            return True