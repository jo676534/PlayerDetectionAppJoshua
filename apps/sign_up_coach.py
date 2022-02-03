import imp
from sre_parse import State
from dash_bootstrap_components._components.FormFeedback import FormFeedback
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import os
import re
from dash.exceptions import PreventUpdate
from app import app
from aws import aws_cognito
#all components:

#########################################################################################################################################
first_name = html.Div(
    [
        dbc.Input(id='user_first_name',placeholder='First Name'),
        dbc.FormFeedback('Please do not leave this entry blank',valid='false')
    ]
        
)

last_name = html.Div(
    [
        dbc.Input(id='user_last_name',placeholder='Last Name'),
        dbc.FormFeedback('Please do not leave this entry blank',valid='false')
    ]

)



email_input_component = html.Div(
    [
        dbc.Input(id='user_email',type='email',placeholder='Enter email'),
        dbc.FormText(id='email_validation_text',children=None),
    
    ]
)


password_description_component = html.Div([

                            dbc.FormText(id='length_description_id',children='* Your Password must include at least 8 characters'),
                            dbc.FormText(id='uppercase_description_id',children='* At least one uppercase letter is needed'),
                            dbc.FormText(id='lowercase_description_id',children='* At least one lowercase letter is needed'),
                            dbc.FormText(id='number_description_id',children='* At least one number [0-9] is needed'),
                            dbc.FormText(id='special_char_description_id',children="* At least one special character ['!','@','#','$', '%', '&','+','/'] is needed"),
])  


password_input_component = html.Div(
    [
        dbc.Input(id='user_password',type='password',placeholder='Enter Password'),
        dbc.FormText(id='password_validation_text',children=password_description_component),
    ]

)

reenter_password_input_component = html.Div(
    [
            dbc.Input(id='user_password_reenter',type='password',placeholder='Confirm Password',disabled=True),
            dbc.FormText(id='password_reenter_validation_text',children=None),
            dbc.FormFeedback('Passwords do not match',valid='false')   
    ]

)


phone_number_input_component = html.Div(
    [
        dbc.Input(id='phone_number',placeholder='Phone Number',type='tel',pattern='[0-9]{3}-[0-9]{3}-[0-9]{4}',maxLength='12'),
        dbc.FormFeedback('Invalid Phone Number',valid='false')
    ]

)

sign_up_button_component = html.Div(
    
       
                        dbc.Button(
                        id='sign_up_button_id',
                        children='Sign Up',
                        color='primary',
                        )
    

    ) 


error_signing_up = html.Div(
                id='error_signing_up_id',
                children=
                [
                    dbc.Alert(id='error_alert_id',
                    children=html.Div(id='alert_text',
                    children='There was an error that occured when signing up, try again!'),
                    is_open=False,
                    color='danger',
                    dismissable=True
                    ),

                ]
)


component_inside_modal = html.Div(
                        children=
                        [
                            dbc.Input(id='verification_code'),
                            dbc.Label(id='validates_code',children=None,style={'color':'red'}),
                            html.Br(),
                            
                            dbc.Button(id='validates_code_button_id',children='Validate Code',disabled=True,style={'padding-bottom':'10px'}),
                            html.Hr(),
                            #dbc.Label(id='error_div',children=None),
                            html.Br(),
                   
                                    dbc.Alert(
                                    id='invalid_code_alert',
                                    children='Invalid Code! Resend Code?',
                                    color="danger",
                                    dismissable=True,
                                    is_open=False),



                        ], style={'textAlign':'center'}
)



confirmation_code_module =  dbc.Modal(
        [
                dbc.ModalHeader(children="Confirm Account"),
                dbc.ModalBody(id='modal_confirm_account_body_id',
                    children=
                        component_inside_modal
                      ),
                dbc.ModalFooter(
                    html.H5('You will be redirected to the login page once successfully confirmed account.')
               
                ),
        ],
        id='confirm_sign_up_module_id',
        is_open=False,
        backdrop='static',
        scrollable=True 
    )


send_back_to_login = dcc.Location(id='from_sign_up_coach_to_login',refresh=True)


card_body = html.Div(id='card_body_id',children=[
                html.H4('Sign Up as a Coach User!'),
                html.Br(),
                first_name,
                html.Br(),
                last_name,
                html.Br(),
                email_input_component,
                html.Br(),
                password_input_component,
                html.Br(),
                reenter_password_input_component,
                html.Br(),
                phone_number_input_component,

                #hiddden component inside body of the card
                confirmation_code_module,
                send_back_to_login

])


card = dbc.Card(
    [
        dbc.CardImg(src='https://github.com/dianabisbe/Images/blob/main/SportScienceLogo.png?raw=true',style={'background-color':'#000e44'}),
        dbc.CardBody(
            [   
                card_body,

            ]
        ),
        dbc.CardFooter(
            [
              # dcc.Location(id='take_user_to_confirm',refresh=True),
              # dcc.Location(id='to_refresh_the_page',refresh=True),
               error_signing_up,
               html.Div(id='sign_up_button_container_id',children=sign_up_button_component,style={'textAlign':'center'}),
               
            ]
           
        )
    ]
)




layout = html.Div(children=card,style={'padding-top':'50px','padding-left':'300px','padding-right':'300px'})


@app.callback(Output('validates_code_button_id','disabled'),
              Input('verification_code','value') #code entered
    )

def enables_button_to_verify_code(entered_code):
    
    if entered_code is None:
        raise PreventUpdate
    else:

        if len(entered_code) == 6:
            return False
        else: return True




@app.callback(
    Output('invalid_code_alert','is_open'), #alert incorrect code
    Output('from_sign_up_coach_to_login','pathname'),
    Output('validates_code_button_id','n_clicks'),
    #Output('',''), #pathname

    Input('validates_code_button_id','n_clicks'), #ensures user clicks button
    Input('user_email','value'), #user email
    Input('verification_code','value'), #code entered
   
    State('invalid_code_alert','is_open') #location
)

def verifies_code(n_clicks,user_email, code_entered,alert_message_is_open):

    if n_clicks is None:
        raise PreventUpdate
    else:  
       

        #api call occurs here to backend
        res = aws_cognito.sign_up_coach_user_confirm(user_email,code_entered)

        if res == 'success':
            alert_message_is_open = False
            pathname = '/apps/login'
        else:
            alert_message_is_open = True
            pathname = '/apps/sign_up_coach' 
        
        return alert_message_is_open ,pathname,None







@app.callback(

    Output('sign_up_button_id','disabled'),
  
    [
    Input('user_first_name','value'),
    Input('user_last_name','value'),
    Input('user_email','value'),
    Input('email_validation_text','children'),
    Input('password_reenter_validation_text','children'),
    Input('phone_number','value')
    ]
)

def enable_sign_up_button(user_first_name,
                          user_last_name,
                          user_email,
                          email_validation_text,
                          password_validation_text,
                          user_phone_number
                          ):
        if user_first_name != None and user_last_name != None and \
            email_validation_text == None and user_email != None and \
            password_validation_text == '* Passwords MATCH' \
            and user_phone_number != None:
            return False
    
        else: return True


""" @app.callback(Output('confirm_sign_up_module_id','is_open'),
              Input('sign_up_button_id','n_clicks'),
              State('confirm_sign_up_module_id','is_open')
            )

def open_up_module_to_confirm_sign_up(n_clicks,is_open):
    if n_clicks is None:
        raise PreventUpdate
    else:
        return True """




@app.callback(
    Output('error_alert_id','is_open'),
    #Output('alert_text','children'),
    #Output('user_email','value'),
   # Output('user_password','value'),
   # Output('user_password_reenter','value'),
    Output('confirm_sign_up_module_id','is_open'),
    Output('confirm_sign_up_module_id','n_clicks'),
    #Output('card_body_id','children'),

    Input('user_first_name','value'),
    Input('user_last_name','value'),
    Input('user_email','value'),
    Input('user_password','value'),
    Input('phone_number','value'),
    Input('sign_up_button_id','n_clicks'),
    State('error_alert_id','is_open'),
    State('confirm_sign_up_module_id','is_open')
)


#Ricardo@1020
def sign_up_user_attempt(
                        first_name,
                        last_name,
                        user_email,
                        user_password,
                        phone_number,
                        n_clicks,
                        is_open_error,
                        is_open_verifaction_code_ui
                        
                        ):
    if n_clicks is None:
        raise PreventUpdate
    
    else:

        #makes an api call to the backend

        if n_clicks:
            
            res = aws_cognito.attempt_to_sign_up_coach_user(first_name,last_name,user_email,user_password,phone_number)

            #res = 'success'

            if res == 'success':
                is_open_error = False
                is_open_verifaction_code_ui = True
                res = None

            else:
                is_open_verifaction_code_ui = False
                is_open_error = True
                error = res.split(':')[1]
                res = error

            return is_open_error,is_open_verifaction_code_ui,None








@app.callback(
    [
    Output('email_validation_text','children'),
    Output('email_validation_text','style'),
    ],
    Input('user_email','value')
)

def validate_email(email):
    if email is None:
        raise PreventUpdate
    else:
        
        #not my code ! Copied and pasted from internet because I did not know how
        #handle regex reference: https://stackabuse.com/python-validate-email-address-with-regular-expressions-regex/
        string_email = str(email)
        
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

        if re.fullmatch(regex,string_email):
            return None,None   
        
        else: return 'Invalid Email!',{'color':'red'}

def return_password_strength(password):

    points = 0
    is_good_length = False
    if len(password) >= 8:
        points = 1
        is_good_length = True

    counter = 0
    special_char_symbols = ['!','@','#','$', '%', '&','+','/']
    strong_password_list = {'isgoodlength': is_good_length,
                            'isupper': False, 
                            'islower': False, 
                            'isdigit': False, 
                            'isspecialchar': False,
                            'points': points
                            }

    while strong_password_list['points'] != 5 and counter < len(str(password)):
        
        if strong_password_list['points'] == 5:
            break
        
        val = str(password[counter])

        if val.isdigit() and strong_password_list['isdigit'] == False:
            strong_password_list['points']+=1
            strong_password_list['isdigit'] = True
        
        if val.islower() and strong_password_list['islower'] == False:
            strong_password_list['points']+=1
            strong_password_list['islower'] = True
        
        if val.isupper() and strong_password_list['isupper'] == False:
            strong_password_list['points']+=1
            strong_password_list['isupper'] = True
        
        if any (char in str(password) for char in special_char_symbols) and strong_password_list['isspecialchar'] == False:
            strong_password_list['points']+=1
            strong_password_list['isspecialchar'] = True


        counter+=1

    list_of_styles = [{'color':'green'},{'color':'green'},{'color':'green'},{'color':'green'},{'color':'green'}]

    if strong_password_list['points'] == 5:
        list_of_styles.append(False)
        return list_of_styles
    else: 
        if strong_password_list['isgoodlength'] == False:
            list_of_styles[0] = {'color':'red'}
            list_of_styles.append(True)

        if strong_password_list['isupper'] == False:
            list_of_styles[1] = {'color':'red'}
            list_of_styles.append(True)

        if strong_password_list['islower'] == False:
            list_of_styles[2] = {'color':'red'}
            list_of_styles.append(True)
        
        if strong_password_list['isdigit'] == False:
            list_of_styles[3] = {'color':'red'}
            list_of_styles.append(True)
  
        
        if strong_password_list['isspecialchar'] == False:
            list_of_styles[4] = {'color':'red'}
            list_of_styles.append(True)

    
        return list_of_styles


        
@app.callback(
    [
    Output('length_description_id','style'),
    Output('uppercase_description_id','style'),
    Output('lowercase_description_id','style'),
    Output('number_description_id','style'),
    Output('special_char_description_id','style'),
    Output('user_password_reenter','disabled')
    ],

    Input('user_password','value')
)

def validate_initial_password(user_password):

    if user_password is None:
        raise PreventUpdate    

    user_password_string = str(user_password)
      
    list_of_styles = return_password_strength(user_password_string)

    if list_of_styles[5] == True:
            return list_of_styles[0],list_of_styles[1],list_of_styles[2],list_of_styles[3],list_of_styles[4],list_of_styles[5]
            
    else: return list_of_styles[0],list_of_styles[1],list_of_styles[2],list_of_styles[3],list_of_styles[4],list_of_styles[5]
   
            
    

@app.callback(
            [
            Output('password_reenter_validation_text','children'),
            Output('password_reenter_validation_text','style')
            ],
            [
            Input('user_password_reenter','value'),
            Input('user_password','value'),
            Input('user_password_reenter','disabled'),
            State('error_alert_id','is_open')
            ]
            )

        
def validate_reenter_password(reenter_user_password,user_password,reenter_user_password_boolean,error_alert_id):

    if (reenter_user_password is None and reenter_user_password_boolean == False) or reenter_user_password_boolean == True:
        raise PreventUpdate
    else:

        if reenter_user_password == None and user_password == None:
            print('true')
            return None,None

        if str(user_password) != str(reenter_user_password):
            return '* Passwords do NOT match!',{'color':'red'}

        else: return '* Passwords MATCH',{'color':'green'}




@app.callback(
    Output('phone_number','value'),
    Input('phone_number','value')
)

def validate_phone_number(phone_number):

    if phone_number is None:
        raise PreventUpdate
    
    phone_number_string = str(phone_number)

    if len(phone_number_string) == 4:

        if phone_number_string[3] == '-':
            phone_number_string = phone_number_string[:3]
        
        else:
            phone_number_string = phone_number_string[:3] + '-' + phone_number_string[3:]
            return phone_number_string


    if len(phone_number_string) == 8:

        # this is for going backwards
        if phone_number_string[7] == '-':
            return phone_number_string[:7]
        
        # this is for going forwards
        else:
            phone_number_string = phone_number_string[:7] + '-' + phone_number_string[7:]
            return phone_number_string

    
    #this will take care of the autofill when user selects autofill #autofill should be all digits
    if len(phone_number_string) == 10 and phone_number_string.isdigit():
        phone_number_string = phone_number_string[:3] + '-' + phone_number_string[3:] 
        phone_number_string = phone_number_string[:7] + '-' + phone_number_string[7:]
        return phone_number_string

    else:
        return phone_number_string 