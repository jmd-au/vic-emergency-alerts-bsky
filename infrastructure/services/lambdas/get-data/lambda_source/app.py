import sys
import os
import json
import boto3
import logging
import urllib3

sqs_client = boto3.client("sqs")
USER_AGENT = os.environ.get("USER_AGENT_STRING")
LOGGING_LEVEL = os.environ.get("LoggingLevel") or "INFO"
EVENTS_QUEUE_URL = os.environ.get("EVENTS_QUEUE_URL")

logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)

def lambda_handler(event, context):
  try:
    request = urllib3.request(
      "GET",
      "https://emergency.vic.gov.au/public/events-geojson.json",
      headers={
        "User-Agent": f"{USER_AGENT}"
      }
    )
    if(request.status == 200):
      for item in request.json()["features"]:
        item["properties"].pop("webBody", None)
        item["properties"].pop("webHeadline", None)
        sqs_client.send_message(
          QueueUrl=EVENTS_QUEUE_URL,
          MessageBody=json.dumps(item["properties"]),
          MessageGroupId=f'{item["properties"]["id"]}',
          MessageDeduplicationId=f'{item["properties"]["id"]}'
        )
        logger.info(f'Event {item["properties"]["id"]} sent to queue.')
  except:
    logger.info(f'emv_get_last_updated FAILED.')
    logger.error(f'{sys.exc_info()[0]}')
  return None
