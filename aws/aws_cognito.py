from ftplib import error_perm
from multiprocessing.connection import Client
import boto3
import os
import botocore

from aws import aws_email
from dotenv import load_dotenv

load_dotenv()


access_key_environment_var = os.getenv('aws_access_key')
secret_access_environment_var = os.getenv('aws_secret_access_key')
aws_region_name_var = os.getenv('aws_region_name')

coach_client_id = os.getenv('aws_coach_user_client_id')
coach_pool_id = os.getenv('aws_coach_user_pool_id')

sportscience_client_id = os.getenv('aws_sportscience_client_id')
sportscience_pool_id = os.getenv('aws_sportscienceai_pool_id')


cognito_client_instance = boto3.client('cognito-idp',aws_access_key_id=access_key_environment_var,aws_secret_access_key=secret_access_environment_var,region_name='us-east-1')
operation_successful = 'success'



#login coach user
def login_coach_user(user_email,user_password):
    #print(coach_client_id)
    #print(coach_pool_id)
    
    if user_email == None or user_password == None:
            return 'Invalid Entries'
    else:

        try:
                response = cognito_client_instance.initiate_auth(
                ClientId=str(coach_client_id),
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={'USERNAME': user_email, 'PASSWORD': user_password})
                
                auth_results = response['AuthenticationResult']

                get_token_for_current_user = auth_results['AccessToken']

                print('User access token that needs to be saved in database: ',get_token_for_current_user)

                user_signed_in_response = cognito_client_instance.get_user(AccessToken=str(get_token_for_current_user))
                                
                checks_if_user_signed_in_metadata = user_signed_in_response['ResponseMetadata']

                checks_if_user_signed_in = checks_if_user_signed_in_metadata['HTTPStatusCode']

                if checks_if_user_signed_in == 200:
                        print('Coach user logged in!')
                        return operation_successful

        
        except botocore.exceptions.ClientError as error:
                print(error)
                return str(error)


#initial sign up coach user
def attempt_to_sign_up_coach_user(
                                user_firstname,
                                user_lastname,
                                user_email,
                                user_password,
                                user_phone_number
                                ):

        if user_firstname == None or user_lastname == None or user_email == None or user_password == None:
                return 'Invalid Entries'
        else:
                temp_phone_number = str(user_phone_number)
                formated_phone = '+1' + temp_phone_number[:3] + (temp_phone_number[4:7] + temp_phone_number[8:])
                try:
                        sign_up_coach_user_response = cognito_client_instance.sign_up(
                        ClientId=coach_client_id,
                        Username=user_email,
                        Password=user_password,
                        UserAttributes=     [
                                                {'Name':'given_name', 'Value': user_lastname},
                                                {'Name': 'family_name', 'Value': user_firstname},
                                                {'Name': 'email', 'Value': user_email },
                                                {'Name': 'phone_number', 'Value': formated_phone}
                                                ]
                                                )


                        get_http_response_temp = sign_up_coach_user_response['ResponseMetadata']

                        get_http_response = get_http_response_temp['HTTPStatusCode']

                        if get_http_response == 200:
                                return operation_successful
                
                except botocore.exceptions.ClientError as error:
                        print(error)    
                        return str(error)


    



#confirm sign up coach user
def sign_up_coach_user_confirm(user_email,user_code):

    if user_email == None or user_code == None:
            return 'Invalid Entries'
    else:
        try:
                confirm_coach_user_sign_up = cognito_client_instance.confirm_sign_up(
                        ClientId=coach_client_id,
                        Username=user_email,
                        ConfirmationCode=str(user_code)
                )

                get_http_response_temp = confirm_coach_user_sign_up['ResponseMetadata']

                get_http_response = get_http_response_temp['HTTPStatusCode'] 

                if get_http_response == 200:
                        return operation_successful

        except botocore.exceptions.ClientError as error:
                print(error)
                return str(error)               





#initial sign up sportscience ai user
def ask_admin_to_sign_user_up(user_firstname,user_lastname,user_email,phone_number):
        if user_firstname == None or user_lastname == None or user_email == None or phone_number == None:
                return 'Invalid Entries'
        else:
                aws_email.send_email_to_admin(user_firstname,user_lastname,user_email,phone_number)
        

#permanent password for user
def sets_password_for_user(user_email,password):
    if user_email == None or password == None:
            return 'Please Enter Your Credentials'
    else:  
        try:
                response = cognito_client_instance.admin_set_user_password(
                        UserPoolId=sportscience_pool_id,
                        Username=user_email,
                        Password=password,
                        Permanent=True

                )
                print(response)

        except botocore.exceptions.ClientError as error:
                print(error)
                return str(error)
 





def login_sportscience_ai(user_email,password):
    if user_email == None or password == None:
            return 'Please Enter Your Credentials'
    else: 
        try:
                response = cognito_client_instance.admin_initiate_auth(
                        UserPoolId=sportscience_pool_id,
                        ClientId=sportscience_client_id,
                        AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                        AuthParameters={'USERNAME':user_email, 'PASSWORD':password}
                )
                

                if 'ChallengeName' in response:
                        get_response_challenge_name =response['ChallengeName']

                        if get_response_challenge_name == 'NEW_PASSWORD_REQUIRED':
                                return 'NEW_PASSWORD_REQUIRED'
                        else:   
                                print('Need to set the password permanently for user')
                                return operation_successful
                else:   
                        print('Sports Science AI Member logged in!')
                        return operation_successful

        except botocore.exceptions.ClientError as error:
                print(error)
                return str(error)



def admin_sets_user_password(user_email,password_perm):
    if user_email == None or password_perm == None:
            return 'Please Enter Your Credentials'
    else: 
        try:
                response = cognito_client_instance.admin_set_user_password(
                        UserPoolId=sportscience_pool_id,
                        Username=user_email,
                        Password=password_perm,
                        Permanent=True
                )
                print('user password is set')
                #print(response)
                return operation_successful

        except botocore.exceptions.ClientError as error:
                print(error)
                return str(error)





#reset password
def reset_any_user_password(user_type,username):
        
        if user_type == 'cu':
                client_id = coach_client_id
        else:
                client_id = sportscience_client_id
        

        try:
                response = cognito_client_instance.forgot_password(
                        ClientId=client_id,
                        Username=username
                )
                print(response)
                return operation_successful

        except botocore.exceptions.ClientError as error:
                print(error)
                return str(error)




#verification code reset password
def confirm_reset_any_user_password(user_type,username,code_entered,new_password):

        if user_type == 'cu':
                client_id = coach_client_id
        else:
                client_id = sportscience_client_id
        
        try:
                response = cognito_client_instance.confirm_forgot_password(
                        ClientId=client_id,
                        Username=username,
                        ConfirmationCode=code_entered,
                        Password=new_password
                )
                print(response)
                return operation_successful

        except botocore.exceptions.ClientError as error:
                print(error)
                return str(error)


#resend confirmation email
def resend_confirmation_code(user_type,username):

        if user_type == 'cu':
                client_id = coach_client_id
        else:
                client_id = sportscience_client_id
        
        try:
                response = cognito_client_instance.resend_confirmation_code(
                        ClientId=client_id,
                        Username=username
                )
                return operation_successful

        except botocore.exceptions.ClientError as error:
                print(error)
                return str(error)