import boto3
from botocore.exceptions import WaiterError

def create_posts_table(table_name):
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'post_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'post_id',
                    'AttributeType': 'S'  # String
                },
                
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        # Wait until the table is created
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)

        print(f'Table {table_name} created successfully.')
        return table

    except WaiterError as e:
        print(f'Error creating table: {e}')


