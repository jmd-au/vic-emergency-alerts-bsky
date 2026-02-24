import os
import json
import datetime
import boto3
import logging

sqs_client = boto3.client("sqs")
ddb_client = boto3.client("dynamodb")
LOGGING_LEVEL = os.environ.get("LoggingLevel") or "INFO"
EVENTS_TABLE_NAME = os.environ.get("EVENTS_TABLE_NAME")
EVENTS_TABLE_ARN = os.environ.get("EVENTS_TABLE_ARN")
EVENTS_QUEUE_URL = os.environ.get("EVENTS_QUEUE_URL")
POSTS_QUEUE_URL = os.environ.get("POSTS_QUEUE_URL")
BATCH_SIZE = 10
FILTER_CONDITIONS = {
  "feedType": ["warning"],
  "category1": ["Advice", "Emergency Warning", "Watch and Act", "Flooding", "Flash Flood"],
  "category2": ["Fire", "Met"]
}

logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)

def lambda_handler(event, context):
  messages = event['Records']
  for message in messages:
    messageBody = json.loads(message["body"])
    # check if message already processed
    if check_exists(f"{messageBody['id']}"):
      logger.info(f"message already processed: {messageBody['id']}")
      continue
    # process messages - filter based on required
    else:
      if(all(check_filter_conditions(messageBody))):
        logger.info(f"message meets filter: {messageBody['id']}")
        put_item_to_ddb(messageBody)
        sqs_client.send_message(
          QueueUrl=POSTS_QUEUE_URL,
          MessageBody=json.dumps(messageBody),
          MessageGroupId=f'{messageBody["id"]}',
          MessageDeduplicationId=f'{messageBody["id"]}'
        )
        continue
      else:
        logger.info(f"message does not meet filter: {messageBody['id']}")
        continue
  return None

def put_item_to_ddb(message: dict):
  ddb_client.put_item(
    TableName=EVENTS_TABLE_NAME,
    Item={
      "EventId": {
        "S": f"{message['id']}"
      },
      "RawEvent": {
        "S": f"{json.dumps(message)}"
      },
      "Created": {
        "S": f"{message['created']}"
      },
      "Updated": {
        "S": f"{message['updated']}"
      },
      "ttl_expire": {
        "N": f"{int((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)).timestamp())}"
      }
    }
  )

def check_exists(EventId: str):
  check_exists = ddb_client.scan(
    TableName=EVENTS_TABLE_NAME,
    ExpressionAttributeValues={
      ":recordId": {
        "S": f"{EventId}"
      }
    },
    FilterExpression="EventId = :recordId"
  )
  return bool(check_exists["Count"])

def check_filter_conditions(message: dict):
  finalResult = []
  for key, value in FILTER_CONDITIONS.items():
    if message[key] in value:
      finalResult.append(True)
    else:
      finalResult.append(False)
  return finalResult