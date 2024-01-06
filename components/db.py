import boto3
import os


# dynamoDBの設定
dynamodb = boto3.resource(
  'dynamodb', 
  region_name='ap-northeast-1', 
  aws_access_key_id='AKIAWDQHRTRMNTVDMJFB',
  aws_secret_access_key='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'
)
client = boto3.client(
  'dynamodb', 
  region_name='ap-northeast-1', 
  aws_access_key_id='AKIAWDQHRTRMNTVDMJFB', 
  aws_secret_access_key='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'
)


class DB():
  def __init__(self, table_name, line_user_id):
    self.table = dynamodb.Table(table_name)
    self.line_user_id = line_user_id


  def get_item_if_exists(self):
    response = self.table.get_item(Key={'SessionId': self.line_user_id})
    item = response.get('Item', None)
    if item:
      return item.get('job_msg', '')
    else:
      return ''


  def update_job_msg(self, new_job_msg):
    if new_job_msg != 'NullQuery' and new_job_msg != '':
      self.table.update_item(
        Key={'SessionId': self.line_user_id},
        UpdateExpression='SET job_msg = :val',
        ExpressionAttributeValues={
          ':val': new_job_msg
        },
        ReturnValues='UPDATED_NEW'
      )
      return True
    else:
      if self.table.get_item(Key={'SessionId': self.line_user_id}):
        self.table.get_item(Key={'SessionId': self.line_user_id})
      return False


  def manage_history(self, k=5):
    num_chat = 2 * k
    response = self.table.get_item(Key={'SessionId': self.line_user_id})
    item = response.get('Item', None)
    if item:
      histories = item.get('History', [])
      # 最新の履歴のみを保持
      if len(histories) > num_chat:
        histories = histories[-num_chat:]
      # 履歴の更新
      self.table.update_item(
        Key={'SessionId': self.line_user_id},
        UpdateExpression='SET History = :val',
        ExpressionAttributeValues={
          ':val': histories
        },
        ReturnValues='UPDATED_NEW'
      )