import sys
import os
import json
import boto3
import logging
import urllib3
import re
from datetime import datetime, timezone
from typing import List, Dict
from bs4 import BeautifulSoup

ssm_client = boto3.client("ssm")
sqs_client = boto3.client("sqs")
ddb_client = boto3.client("dynamodb")
LOGGING_LEVEL = os.environ.get("LoggingLevel") or "INFO"

EVENTS_TABLE_NAME = os.environ.get("EVENTS_TABLE_NAME")
POSTS_QUEUE_URL = os.environ.get("POSTS_QUEUE_URL")

BSKY_HANDLE = os.environ.get("BSKY_HANDLE").split("parameter")[-1]
BSKY_DID = os.environ.get("BSKY_DID").split("parameter")[-1]
BSKY_SECRET = os.environ.get("BSKY_SECRET").split("parameter")[-1]
BSKY_JWT = os.environ.get("BSKY_JWT").split("parameter")[-1]
BSKY_REFRESH_JWT = os.environ.get("BSKY_REFRESH_JWT").split("parameter")[-1]

logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)

def lambda_handler(event, context):
  bsky_handle = ssm_client.get_parameter(Name=BSKY_HANDLE,WithDecryption=True).get("Parameter").get("Value")
  bsky_did = ssm_client.get_parameter(Name=BSKY_DID,WithDecryption=True).get("Parameter").get("Value")
  bsky_secret = ssm_client.get_parameter(Name=BSKY_SECRET,WithDecryption=True).get("Parameter").get("Value")
  bsky_jwt = ssm_client.get_parameter(Name=BSKY_JWT, WithDecryption=True).get("Parameter").get("Value")
  bsky_refresh_jwt = ssm_client.get_parameter(Name=BSKY_REFRESH_JWT, WithDecryption=True).get("Parameter").get("Value")  

  messages = sqs_client.receive_message(
    QueueUrl=POSTS_QUEUE_URL
  )

  for message in messages["Records"]:
    logger.info(f"message: {json.dumps(message)}")

  event_id = "40602"
  post_text = "TEST ALERT"

  messages = event['Records']
  for message in messages:
    messageBody = json.loads(message["body"])
    # check if message already processed
    if check_exists(f"{messageBody['id']}"):
      logger.info(f"message already processed: {messageBody['id']}")
      continue


  # if(get_current_atproto_session(bsky_jwt)[1] == 400):
  #   logger.info("Creating new session...")
  #   create_atproto_session(bsky_handle, bsky_secret)
  #   create_post(
  #       text=post_text,
  #       session_jwt=bsky_jwt,
  #       session_did=bsky_did,
  #       embed_url=f'https://emergency.vic.gov.au/respond/#!/warning/{event_id}/moreinfo?ref=vic-emergencyalert.bsky.social',
  #     )
  # else:
  #   logger.info("Refreshing session...")
  #   refresh_atproto_session(bsky_refresh_jwt, bsky_jwt)
  #   create_post(
  #       text=post_text,
  #       session_jwt=bsky_jwt,
  #       session_did=bsky_did,
  #       embed_url=f'https://emergency.vic.gov.au/respond/#!/warning/{event_id}/moreinfo',
  #     )
  return None

def create_post(text: str, session_jwt: str, session_did: str, embed_url=None):
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    post = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
    }

    # parse out mentions and URLs as "facets"
    if len(text) > 0:
        facets = parse_facets(post["text"])
        if facets:
            post["facets"] = facets
    if embed_url != None:
      post["embed"] = fetch_embed_url_card(
        session_jwt, embed_url
      )

    logger.info(f"creating post: {json.dumps(post, indent=2)}")

    resp = urllib3.request("POST",
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + session_jwt},
        json={
            "repo": session_did,
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )
    logger.info(f"createRecord response: {json.dumps(resp.json())}")

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
    ssm_client.put_parameter(
      Name=BSKY_DID,
      Value=request.json().get("did"),
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

#
#   Upload helpers
#

def fetch_embed_url_card(access_token: str, url: str) -> Dict:
    # the required fields for an embed card
    card = {
        "uri": url,
        "title": "",
        "description": "",
    }

    # fetch the HTML
    resp = urllib3.request("GET", url)
    soup = BeautifulSoup(resp.data, "html.parser")

    title_tag = soup.find("meta", property="og:title")
    if title_tag:
        card["title"] = title_tag["content"]

    description_tag = soup.find("meta", property="og:description")
    if description_tag:
        card["description"] = description_tag["content"]

    image_tag = soup.find("meta", property="og:image")
    if image_tag:
        img_url = image_tag["content"]
        if "://" not in img_url:
            img_url = url + img_url
        resp = urllib3.request("GET", img_url)
        card["thumb"] = upload_file(access_token, resp.data)

    return {
        "$type": "app.bsky.embed.external",
        "external": card,
    }

def upload_file(access_token, img_bytes) -> Dict:
  try:
    mimetype = "image/png"

    resp = urllib3.request(
        "POST",
        "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
        headers={
            "Content-Type": mimetype,
            "Authorization": "Bearer " + access_token,
        },
        body=img_bytes,
    )
    return resp.json()["blob"]
  except:
    logger.error("Error uploading file")
    logger.error(f'{sys.exc_info()[0]}')

#
#   Parsing methods
#

def parse_facets(text: str) -> List[Dict]:
    facets = []
    for m in parse_mentions(text):
        resp = urllib3.request("GET",
            "https://bsky.social/xrpc/com.atproto.identity.resolveHandle",
            params={"handle": m["handle"]},
        )
        # If the handle can't be resolved, just skip it!
        # It will be rendered as text in the post instead of a link
        if resp.status_code == 400:
            continue
        did = resp.json()["did"]
        facets.append({
            "index": {
                "byteStart": m["start"],
                "byteEnd": m["end"],
            },
            "features": [{"$type": "app.bsky.richtext.facet#mention", "did": did}],
        })
    for u in parse_urls(text):
        facets.append({
            "index": {
                "byteStart": u["start"],
                "byteEnd": u["end"],
            },
            "features": [
                {
                    "$type": "app.bsky.richtext.facet#link",
                    # NOTE: URI ("I") not URL ("L")
                    "uri": u["url"],
                }
            ],
        })
    return facets

def parse_mentions(text: str) -> List[Dict]:
    spans = []
    # regex based on: https://atproto.com/specs/handle#handle-identifier-syntax
    mention_regex = rb"[$|\W](@([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"
    text_bytes = text.encode("UTF-8")
    for m in re.finditer(mention_regex, text_bytes):
        spans.append(
            {
                "start": m.start(1),
                "end": m.end(1),
                "handle": m.group(1)[1:].decode("UTF-8"),
            }
        )
    return spans

def parse_urls(text: str) -> List[Dict]:
    spans = []
    # partial/naive URL regex based on: https://stackoverflow.com/a/3809435
    # tweaked to disallow some training punctuation
    url_regex = rb"[$|\W](https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*[-a-zA-Z0-9@%_\+~#//=])?)"
    text_bytes = text.encode("UTF-8")
    for m in re.finditer(url_regex, text_bytes):
        spans.append(
            {
                "start": m.start(1),
                "end": m.end(1),
                "url": m.group(1).decode("UTF-8"),
            }
        )
    return spans

def parse_uri(uri: str) -> Dict:
    if uri.startswith("at://"):
        repo, collection, rkey = uri.split("/")[2:5]
        return {"repo": repo, "collection": collection, "rkey": rkey}
    elif uri.startswith("https://bsky.app/"):
        repo, collection, rkey = uri.split("/")[4:7]
        if collection == "post":
            collection = "app.bsky.feed.post"
        elif collection == "lists":
            collection = "app.bsky.graph.list"
        elif collection == "feed":
            collection = "app.bsky.feed.generator"
        return {"repo": repo, "collection": collection, "rkey": rkey}
    else:
        raise Exception("unhandled URI format: " + uri)

def get_reply_refs(pds_url: str, parent_uri: str) -> Dict:
    uri_parts = parse_uri(parent_uri)
    resp = urllib3.request(
        "GET",
        "https://bsky.social/xrpc/com.atproto.repo.getRecord",
        params=uri_parts,
    )
    parent = resp.json()
    root = parent
    parent_reply = parent["value"].get("reply")
    if parent_reply is not None:
        root_uri = parent_reply["root"]["uri"]
        root_repo, root_collection, root_rkey = root_uri.split("/")[2:5]
        resp = urllib3.request(
            "GET",
            "https://bsky.social/xrpc/com.atproto.repo.getRecord",
            params={
                "repo": root_repo,
                "collection": root_collection,
                "rkey": root_rkey,
            },
        )
        root = resp.json()

    return {
        "root": {
            "uri": root["uri"],
            "cid": root["cid"],
        },
        "parent": {
            "uri": parent["uri"],
            "cid": parent["cid"],
        },
    }

def get_embed_ref(pds_url: str, ref_uri: str) -> Dict:
    uri_parts = parse_uri(ref_uri)
    resp = urllib3.request(
        "GET",
        "https://bsky.social/xrpc/com.atproto.repo.getRecord",
        params=uri_parts,
    )
    print(resp.json())
    resp.raise_for_status()
    record = resp.json()

    return {
        "$type": "app.bsky.embed.record",
        "record": {
            "uri": record["uri"],
            "cid": record["cid"],
        },
    }

#
#   DynamoDB Helpers
#

def update_item_ddb(message: dict):
  response = users_table.update_item(
        Key={"email": "test1@example.com"},
        UpdateExpression="set #name = :n",
        ExpressionAttributeNames={
            "#name": "name",
        },
        ExpressionAttributeValues={
            ":n": "John Doe",
        },
        ReturnValues="UPDATED_NEW",
    )
  ddb_client.update_item(
    TableName=EVENTS_TABLE_NAME,
    Key={
      "EventId": f"{message['id']}"
    },
    UpdateExpression="set #",


    Item={
      "EventId": {
        "S": f"{message['id']}"
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