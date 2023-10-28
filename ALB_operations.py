#Created by Sridhar Gundumalla
#700734079

import boto3

def create_application_load_balancer(load_balancer_name, subnets, security_groups):
    elbv2_client = boto3.client('elbv2')

    # Create the ALB
    response = elbv2_client.create_load_balancer(
        Name=load_balancer_name,
        Subnets=subnets,
        SecurityGroups=security_groups,
        Scheme='internet-facing',
        )  # Set to 'internal' for internal load balancer
        
    

    # Get the ARN of the created load balancer
    load_balancer_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    print(f"Application Load Balancer created with ARN: {load_balancer_arn}")


load_balancer_name = 'SVALB'
subnets = ['subnet-0600404d233e36cc7', 'subnet-0ec8d869071e3a2ef']  # Replace with your subnet IDs
security_groups = ['sg-0e57e961d91dc51b7']  # Replace with your security group IDs

create_application_load_balancer(load_balancer_name, subnets, security_groups)
