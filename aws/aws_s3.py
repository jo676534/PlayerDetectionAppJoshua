import boto3
import os
import botocore



access_key_environment_var = os.getenv('aws_access_key')
secret_access_environment_var = os.getenv('aws_secret_access_key')

cognito_client_instance = boto3.client('s3',aws_access_key_id=access_key_environment_var,
                                                        aws_secret_access_key=secret_access_environment_var,
                                                        region_name='us-east-1')
                                                        
                                                        




#upload file
