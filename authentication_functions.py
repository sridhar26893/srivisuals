import boto3
import bcrypt
from dynamodb_operations import create_dynamodb_table

class DynamoDB:
    def __init__(self):
        self.client = boto3.client('dynamodb', region_name='us-east-1')

    def query(self, **kwargs):
        return self.client.query(**kwargs)

    def scan(self, **kwargs):
        return self.client.scan(**kwargs)

# Define the 'Registration' table name
TABLE_NAME = 'UserRegistration'
create_dynamodb_table(TABLE_NAME)

class DynamoDB:
    def __init__(self):
        self.client = boto3.client('dynamodb', region_name='us-east-1')

    def query(self, **kwargs):
        return self.client.query(**kwargs)

    def scan(self, **kwargs):
        return self.client.scan(**kwargs)

class UserUtils:
    dynamodb_proxy = DynamoDB()  # Create an instance of the DynamoDB class

    @staticmethod
    def get_user_by_username(username):
        try:
            response = UserUtils.dynamodb_proxy.query(
                TableName=TABLE_NAME,
                KeyConditionExpression='#u = :username',
                ExpressionAttributeNames={'#u': 'username'},
                ExpressionAttributeValues={':username': {'S': username}}
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error in get_user_by_username: {e}")
            return []

    @staticmethod
    def get_user_by_email(email):
        try:
            response = UserUtils.dynamodb_proxy.scan(
                TableName=TABLE_NAME,
                IndexName='EmailIndex',
                FilterExpression='#e = :email',
                ExpressionAttributeNames={'#e': 'email'},
                ExpressionAttributeValues={':email': {'S': email}}
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error in get_user_by_email: {e}")
            return []

    @staticmethod
    def authenticate_user(email, password):
        error_message = None
        user = UserUtils.get_user_by_email(email)

        if user:
            stored_password_hash = user[0].get('password_hash', '')

            if password is not None:
                # Use bcrypt to check if the entered password matches the stored hash
                if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                    return True  # Authentication successful
                else:
                    error_message = "Invalid password"
            else:
                error_message = "Password cannot be empty"

        return False, error_message  # Authentication failed

# Provide desired username and email
user_data_by_username = UserUtils.get_user_by_username('sridhar26893')
user_data_by_email = UserUtils.get_user_by_email('g.sridhar888@gmail.com')
