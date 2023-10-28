#Created by Sridhar Gundumalla
#700734079

import boto3
import paramiko
import time
from flask import Flask, request, render_template, redirect, url_for
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify,render_template,redirect, url_for,flash
from s3_functions import create_bucket,upload_folder_to_s3
from dynamodb_operations import create_dynamodb_table
import bcrypt
import re

# Initialize the Flask app
app = Flask(__name__, template_folder='templates')


# Define the index route for rendering the Home Page


# Define a function to check if a username already exists
def check_existing_username(username):
    response = dynamodb.query(
        TableName=TABLE_NAME,
        KeyConditionExpression='username = :username',
        ExpressionAttributeValues={
            ':username': {'S': username}
        }
    )
    return response['Items']

# Define a function to check if an email already exists
def check_existing_email(email):
    response = dynamodb.scan(
        TableName=TABLE_NAME,
        FilterExpression='email = :email',
        ExpressionAttributeValues={
            ':email': {'S': email}
        }
    )
    return response['Items']




# Define the register route for handling registration
@app.route('/register', methods=['POST'])
def register():
    error_message = None
    success_message = None
    

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    agreed = request.form.get('agree')

    # Client-side validation for username (checking if it's empty)
    if not username.strip():
        error_message = 'Username cannot be empty'
    else:
        # Validate email format using a regular expression
        if not re.match(r'^[\w\.-]+@[\w\.-]+$', email):
            error_message = 'Invalid email address'

        # Password policies (you can add more here)
        elif len(password) < 8:
            error_message = 'Password must be at least 8 characters long'

        elif not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=])', password):
            error_message = 'Password must include at least one uppercase letter, one lowercase letter, one digit, and one special character'

        elif not username.strip():
            error_message = 'Username cannot be empty'

        elif not agreed:
            error_message = 'You must agree to the terms and conditions to register'

        else:
            # Check if the username already exists
            existing_username_users = check_existing_username(username)
            # Check if the email already exists
            existing_email_users = check_existing_email(email)

            if existing_username_users:
                error_message = 'Username already exists'
            elif existing_email_users:
                error_message = 'Email already exists'
            else:
                # Hash the user's password before storing it
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                hashed_password_str = hashed_password.decode('utf-8')

                # Store user data in DynamoDB
                try:
                    dynamodb.put_item(
                        TableName=TABLE_NAME,
                        Item={
                            'username': {'S': username},
                            'email': {'S': email},
                            'password': {'S': hashed_password_str}
                        }
                    )
                    success_message = 'Registration Successful'
                except Exception as e:
                    error_message = f'Registration Failed: {str(e)}'

    # Handle GET requests (initial form load or errors)
    return render_template('Registration.html', error=error_message, success=success_message)
    
if __name__ == '__main__':
    app.run(debug=True)