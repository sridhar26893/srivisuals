import boto3
def create_ec2_instance():
    
    try:
        print ("Creating EC2 instance")
        resource_ec2 = boto3.client("ec2")
        resource_ec2.run_instances(
            ImageId="ami-06d2c6c1b5cbaee5f",
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            KeyName="westkey"
        )
    except Exception as e:
        print(e)