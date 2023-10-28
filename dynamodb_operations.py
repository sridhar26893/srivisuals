import boto3

def create_dynamodb_table(table_name, region='us-east-1'):
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name=region)

        # Define the KeySchema and AttributeDefinitions as needed for your table
        key_schema = [
            {
                'AttributeName': 'email',
                'KeyType': 'HASH'  # PARTITION KEY
            },
            {
                'AttributeName': 'username',
                'KeyType': 'RANGE'  # SORT KEY
            }
        ]

        attribute_definitions = [
            {
                'AttributeName': 'email',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            }
        ]

        # Define provisioned throughput settings (adjust as needed)
        provisioned_throughput = {
            'ReadCapacityUnits': 30,
            'WriteCapacityUnits': 30
        }

        global_secondary_indexes = [
            {
                'IndexName': 'EmailIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'email',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            },
            {
                'IndexName': 'UsernameIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'username',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            }
        ]

                
        # Create the DynamoDB table with Global Secondary Indexes
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput,
            GlobalSecondaryIndexes=global_secondary_indexes
            
        )

        print(f"Table '{table_name}' creation initiated")

        # Wait for the table to exist
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(
            TableName=table_name,
            WaiterConfig={'Delay': 5, 'MaxAttempts': 20}
        )

        print(f"Table '{table_name}' created successfully!")

    except Exception as e:
        print(f"Error creating table: {e}")


