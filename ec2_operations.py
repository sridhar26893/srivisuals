#Created By Sridhar Gundumalla
#700734079

import boto3
import base64

def create_ec2_instance_with_autoscaling_and_apache(
    ami_id,
    instance_type,
    key_name,
    security_group_ids,
    subnet_id,
    min_size,
    max_size,
    desired_capacity,
    launch_template_name,
    autoscaling_group_name,
):
    # Initialize EC2 and Auto Scaling clients
    ec2_client = boto3.client('ec2')
    autoscaling_client = boto3.client('autoscaling')

    # User data script to install and start Apache web server
    user_data_script = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo '<html><h1>Hello, Apache is running!</h1></html>' > /var/www/html/index.html
"""

    # Encode the user data script in base64
    user_data_encoded = base64.b64encode(user_data_script.encode('utf-8')).decode('utf-8')

    # Create a launch template with the encoded user data
    response = ec2_client.create_launch_template(
        LaunchTemplateName=launch_template_name,
        VersionDescription='Initial version',
        LaunchTemplateData={
            'KeyName': key_name,
            'ImageId': ami_id,
            'InstanceType': instance_type,
            'SecurityGroupIds': security_group_ids,
            'UserData': user_data_encoded,  # Use the encoded user data
            'Placement': {
                'GroupName': '',
            },
        },
    )
    launch_template_id = response['LaunchTemplate']['LaunchTemplateId']

    # Create an auto scaling group
    response = autoscaling_client.create_auto_scaling_group(
        AutoScalingGroupName=autoscaling_group_name,
        LaunchTemplate={
            'LaunchTemplateName': launch_template_name,
            'Version': '1',  
        },
        MinSize=min_size,
        MaxSize=max_size,
        DesiredCapacity=desired_capacity,
        VPCZoneIdentifier=subnet_id,
    )

    # Attach the instance to the auto scaling group
    instance_id = response['Instances'][0]['InstanceId']
    autoscaling_client.attach_instances(
        AutoScalingGroupName=autoscaling_group_name,
        InstanceIds=[instance_id],
    )

    print(f"EC2 instance with ID {instance_id} and auto scaling group {autoscaling_group_name} created.")

# Example usage:
create_ec2_instance_with_autoscaling_and_apache(
    ami_id='ami-06d2c6c1b5cbaee5f',  
    instance_type='t2.micro',
    key_name='westkey',
    security_group_ids=['sg-0e57e961d91dc51b7'],  
    subnet_id='	subnet-0600404d233e36cc7',  
    min_size=1,
    max_size=3,
    desired_capacity=1,
    launch_template_name='my-launch-template1',
    autoscaling_group_name='my-auto-scaling-group',
)
