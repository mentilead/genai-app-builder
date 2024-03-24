import time

import boto3
import os

from boto3.dynamodb.conditions import Key


class BaseDynamoDBModel:
    def __init__(self, table_name):
        self.session = boto3.session.Session()
        self.dynamodb_resource = self.session.resource('dynamodb',
                                                       region_name=os.getenv('REGION_NAME'),
                                                       aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                                       aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                                                       endpoint_url='http://localhost:4000')
        self.table = self.dynamodb_resource.Table(table_name)

    def get_item(self, key):
        # Basic functionality for getting an item from the table
        response = self.table.get_item(Key=key)
        return response['Item']

    # Other common operations like put, update, delete, etc.


class MentorSessionDDB(BaseDynamoDBModel):
    def __init__(self):
        super().__init__('MentorSession')

    def insert(self, user_id, create_date, mentoring_data_json):
        self.table.put_item(
            Item={
                'user_id': user_id,
                'create_date': create_date,
                'mentoring_data': mentoring_data_json
            }
        )
        self.insert_history(user_id, create_date, create_date, mentoring_data_json)

    def update(self, user_id, create_date, mentoring_data_json):
        self.table.update_item(
            Key={'user_id': user_id, 'create_date': create_date},
            UpdateExpression='SET mentoring_data = :mentoring_data',
            ExpressionAttributeValues={':mentoring_data': mentoring_data_json}
        )
        history_date = int(time.time())
        self.insert_history(user_id, create_date, history_date, mentoring_data_json)


    @staticmethod
    def insert_history(user_id, create_date, history_date, mentoring_data_json):
        mentor_session_history_ddb = MentorSessionHistoryDDB()
        mentor_session_id = f"{user_id}-{create_date}"
        mentor_session_history_ddb.insert(mentor_session_id, history_date, mentoring_data_json)

    def query_with_paging(self, user_id, page_size, exclusive_start_key):
        if exclusive_start_key:
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ExclusiveStartKey=exclusive_start_key,
                ScanIndexForward=False,  # This parameter makes the sorting in descending order
                Limit=page_size  # Limit parameter for paging. Modify limit as per your requirements
            )
        else:
            response = self.table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=False,  # This parameter makes the sorting in descending order
                Limit=page_size  # Limit parameter for paging. Modify limit as per your requirements
            )

        return response



class MentorSessionHistoryDDB(BaseDynamoDBModel):
    def __init__(self):
        super().__init__('MentorSessionHistory')

    def insert(self, mentor_session_id, history_date, mentoring_data_json):
        self.table.put_item(
            Item={
                'mentor_session_id': mentor_session_id,
                'history_date': history_date,
                'mentoring_data': mentoring_data_json
            }
        )

    def query_with_paging(self, mentor_session_id, page_size, exclusive_start_key):
        if exclusive_start_key:
            response = self.table.query(
                KeyConditionExpression=Key('mentor_session_id').eq(mentor_session_id),
                ExclusiveStartKey=exclusive_start_key,
                ScanIndexForward=False,  # This parameter makes the sorting in descending order
                Limit=page_size  # Limit parameter for paging. Modify limit as per your requirements
            )
        else:
            response = self.table.query(
                KeyConditionExpression=Key('mentor_session_id').eq(mentor_session_id),
                ScanIndexForward=False,  # This parameter makes the sorting in descending order
                Limit=page_size  # Limit parameter for paging. Modify limit as per your requirements
            )
        return response
