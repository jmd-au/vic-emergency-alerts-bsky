import sys
import os
import json
import datetime
import boto3
import logging
import urllib3

ssm_client = boto3.client("ssm")
LOGGING_LEVEL = os.environ.get("LoggingLevel") or "INFO"

DATA_LAST_UPDATED_TIMESTAMP = os.environ.get("DATA_LAST_UPDATED_TIMESTAMP").split("parameter")[-1]
DATA_LAST_UPDATED_HASH = os.environ.get("DATA_LAST_UPDATED_HASH").split("parameter")[-1]

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.3650.139"
      }
    )

    if(get_last_update.status == 200):
      
      timestamp_newer = (datetime.datetime.now(datetime.timezone.utc) > datetime.datetime.fromisoformat(last_updated_timestamp))
      if(timestamp_newer):
        ssm_client.put_parameter(
          Name=DATA_LAST_UPDATED_TIMESTAMP,
          Value=f"{json.dumps(get_last_update.json()["lastModified"])}",
          Overide=True
        )

      if(last_updated_hash != json.dumps(get_last_update.json()["lastHash"])):
        ssm_client.put_parameter(
          Name=DATA_LAST_UPDATED_HASH,
          Value=f"{json.dumps(get_last_update.json()["lastHash"])}",
          Overide=True
        )

    else:
      logger.info(f'emv_get_last_updated FAILED. Request error: `{get_last_update.text}`')
      logger.error(f'{sys.exc_info()[0]}')
  except:
    logger.info(f'emv_get_last_updated FAILED. Last data saved to SSM: `lastModified: {last_updated_timestamp}`, `lastHash: {last_updated_hash}')
    logger.error(f'{sys.exc_info()[0]}')
  return None
