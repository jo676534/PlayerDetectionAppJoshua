import boto3
import os
import botocore

from dotenv import load_dotenv
load_dotenv()

access_key_environment_var = os.getenv('aws_access_key')
secret_access_environment_var = os.getenv('aws_secret_access_key')
aws_region_name_var = os.getenv('aws_region_name')


ses_client = boto3.client('ses',aws_access_key_id=access_key_environment_var,aws_secret_access_key=secret_access_environment_var,region_name='us-east-1')
                                                    

aws_cognito_sportscience_link = 'https://console.aws.amazon.com/cognito/users/?region=us-east-1#/pool/us-east-1_LZxnKOtb3/users?_k=m0batf'


CHARSET = 'UTF-8'

verified_email_address = 'ricardo.mangandi@gmail.com'
admin_email_account = 'ricardo.mangandi@gmail.com'

def send_email_to_admin(first_name,last_name,email,phone):

    try:
        response = ses_client.send_email(
            Destination={'ToAddresses':[admin_email_account]},

            Message={
                'Body':{
                    'Text':{
                        'Charset':CHARSET,
                        'Data':f"Dear Admin, \
                                There is a request to create a new user with the following content:  \n \
                                Firstname: {first_name} \n \
                                Lastname: {last_name} \n  \
                                Email: {email} \n \
                                Phone: {phone} \n \
                                Please create the user at the following link: {aws_cognito_sportscience_link} \n \
                                Once the user has been created they will receive an email with a temporary password you have created."
                    }
                },
                'Subject':{
                    'Charset':CHARSET,
                    'Data':'New User Request'
                },
            },
            Source=verified_email_address

        )
        print(response)

    except botocore.exceptions.ClientError as error:
            print(error)
            return str(error)



def send_email_to_coach(coach_email,coach_name,game_time_submitted,first_name,last_name):

    try:
        response = ses_client.send_email(
            Destination={'ToAddresses':[coach_email]},

            Message={
                'Body':{
                    'Text':{
                        'Charset':CHARSET,
                        'Data':f"Dear {coach_name}, we have finished processing your game submitted on {game_time_submitted}, the submission was completed by {first_name} {last_name}. \
                        Please contact us with any additional questions at: sportscienceai@gmail.com"
                                
                    }
                },
                'Subject':{
                    'Charset':CHARSET,
                    'Data':'New User Request'
                },
            },
            Source=verified_email_address

        )
        print(response)

    except botocore.exceptions.ClientError as error:
            print(error)
            return str(error)


#if there is a new verified email address run this script or function 
""" def verify_email_address_as_source(unverified_email):
    
    try:
        response = ses_client.verify_email_identity(
            EmailAddress=unverified_email
        )
        print(response)

    except botocore.exceptions.ClientError as error:
        print(error) """
