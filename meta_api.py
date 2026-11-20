"""
Mercury Meta Graph API Client for Instagram & Facebook Automation
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
        "User-Agent": "Mercury/1.0",
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


def get_recent_media(limit: int = 25) -> list:
    """Fetch recent posts and reels from the Instagram business account."""
    endpoint = f"{IG_BUSINESS_ACCOUNT_ID}/media?fields=id,caption,media_type,thumbnail_url,media_url,permalink,timestamp,comments_count,like_count&limit={limit}"
    res = _request(endpoint)
    data = res.get("data")
    return data if isinstance(data, list) else []


def get_media_comments(media_id: str) -> list:
    """Fetch comments on a specific post/reel."""
    endpoint = f"{media_id}/comments?fields=id,text,username,timestamp,like_count,user"
    res = _request(endpoint)
    data = res.get("data")
    return data if isinstance(data, list) else []


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


def check_user_follows(user_id: str) -> bool:
    """
    Checks if an Instagram user follows the business account.
    Returns:
      True  -> Verified follower
      False -> Verified non-follower
      None  -> Permission restricted (Meta dev mode) or rate limited
    """
    if not user_id:
        return None
    endpoint = f"{user_id}?fields=id,name,username,is_user_follow_business"
    res = _request(endpoint)
    if "is_user_follow_business" in res:
        return bool(res["is_user_follow_business"])
    return None


def send_private_reply_with_buttons(comment_id: str, text: str, buttons: list = None) -> dict:
    """
    Attempts to send a Button Template private reply to an Instagram comment.
    Falls back gracefully to plain text if template is rejected by Meta endpoint.
    """
    endpoint = f"{PAGE_ID}/messages"
    if buttons:
        payload = {
            "recipient": {
                "comment_id": comment_id
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": text,
                        "buttons": buttons
                    }
                }
            }
        }
        res = _request(endpoint, method="POST", payload=payload)
        if "error" not in res:
            return res

    # Graceful fallback to plain text
    return send_private_reply(comment_id=comment_id, message_text=text)


def send_follow_gate_message(comment_id: str, text: str, account_username: str = "theabeerkumar", user_id: str = None) -> dict:
    """
    Sends an interactive Follow-Gate card with a direct 'Follow @username' button.
    Tapping the button immediately redirects the user to the Instagram profile within the app.
    Falls back gracefully to clean formatted text link if templates are restricted.
    """
    profile_url = f"https://www.instagram.com/{account_username}/"
    buttons = [
        {
            "type": "web_url",
            "url": profile_url,
            "title": f"Follow @{account_username}"
        }
    ]

    # 1. If 24-hr session exists for user_id, try Generic Template card
    if user_id:
        endpoint = f"{PAGE_ID}/messages"
        payload = {
            "recipient": {"id": user_id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": f"Follow @{account_username} to Unlock",
                                "subtitle": "Tap below to visit my profile and hit follow. Then reply 'FOLLOWED' here!",
                                "buttons": buttons
                            }
                        ]
                    }
                }
            }
        }
        res = _request(endpoint, method="POST", payload=payload)
        if "error" not in res:
            return {"status": "success", "mode": "generic_template_user", "res": res}

    # 2. Try Button Template or plain text via comment_id
    res_btn = send_private_reply_with_buttons(comment_id=comment_id, text=text, buttons=buttons)
    return res_btn


def send_two_dms(comment_id: str, message1: str, message2: str, user_id: str = None) -> dict:
    """
    Delivers a 2-message sequence:
    1. If an existing 24-hr session exists (user_id), sends message 1, pauses 1.2s, and sends message 2.
    2. Otherwise delivers message 1 and message 2 sequentially in a clean, dual-bubble layout.
    """
    if user_id:
        # Try sending as two distinct sequential messages
        res1 = send_direct_message(recipient_id=user_id, message_text=message1)
        if "error" not in res1:
            import time
            time.sleep(1.2) # Human-like safe pause
            res2 = send_direct_message(recipient_id=user_id, message_text=message2)
            return {"status": "success", "mode": "dual_direct_messages", "res1": res1, "res2": res2}

    # Combined dual-message layout for comment-to-DM Private Reply
    combined = f"{message1}\n\n───────────────\n\n{message2}"
    res = send_private_reply(comment_id=comment_id, message_text=combined)
    is_success = "error" not in res and bool(res.get("recipient_id") or res.get("message_id"))
    return {"status": "success" if is_success else "error", "mode": "combined_private_reply", "response": res}


if __name__ == "__main__":
    print("Testing Mercury Meta API client...")
    media = get_recent_media(limit=3)
    print(f"Retrieved {len(media)} media items.")
    for m in media:
        print(f"- ID: {m.get('id')} | Comments: {m.get('comments_count')} | Caption: {m.get('caption', '')[:40]}...")
