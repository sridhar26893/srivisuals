import boto3
from flask import Flask, request, render_template, redirect, url_for,session
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify,render_template,redirect, url_for,flash
#from s3_functions import create_bucket,upload_folder_to_s3
from dynamodb_operations import create_dynamodb_table
from cloudfront_creation import create_cloudfront_distribution
from dynamodb_posts import create_posts_table
#from ec2_operations import create_ec2_instance_with_autoscaling_and_apache
#from ALB_operations import create_application_load_balancer
from datetime import datetime
import uuid
import logging

from flask import current_app
import bcrypt
import re


# Initialize the Flask app
app = Flask(__name__, template_folder='templates')
app.secret_key =b"\xff\x86\xba<\xac\x031\x90n\xeb2\xd7\xe8'\xb6E\x88BUd\x9b\x8cu\xba"

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3')
region = "us-east-2"
# Define the 'Registration' table name
DYNAMODB_TABLE_POSTS = 'Posts'
#create_posts_table(DYNAMODB_TABLE_POSTS)
TABLE_NAME = 'UserRegistration'
create_dynamodb_table(TABLE_NAME)


# S3 bucket creationg
#bucket_name = "srivisual-webpages"
#location = {"LocationConstraint": region}
#result=create_bucket(bucket_name,location)

#S3 function call to upload files
#local_folder_path = "C:/Users/gsrid/Desktop/myproject"
#bucket_name = "srivisual-webpages"
#upload_folder_to_s3(local_folder_path, bucket_name)

#CDN creation
s3_bucket_name = 'srivisual-webpages'
create_cloudfront_distribution(s3_bucket_name)
CDN_DOMAIN ='EL0UGSNXY6FSZ'
S3_BUCKET_NAME ='srivisual-webpages' 
IMAGE_COUNTER=0



# Define a function to check if a username already exists
def check_existing_username(username):
    response = dynamodb.scan(
        TableName=TABLE_NAME,
        IndexName='UsernameIndex',
        FilterExpression='#u = :username',
        ExpressionAttributeNames={'#u': 'username'},
        ExpressionAttributeValues={
            ':username': {'S': username}
        }
    )
    return response['Items']

# Define a function to check if an email already exists
def check_existing_email(email):
    if email is None:
        return []  # Return an empty list if email is None
    response = dynamodb.scan(
        TableName=TABLE_NAME,
        IndexName='EmailIndex',
        FilterExpression='#e = :email',
        ExpressionAttributeNames={'#e': 'email'},
        ExpressionAttributeValues={
            ':email': {'S': email}
        }
    )
    return response['Items']


# Function to retrieve a user by email
def get_user_data(identifier):
    if identifier is not None and isinstance(identifier, str):
        # Check if the identifier is an email
        if '@' in identifier:
            response = dynamodb.query(
                TableName=TABLE_NAME,
                IndexName='EmailIndex',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={
                    ':email': {'S': identifier.lower()}
                }
            )
            
        else:  # Assume it's a username
            response = dynamodb.query(
                TableName=TABLE_NAME,
                IndexName='UsernameIndex',
                KeyConditionExpression='username = :username',
                ExpressionAttributeValues={
                    ':username': {'S': identifier.lower()}
                }
            )
           
        if 'Items' in response:
            user_data = response['Items']
            if user_data:
                return user_data[0]
    else:
        print("Invalid identifier. Please provide a valid email or username.")
    
    return {}


    
def authenticate_user(identifier, password):
    error_message = None

    # Retrieve user data using the combined function
    user_data = get_user_data(identifier)

    
    if user_data:
        stored_password_hash = user_data.get('password', {}).get('S', '')

        if stored_password_hash:
            password_bytes = password.encode('utf-8')
            stored_hash_bytes = stored_password_hash.encode('utf-8')

            print(f"Entered Password Bytes: {password_bytes}")
            print(f"Stored Hash Bytes: {stored_hash_bytes}")

            # Use bcrypt to check if the entered password matches the stored hash
            if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                return True, None  # Authentication successful
            else:
                error_message = "Invalid password"
        else:
            error_message = "Stored password hash is missing or empty"
    else:
        error_message = "User not found with the provided identifier"

    # Logging the error
    logging.error(f"Authentication failed: {error_message}")

    return False, error_message  # Authentication failed



#Function for defining post id
def generate_post_id():
    # Use a combination of timestamp and a random UUID for uniqueness
    return f"{int(datetime.now().timestamp())}"

def upload_image_and_create_post(image_file):
    try:

        current_user_identifier=session.get('user_identifier')
        user_data=get_user_data(current_user_identifier)
        # Generate a unique post ID
        post_id = generate_post_id()

        # Get current date and time
        creation_date = datetime.now().isoformat()

        # Get the current user's username using the get_user_data function
        #user_data = get_user_data(identifier)
        if not user_data:
            raise ValueError(f"User not found with identifier: {current_user_identifier}")

        # Extract username from user_data
        username = user_data.get('username', {}).get('S', '')
        
        # Check if the user is authenticated
        if not username:
            raise ValueError("User not authenticated")

        # Extract filename without using secure_filename
        original_filename = image_file.filename

        # Include the username in the file path
        filename = f"uploads/{username}/{post_id}.{original_filename.split('.')[-1]}"

        # Upload image to S3
        s3.upload_fileobj(image_file, S3_BUCKET_NAME, filename)

        # Store post information in DynamoDB
        dynamodb.put_item(
            TableName=DYNAMODB_TABLE_POSTS,
                Item={
                    'post_id':{'S': post_id},
                    'createdByUser':{'S': username},
                    'postCreationDate':{'S': creation_date},
                    'mediaType': {'S': image_file.content_type},
                    'likes': {'N': '0'},
                           
                }
        ) 
       
        print('Post information stored in DynamoDB.')

        return True
    
    except Exception as e:
        print(f"Error uploading image and creating post: {str(e)}")
        return False

def create_s3_folder(bucket_name, folder_name):
    s3 = boto3.client('s3')

    # Ensure the bucket exists
    try:
        s3.head_bucket(Bucket=bucket_name)
    except s3.exceptions.NoSuchBucket:
        # Create the bucket
        s3.create_bucket(Bucket=bucket_name)

    # Ensure folder_name doesn't start or end with a '/'
    if folder_name.startswith('/') or folder_name.endswith('/'):
        folder_name = folder_name.strip('/')

    # Check if the folder already exists
    if not does_s3_folder_exist(bucket_name, folder_name):
        # Create a new folder by uploading an empty object with a trailing slash
        folder_key = f"{folder_name}/"
        s3.put_object(Bucket=bucket_name, Key=folder_key)

def does_s3_folder_exist(bucket_name, folder_name):
    s3 = boto3.client('s3')

    # Ensure the bucket exists
    try:
        s3.head_bucket(Bucket=bucket_name)
    except s3.exceptions.NoSuchBucket:
        return False  # Bucket doesn't exist, so folder can't exist

    # Check if the folder exists by listing objects with the given prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f"{folder_name}/")

    # If objects are listed, the folder exists
    return 'Contents' in response

def get_s3_image_urls(username):
    
    s3_base_url = f'https://{s3_bucket_name}.s3.us-east-2.amazonaws.com/'

    # Assume the images are stored in the 'uploads' folder under the username
    prefix = f'uploads/{username}/'

    s3 = boto3.client('s3', region_name='us-east-2')
    
    # List objects in the specified folder
    response = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=prefix)

    # Extract image URLs
    image_urls = [s3_base_url + obj['Key'] for obj in response.get('Contents', [])]

    return image_urls

folder_prefix = 'uploads/'
def list_images_in_folder(folder_path):
    response = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=folder_path)
    images = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    return images

  # Change this to the desired folder path

def get_images_with_username_from_s3(s3_bucket_name, prefix='uploads/'):
    try:
        # List objects in the specified prefix
        response = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=prefix)

        # Extract image URLs, usernames, and post IDs from the response
        base_url = f'https://{s3_bucket_name}.s3.{region}.amazonaws.com/'

        images_data = [
            {
                'url': base_url + obj['Key'],
                'username': obj['Key'].rsplit('/', 2)[1],
                'post_id': obj['Key'].rsplit('/', 1)[1].rsplit('.', 1)[0]
            }
            for obj in response.get('Contents', [])
        ]

        for image_data in images_data:
            print(f"Base URL: {base_url}, Image URL: {image_data['url']}")

        return images_data

    except Exception as e:
        print(f"Error getting images from S3: {str(e)}")
        return []


def store_like_for_post(post_id):
    try:
        response = dynamodb.update_item(
            TableName=DYNAMODB_TABLE_POSTS,
            Key={
                'post_id': {'S': post_id}
            },
            UpdateExpression='SET likes = likes + :val',
            ExpressionAttributeValues={
                ':val': {'N': '1'}
            },
            ReturnValues='UPDATED_NEW'
        )
        new_like_count = response['Attributes']['likes']['N']
        print(f'Like count for post {post_id} incremented to {new_like_count}')
        return int(new_like_count)
    except Exception as e:
        print(f"Error storing like for post: {str(e)}")
        return None

@app.route('/')
def index():
    
    s3_bucket_name = 'srivisual-webpages'
    s3_folder = 'uploads/'
  

    # List objects in the S3 bucket
    response = s3.list_objects_v2(Bucket=s3_bucket_name, Prefix=s3_folder)

    # Extract image URLs from the response
    image_urls = [f'https://{s3_bucket_name}.s3.amazonaws.com/{obj["Key"]}' for obj in response.get('Contents', [])]

   
    return render_template('Home.html',image_urls=image_urls )

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

@app.route('/profile/<identifier>', methods=['GET'])
def profile(identifier):
    user_data = get_user_data(identifier)

    # Extract username and email from the user_data
    username = user_data.get('username', {}).get('S', '')
    email = user_data.get('email', {}).get('S', '')

    image_urls = get_s3_image_urls(username)
   
    # Pass username and email to the template
    return render_template('profile.html', username=username, email=email,image_urls=image_urls)




@app.route('/test', methods=['GET', 'POST'])
def test():
    image_urls = [f'https://{s3_bucket_name}.s3.{region}.amazonaws.com/{image}' for image in list_images_in_folder(folder_prefix)]

    if request.method == 'POST':
        if request.is_json:
            # Handle JSON request
            data = request.get_json()
            post_id = data.get('post_id')
            print(f"Received JSON data. Post ID: {post_id}")
            if post_id:
                # Call the function to store the like in the database
                new_like_count = store_like_for_post(post_id)
                print(f"Post ID {post_id} liked! New like count: {new_like_count}")
                if new_like_count is not None:
                    return jsonify({'status': 'success', 'message': 'Like successful!'})
                else:
                    return jsonify({'status': 'error', 'message': 'Failed to like the post'})

        else:
            # Handle form data request
            post_id = request.form.get('post_id')
            if post_id:
                # Call the function to store the like in the database
                new_like_count = store_like_for_post(post_id)
                print(f"Post ID {post_id} liked! New like count: {new_like_count}")
                if new_like_count is not None:
                    flash('Like successful!', 'success')
                else:
                    flash('Failed to like the post', 'error')

    image_data_list = get_images_with_username_from_s3(s3_bucket_name)
    
    enumerated_data = list(enumerate(image_data_list))

    

    
    return render_template('test.html', enumerated_data=enumerated_data, image_urls=image_urls)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    
    if request.method == 'GET':
        return render_template('Login.html')
    
    elif request.method == 'POST':
        identifier = request.form.get('identifier')  # This can be either email or username
        password = request.form.get('password')
        
        if identifier is None or not identifier.strip():
            error_message = 'Email or username cannot be empty'
        else:
            result, authentication_error = authenticate_user(identifier, password)
            
            if result:
                user_data = get_user_data(identifier)
                
                if user_data:
                    username = user_data.get('username', {}).get('S', '')  # Extract the 'username' value
                    session['user_identifier']=username
                    flash('Login successful', 'success')
                    # Redirect to the dashboard page on successful login
                    return redirect(url_for('profile', identifier=username))
                else:
                    # Handle the case where user_data is None
                    error_message = 'User data not found'
            else:
                error_message = authentication_error  # Use the specific error from authenticate_user

    return render_template('Login.html', error=error_message)
    
@app.route('/register', methods=['GET','POST'])
def register():
    error_message = None
    success_message = None
    
    if request.method=='GET':
        return render_template("Registration.html")
    
    elif request.method=='POST':
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

                    create_s3_folder(s3_bucket_name, username)
                    success_message = 'Registration Successfull'
                except Exception as e:
                    error_message = f'Registration Failed: {str(e)}'

    # Handle GET requests (initial form load or errors)
    return render_template('Registration.html', error=error_message, success=success_message)

        
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template("upload.html")

    elif request.method == 'POST':
        file = request.files.get('image')

        if file:
            # Call the function to upload the image and create a post
            if upload_image_and_create_post(file):
                flash('Image uploaded successfully!', 'success')
            else:
                flash('Error uploading image', 'error')
        else:
            flash('No image selected', 'error')

        return redirect(url_for('upload'))
   


if __name__ == '__main__':
   
    app.run(debug=True)
