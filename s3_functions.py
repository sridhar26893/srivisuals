#Created by Sridhar Gundumalla
#700734079

import boto3
import os

# Initialize the S3 client
s3 = boto3.client('s3')
region = "us-east-2"

# Function for creating an S3 bucket
def create_bucket(bucket_name, location):
    try:
        result = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print(f"S3 Bucket successfully created: {bucket_name}")
        return result
    except Exception as e:
        print(f"An error occurred while creating the bucket: {str(e)}")
        



def upload_folder_to_s3(local_folder_path, bucket_name):
    
    s3 = boto3.client('s3')

    # Iterate through the local folder and upload each file
    for root, _, files in os.walk(local_folder_path):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            # Calculate the S3 object key by removing the local folder path
            s3_object_key = os.path.relpath(local_file_path, local_folder_path)

            # Upload the file to S3
            try:
                s3.upload_file(local_file_path, bucket_name, s3_object_key)
                print(f"Uploaded '{local_file_path}' to '{bucket_name}/{s3_object_key}'")
            except Exception as e:
                print(f"Failed to upload '{local_file_path}' to '{bucket_name}/{s3_object_key}': {str(e)}")





