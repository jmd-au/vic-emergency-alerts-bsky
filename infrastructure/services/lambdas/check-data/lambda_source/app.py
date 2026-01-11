import sys
import os
import json
import datetime
import boto3
import logging
import urllib3

ssm_client = boto3.client("ssm")
lambda_client = boto3.client("lambda")
LOGGING_LEVEL = os.environ.get("LoggingLevel") or "INFO"
USER_AGENT = os.environ.get("USER_AGENT")
DATA_LAST_UPDATED_TIMESTAMP = os.environ.get("DATA_LAST_UPDATED_TIMESTAMP").split("parameter")[-1]
DATA_LAST_UPDATED_HASH = os.environ.get("DATA_LAST_UPDATED_HASH").split("parameter")[-1]
EVENTS_LAMBDA_ARN = os.environ.get("EVENTS_LAMBDA_ARN")
EVENTS_LAMBDA_NAME = os.environ.get("EVENTS_LAMBDA_NAME")

logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)

def lambda_handler(event, context):
  last_updated_timestamp = ssm_client.get_parameter(Name=DATA_LAST_UPDATED_TIMESTAMP,WithDecryption=True).get("Parameter").get("Value")
  last_updated_hash = ssm_client.get_parameter(Name=DATA_LAST_UPDATED_HASH,WithDecryption=True).get("Parameter").get("Value")

  try:
    get_last_update = urllib3.request(
      "GET",
      "https://emergency.vic.gov.au/public/osom-delta.json",
      headers={
        "User-Agent": USER_AGENT
      }
    )

    if(get_last_update.status == 200):
      timestamp_newer = (datetime.datetime.fromisoformat(json.dumps(get_last_update.json()["lastModified"]).strip('"')) > datetime.datetime.fromisoformat(f'{last_updated_timestamp.strip('"')}'))
      if(timestamp_newer):
        ssm_client.put_parameter(
          Name=DATA_LAST_UPDATED_TIMESTAMP,
          Value=f"{json.dumps(get_last_update.json()["lastModified"])}",
          Overwrite=True
        )
        logger.info(f'INFO: Timestamp updated, SSM Parameter updated with new timestamp: {json.dumps(get_last_update.json()["lastModified"])}')
      else:
        logger.info('INFO: Timestamp still the same, no update necessary.')

      if(last_updated_hash != json.dumps(get_last_update.json()["lastHash"])):
        ssm_client.put_parameter(
          Name=DATA_LAST_UPDATED_HASH,
          Value=f"{json.dumps(get_last_update.json()["lastHash"])}",
          Overwrite=True
        )
        logger.info(f'INFO: Hash updated, SSM Parameter updated with new hash: {json.dumps(get_last_update.json()["lastHash"])}')
      else:
        logger.info(f'INFO: Hash still the same, no update necessary.')
      
      if(timestamp_newer and last_updated_hash == json.dumps(get_last_update.json()["lastHash"])):
        lambda_client.invoke(
          FunctionName=EVENTS_LAMBDA_NAME,
          InvocationType='Event',
          LogType='None',
          Payload='{}'
        )
    else:
      logger.info(f'emv_get_last_updated FAILED. Request error: `{get_last_update.text}`')
      logger.error(f'{sys.exc_info()[0]}')
  except:
    logger.info(f'emv_get_last_updated FAILED. Last data saved to SSM: `lastModified: {last_updated_timestamp}`, `lastHash: {last_updated_hash}`, request response: `{get_last_update.text}`')
    logger.error(f'{sys.exc_info()[0]}')
  return None
