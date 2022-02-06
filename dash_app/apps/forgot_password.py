import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
import os
from dash.exceptions import PreventUpdate
from matplotlib import use
from torch import layout
from aws import aws_cognito
from app import app
import re
from apps import sign_up_coach as password_strength

password_description_component = html.Div(
    [
        dbc.FormText(
            id="reset_length_description_id",
            children="* Your Password must include at least 8 characters",
        ),
        dbc.FormText(
            id="reset_uppercase_description_id",
            children="* At least one uppercase letter is needed",
        ),
        dbc.FormText(
            id="reset_lowercase_description_id",
            children="* At least one lowercase letter is needed",
        ),
        dbc.FormText(
            id="reset_number_description_id",
            children="* At least one number [0-9] is needed",
        ),
        dbc.FormText(
            id="reset_special_char_description_id",
            children="* At least one special character ['!','@','#','$', '%', '&','+','/'] is needed",
        ),
    ]
)


email_component = html.Div(
    [
        dbc.Input(
            type="email", id="user_email_forgot_password", placeholder="Enter email"
        ),
        html.Br(),
    ],
    style={"padding-left": "200px", "padding-right": "200px"},
)


""" 
user_instruction_component = html.Div(
    children=
    [
        
    ]
) """

drop_down = html.Div(
    children=dcc.Dropdown(
        id="type_of_user",
        options=[
            {"label": "Coach User", "value": "cu"},
            {"label": "SportScience AI User", "value": "spai"},
        ],
        style={"padding-left": "200px", "padding-right": "200px"},
    )
)


send_verifaction_code = html.Div(
    [dbc.Button(id="send_verifaction_code_reset", children="Send Code", disabled=True)]
)

an_error_occurred = html.Div(
    children=dbc.Alert(
        id="invalid_code_alert_reset",
        children="Invalid Code! Resend Code?",
        color="danger",
        dismissable=True,
        is_open=False,
    ),
    style={"padding-left": "200px", "padding-right": "200px"},
)

""" 
component_inside_modal = html.Div(
                        children=
                        [   
                            
                            dbc.Input(id='input_code'),
                            dbc.Label(id='validates_code',children=None,style={'color':'red'}),
                            html.Br(),
                            
                            dbc.Button(id='open_up_reset_component_button',children='Validate Code',disabled=True,style={'padding-bottom':'10px'}),
                            html.Hr(),
                            html.Br(),
                   
                                    dbc.Alert(
                                    id='invalid_code_alert_reset',
                                    children='Invalid Code! Resend Code?',
                                    color="danger",
                                    is_open=False),



                        ], style={'textAlign':'center'}
)
 """


form_to_reset_and_submit_component = html.Div(
    children=[
        dbc.Label("Enter Confirmation Code"),
        dbc.Input(id="validation_code"),
        html.Br(),
        dbc.Label("Reset Password"),
        dbc.Input(id="reset_password_input", type="password"),
        dbc.Popover(
            id="popover_password",
            children="",
            trigger="hover",
            target="reset_password_input",
        ),
        password_description_component,
        html.Br(),
        dbc.Input(id="confirm_password_input", type="password"),
        html.Br(),
        html.Div(
            children=dbc.Alert(
                id="invalid_code_alert_reset_inside",
                children="Invalid Code! Resend Code?",
                color="danger",
                dismissable=True,
                is_open=False,
            ),
        ),  # hidden until further notice
        html.Br(),
        html.Div(
            dbc.Button(
                id="submit_password_reset_button",
                children="Submit Password Reset",
                disabled=True,
            ),
            style={"textAlign": "center"},
        ),
    ]
)


reset_password_module = html.Div(
    dbc.Modal(
        [
            dbc.ModalHeader(children="Resetting User Password"),
            dbc.ModalBody(
                id="modal_body_id", children=form_to_reset_and_submit_component
            ),
            dbc.ModalFooter(
                html.H5(
                    "You will be redirected to the login page once successfully resetted password."
                )
                # form_to_reset_and_submit_component
                # html.Div(id='reset_password_div_entry_holder',children=dbc.Button('hello',style={'textAlign':'center'}))
            ),
        ],
        id="reset_password_module",
        is_open=False,
        backdrop="static",
        scrollable=True,
    )
)

card_container = dbc.Card(
    id="forgot_password_container",
    children=[
        dbc.CardHeader(
            children=[
                html.Img(
                    id="logo_login",
                    src="https://github.com/dianabisbe/Images/blob/main/SportScienceLogo.png?raw=true",
                )
            ],
            style={"background-color": "#000e44"},
        ),
        dbc.CardBody(
            [
                html.H4(
                    "Please enter your email and we will send a verifaction code to allow you to reset your password."
                ),
                html.Br(),
                email_component,
                html.Div(id="email_error_id", children=None, style={"color": "red"}),
                drop_down,
                html.Br(),
                send_verifaction_code,
                reset_password_module,  # hidden
                html.Br(),
                an_error_occurred,
                html.Br(),
                html.Div(id="error_description", children=None),
                dcc.Location(id="return_to_login", refresh=True),
            ]
        ),
    ],
)


layout = html.Div(
    children=[card_container],
    style={
        "textAlign": "center",
        "padding-left": "50px",
        "padding-right": "50px",
        "padding-top": "10px",
        "padding-bottom": "20px",
    },
)
##########################################################################################


@app.callback(
    [
        Output("reset_length_description_id", "style"),
        Output("reset_uppercase_description_id", "style"),
        Output("reset_lowercase_description_id", "style"),
        Output("reset_number_description_id", "style"),
        Output("reset_special_char_description_id", "style"),
        Input("reset_password_input", "value"),
    ],
)
def validate_password_strength(user_password):

    if user_password is None:
        raise PreventUpdate

    else:
        list_of_styles = password_strength.return_password_strength(str(user_password))
        if list_of_styles[5] == True:
            return (
                list_of_styles[0],
                list_of_styles[1],
                list_of_styles[2],
                list_of_styles[3],
                list_of_styles[4],
            )

        else:
            return (
                list_of_styles[0],
                list_of_styles[1],
                list_of_styles[2],
                list_of_styles[3],
                list_of_styles[4],
            )


##########################################################################################


@app.callback(
    Output("submit_password_reset_button", "disabled"),
    Input("confirm_password_input", "value"),
    Input("reset_password_input", "value"),
)
def double_checks_user_input(confirm_password_input, reset_password_input):

    if confirm_password_input is None and reset_password_input is None:
        raise PreventUpdate

    else:
        if confirm_password_input != reset_password_input:
            return True
        else:
            return False


##########################################################################################


@app.callback(
    Output("invalid_code_alert_reset_inside", "children"),
    Output("invalid_code_alert_reset_inside", "is_open"),
    Output("submit_password_reset_button", "n_clicks"),
    Output("return_to_login", "pathname"),
    Input("submit_password_reset_button", "n_clicks"),
    Input("type_of_user", "value"),  # type of user
    Input("user_email_forgot_password", "value"),  # usernanme
    Input("reset_password_input", "value"),  # password
    Input("validation_code", "value"),
    State("invalid_code_alert_reset_inside", "is_open"),
)
def submit_password_reset(
    n_clicks, user_type, username, new_password, code_entered, is_open_error
):
    if n_clicks is None:
        raise PreventUpdate

    else:
        res = aws_cognito.confirm_reset_any_user_password(
            user_type, username, code_entered, new_password
        )
        # print('usertype',user_type)
        # print('usernanme',username)
        # print('password',new_password)
        # print('code',code_entered)

        # res = 'success'
        if res == "success":
            is_open_error = False

            return None, is_open_error, None, "/apps/login"

        else:
            is_open_error = True
            error = res.split(":")[1]
            res = error
            return res, is_open_error, None, "/apps/forgot_password"


##########################################################################################


@app.callback(
    Output("reset_password_module", "is_open"),
    Input("send_verifaction_code_reset", "n_clicks"),
    State("reset_password_module", "is_open"),
)
def open_reset_password(n_clicks, reset_module_is_open):

    if n_clicks is None:
        raise PreventUpdate
    else:
        reset_module_is_open = True
        return reset_module_is_open


##########################################################################################


@app.callback(
    Output("send_verifaction_code_reset", "disabled"),
    Output("email_error_id", "children"),
    Input("user_email_forgot_password", "value"),
    Input("type_of_user", "value"),
)
def sets_send_code_button(user_email, type_of_user):
    # print(type_of_user)
    if user_email is None or type_of_user is None:
        raise PreventUpdate

    else:

        # not my code ! Copied and pasted from internet because I did not know how
        # handle regex reference: https://stackabuse.com/python-validate-email-address-with-regular-expressions-regex/
        string_email = str(user_email)

        regex = re.compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )

        if re.fullmatch(regex, string_email):
            return False, None

        else:
            return True, "Invalid Email!"


##########################################################################################


@app.callback(
    Output("send_verifaction_code_reset", "children"),
    Output("send_verifaction_code_reset", "n_clicks"),
    Output("invalid_code_alert_reset", "children"),
    Output("invalid_code_alert_reset", "is_open"),
    # Output('error_description','children'),
    Input("send_verifaction_code_reset", "n_clicks"),
    Input("user_email_forgot_password", "value"),
    Input("type_of_user", "value"),
    State("invalid_code_alert_reset", "is_open"),
)
def send_code_to_user_email(n_clicks, user_email, type_of_user, alert_is_open):

    if n_clicks is None:
        raise PreventUpdate
    else:
        res = aws_cognito.reset_any_user_password(
            user_type=type_of_user, username=user_email
        )
        # print(res)
        # res = 'success'
        if res == "success":
            alert_is_open = False
            return "Sent!", True, None, alert_is_open
        else:
            alert_is_open = True
            error = res.split(":")[0]
            res = error
            return (
                "An error occurred! Try Again?",
                None,
                res,
                alert_is_open,
            )
