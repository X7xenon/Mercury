import os
import json
import ssl
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID", "1306178772583899")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 1. Fetch 3 comments from reel 1
url = f"https://graph.facebook.com/v21.0/18159554401483315/comments?fields=id,text,username,timestamp&limit=3&access_token={PAGE_ACCESS_TOKEN}"
req = urllib.request.Request(url, headers={"User-Agent": "Mercury/1.0"})
with urllib.request.urlopen(req, context=ctx) as resp:
    comments = json.loads(resp.read().decode())
    print("Sample comments:", comments)

if comments.get("data"):
    test_comment = comments["data"][0]
    cid = test_comment["id"]
    print(f"\nTesting Private Reply on comment {cid} ({test_comment.get('username')}, text='{test_comment.get('text')}')...")
    
    post_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = json.dumps({
        "recipient": {"comment_id": cid},
        "message": {"text": "Test"}
    }).encode()
    
    post_req = urllib.request.Request(post_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(post_req, context=ctx) as r:
            print("SUCCESS:", r.read().decode())
    except urllib.error.HTTPError as e:
        print("API Response Error:", e.code, e.read().decode())
