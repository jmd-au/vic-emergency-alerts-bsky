import sys
import os
import json
import time
import boto3
import logging
import urllib3

ssm_client = boto3.client("ssm")
ddb_client = boto3.client("dynamodb")
LOGGING_LEVEL = os.environ.get("LoggingLevel") or "INFO"
BSKY_HANDLE = os.environ.get("BSKY_HANDLE").split("parameter")[-1]
BSKY_SECRET = os.environ.get("BSKY_SECRET").split("parameter")[-1]
BSKY_JWT = os.environ.get("BSKY_JWT").split("parameter")[-1]
BSKY_REFRESH_JWT = os.environ.get("BSKY_REFRESH_JWT").split("parameter")[-1]

logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)

def lambda_handler(event, context):
  bsky_handle = ssm_client.get_parameter(Name=BSKY_HANDLE,WithDecryption=True).get("Parameter").get("Value")
  bsky_secret = ssm_client.get_parameter(Name=BSKY_SECRET,WithDecryption=True).get("Parameter").get("Value")
  bsky_jwt = ssm_client.get_parameter(Name=BSKY_JWT, WithDecryption=True).get("Parameter").get("Value")
  bsky_refresh_jwt = ssm_client.get_parameter(Name=BSKY_REFRESH_JWT, WithDecryption=True).get("Parameter").get("Value")
  
  logger.info(get_current_atproto_session(bsky_jwt))

  # if(get_current_atproto_session(bsky_jwt)[1] == 400]):
  #   create_atproto_session(bsky_handle, bsky_secret)
  # elif(get_current_atproto_session(bsky_jwt)[1] == 400 && ):
  #   refresh_atproto_session(bsky_refresh_jwt, bsky_jwt)
  
  # send_post = urllib3.request(
  #     "POST",
  #     "https://emergency.vic.gov.au/public/osom-delta.json",
  #     headers={
  #       "User-Agent": USER_AGENT
  #     }
  #   )
  # create_atproto_session(bsky_handle, bsky_secret)
  # refresh_atproto_session(bsky_refresh_jwt, bsky_jwt)
  return None


def create_atproto_session(bsky_handle: str, bsky_secret: str):
  try:
    request = urllib3.request(
      "POST",
      "https://bsky.social/xrpc/com.atproto.server.createSession",
      headers={
        "Content-Type": "application/json"
      },
      json={
        "identifier": bsky_handle,
        "password": bsky_secret
      }
    )
    ssm_client.put_parameter(
      Name=BSKY_JWT,
      Value=request.json().get("accessJwt"),
      Type="SecureString",
      Overwrite=True
    )
    ssm_client.put_parameter(
      Name=BSKY_REFRESH_JWT,
      Value=request.json().get("refreshJwt"),
      Type="SecureString",
      Overwrite=True
    )
    logger.info(f"Session created for user: {request.json().get("handle")} ({request.json().get("did")})")
  except:
    logger.error("Error creating session")
    logger.error(f'{sys.exc_info()[0]}')
  return None


def refresh_atproto_session(bsky_refresh_jwt: str, bsky_jwt: str):
  try:
    request = urllib3.request(
      "POST",
      "https://bsky.social/xrpc/com.atproto.server.refreshSession",
      headers={
        "Authorization": f"Bearer {bsky_refresh_jwt}",
        "Content-Type": "application/json"
      }
    )
    ssm_client.put_parameter(
      Name=BSKY_JWT,
      Value=request.json().get("accessJwt"),
      Type="SecureString",
      Overwrite=True
    )
    ssm_client.put_parameter(
      Name=BSKY_REFRESH_JWT,
      Value=request.json().get("refreshJwt"),
      Type="SecureString",
      Overwrite=True
    )
    logger.info(f"Session refreshed for user: {request.json().get("handle")} ({request.json().get("did")})")
  except:
    logger.error("Error refreshing session")
    logger.error(f'{sys.exc_info()[0]}')
  return request.json()

def get_current_atproto_session(bsky_jwt: str):
  try:
    request = urllib3.request(
      "GET",
      "https://bsky.social/xrpc/com.atproto.server.getSession",
      headers={
        "Authorization": f"Bearer {bsky_jwt}",
        "Content-Type": "application/json"
      }
    )
    logger.info(f"Session retrieved for user: {request.json().get("handle")} ({request.json().get("did")})")
  except:
    logger.error("Error retrieving session")
    logger.error(f'{sys.exc_info()[0]}')
  return [request.json().get("did") or None, request.status or None]