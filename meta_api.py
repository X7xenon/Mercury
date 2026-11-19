"""
Meta Graph API Client for Instagram & Facebook Automation
Handles Private Replies, Comment Fetching, Direct Messaging, and Public Comment Replies.
"""

import os
import json
import ssl
import urllib.request
import urllib.error
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID", "1306178772583899")
IG_BUSINESS_ACCOUNT_ID = os.getenv("IG_BUSINESS_ACCOUNT_ID", "17841415119954802")
GRAPH_API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# SSL Context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def _request(endpoint: str, method: str = "GET", payload: dict = None) -> dict:
    url = f"{BASE_URL}/{endpoint}"
    separator = "&" if "?" in url else "?"
    url_with_token = f"{url}{separator}access_token={PAGE_ACCESS_TOKEN}"

    headers = {
        "User-Agent": "ForgeBot/1.0",
        "Content-Type": "application/json"
    }

    data = None
    if payload:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url_with_token, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[API ERROR {e.code}] {endpoint}: {error_body}")
        try:
            return {"error": e.code, "detail": json.loads(error_body)}
        except Exception:
            return {"error": e.code, "raw": error_body}
    except Exception as e:
        print(f"[NET ERROR] {endpoint}: {str(e)}")
        return {"error": 500, "message": str(e)}


def get_recent_media(limit: int = 15) -> list:
    """Fetch recent posts and reels from the Instagram business account."""
    endpoint = f"{IG_BUSINESS_ACCOUNT_ID}/media?fields=id,caption,media_type,timestamp,permalink,comments_count&limit={limit}"
    res = _request(endpoint)
    return res.get("data", [])


def get_media_comments(media_id: str) -> list:
    """Fetch comments on a specific post/reel."""
    endpoint = f"{media_id}/comments?fields=id,text,username,timestamp,like_count,user"
    res = _request(endpoint)
    return res.get("data", [])


def send_private_reply(comment_id: str, message_text: str) -> dict:
    """
    Send a direct message to a user who commented on a post/reel (ManyChat core mechanism).
    Official Meta Private Replies API:
    POST /{PAGE_ID}/messages with recipient: { comment_id }
    """
    endpoint = f"{PAGE_ID}/messages"
    payload = {
        "recipient": {
            "comment_id": comment_id
        },
        "message": {
            "text": message_text
        }
    }
    return _request(endpoint, method="POST", payload=payload)


def reply_to_comment(comment_id: str, reply_text: str) -> dict:
    """Post a public reply under a user's comment."""
    endpoint = f"{comment_id}/replies"
    payload = {
        "message": reply_text
    }
    return _request(endpoint, method="POST", payload=payload)


def send_direct_message(recipient_id: str, message_text: str) -> dict:
    """Send a direct message in an open 24-hour window."""
    endpoint = f"{PAGE_ID}/messages"
    payload = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    }
    return _request(endpoint, method="POST", payload=payload)


if __name__ == "__main__":
    print("Testing Meta API client...")
    media = get_recent_media(limit=3)
    print(f"Retrieved {len(media)} media items.")
    for m in media:
        print(f"- ID: {m.get('id')} | Comments: {m.get('comments_count')} | Caption: {m.get('caption', '')[:40]}...")
