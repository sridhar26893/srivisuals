import boto3
import json
import gzip
import base64
from io import BytesIO
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
logs_table_name = 'YourLogsTable'
users_table_name = 'YourUsersTable'  # Change this to the actual table name for users

def lambda_handler(event, context):
    for record in event['Records']:
        # S3 bucket and key
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Retrieve the S3 object
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=bucket, Key=key)

        # Read and parse the access logs (assumes logs are in gzip format)
        log_data = gzip.decompress(obj['Body'].read()).decode('utf-8')
        logs = log_data.splitlines()

        # Process and store logs in DynamoDB
        for log in logs:
            log_entry = json.loads(log)
            store_log_in_dynamodb(log_entry)

def store_log_in_dynamodb(log_entry):
    # Generate a unique id for the log entry
    log_id = str(uuid.uuid4())

    # Get current timestamp
    timestamp = datetime.utcnow().isoformat()

    # Assuming 'user_id', 'event_type', 'details' are present in the log entry
    user_id = log_entry.get('user_id', 'N/A')
    event_type = log_entry.get('event_type', 'N/A')
    details = log_entry.get('details', 'N/A')

    # Retrieve username from the users table
    username = get_username_from_user_table(user_id)

    # Store log in DynamoDB
    table = dynamodb.Table(logs_table_name)
    table.put_item(
        Item={
            'id': log_id,
            'timestamp': timestamp,
            'event_type': event_type,
            'username': username,
            'details': details
        }
    )

def get_username_from_user_table(user_id):
    # Retrieve the username from the users table based on user_id
    user_table = dynamodb.Table(users_table_name)
    response = user_table.get_item(Key={'user_id': user_id})

    # Assume that the user table has an attribute 'username'
    username = response.get('Item', {}).get('username', 'N/A')

    return username
