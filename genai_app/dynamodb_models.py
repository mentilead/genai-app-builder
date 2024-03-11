import boto3

class BaseDynamoDBModel:
    def __init__(self, table_name, region_name='your-region',
                 aws_access_key_id='your-key-id', aws_secret_access_key='your-secret-key'):
        self.session = boto3.session.Session()
        self.dynamodb_resource = self.session.resource('dynamodb',
                                                       region_name=region_name,
                                                       aws_access_key_id=aws_access_key_id,
                                                       aws_secret_access_key=aws_secret_access_key)
        self.table = self.dynamodb_resource.Table(table_name)

    def get_item(self, key):
        # Basic functionality for getting an item from the table
        response = self.table.get_item(Key=key)
        return response['Item']

    # Other common operations like put, update, delete, etc.


class UserMentoringDynamoDBModel(BaseDynamoDBModel):
    def __init__(self, *args, **kwargs):
        super().__init__('UserMentoring', *args, **kwargs)

    def get_usermentoring_info_by_id(self, user_id):
        # This is an example of a specific method for this table
        # More complex queries and operations specific to UserMentoring go here
        pass

# Don't forget to replace 'your-key-id', 'your-secret-key', 'your-region'
# with your AWS key id, secret key and DynamoDB region.