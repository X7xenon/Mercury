"""
ForgeBot: Targeted XenClips DMs Dispatcher with Anti-Ban / Anti-Flag Guardrails.
Sends personalized automated DMs to users who commented on XenClips reels.
"""

import os
import sys
import json
import time
import random
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

load_dotenv(dotenv_path=BASE_DIR / ".env")

from database import is_comment_processed, mark_comment_processed

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID", "1306178772583899")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

REELS = [
    {"name": "Reel 1 (DbsJifchlUi)", "id": "18159554401483315"},
    {"name": "Reel 2 (Dbp5cpJhE08)", "id": "17907781038461021"}
]

MESSAGE_TEMPLATE = """Hey! Thanks for showing interest in XenClips!

Here's the video where I explain everything about it:
https://youtu.be/JFh1Onb6OmM

Also, I'd really appreciate it if you could subscribe to my YouTube channel and follow along for more projects, experiments and things I'm building.

Thanks for the support!

Also, I've started a little community for like-minded creators, builders and people who love experimenting with technology and creating things.

The idea is to connect, share projects, exchange ideas and grow together.

Would love to have you join us!

Join here:
https://www.instagram.com/channel/butuNaXRRCP7Y0SB/"""


def get_eligible_comments(days_limit=7):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days_limit)
    
    eligible = []
    seen_users = set()
    
    # Mark test comment from samuelpee10 as processed so we don't repeat
    seen_users.add("samuelpee10")

    for r in REELS:
        url = f"https://graph.facebook.com/v21.0/{r['id']}/comments?fields=id,text,username,timestamp&limit=50&access_token={PAGE_ACCESS_TOKEN}"
        while url:
            req = urllib.request.Request(url, headers={"User-Agent": "ForgeBot/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                    data = json.loads(resp.read().decode())
            except Exception as e:
                print(f"Error fetching comments for {r['name']}: {e}")
                break

            items = data.get("data", [])
            if not items:
                break

            reached_old = False
            for c in items:
                ts_str = c.get("timestamp")
                if not ts_str:
                    continue
                dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if dt >= cutoff:
                    uname = (c.get("username") or "").lower()
                    cid = c.get("id")
                    
                    # Deduplicate user & skip already processed
                    if uname and uname not in seen_users and not is_comment_processed(cid):
                        seen_users.add(uname)
                        c["reel_name"] = r["name"]
                        c["media_id"] = r["id"]
                        eligible.append(c)
                else:
                    reached_old = True
                    break

            if reached_old:
                break
            url = data.get("paging", {}).get("next")

    return eligible


def send_private_reply(comment_id: str, text: str) -> dict:
    url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = json.dumps({
        "recipient": {"comment_id": comment_id},
        "message": {"text": text}
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return {"success": True, "data": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return {"success": False, "status": e.code, "error": error_body}
    except Exception as e:
        return {"success": False, "status": 500, "error": str(e)}


def run_batch_sender(min_delay=10.0, max_delay=16.0):
    print("=" * 65)
    print("🛡️ FORGEBOT SAFE XENCLIPS DM DISPATCHER (ANTI-FLAG MODE)")
    print(f"⏱️ Random delay between DMs: {min_delay}s - {max_delay}s")
    print("=" * 65)

    eligible = get_eligible_comments(days_limit=7)
    total = len(eligible)
    print(f"\nFound {total} eligible unique commenters within the 7-day Meta policy window.\n")

    if total == 0:
        print("No new comments to process.")
        return

    sent_count = 0
    failed_count = 0

    for idx, c in enumerate(eligible, 1):
        uname = c.get("username", "user")
        cid = c.get("id")
        text = c.get("text", "")
        media_id = c.get("media_id")
        reel = c.get("reel_name")

        print(f"[{idx}/{total}] Processing @{uname} ({reel})...")
        print(f"       Comment: \"{text}\"")

        res = send_private_reply(comment_id=cid, text=MESSAGE_TEMPLATE)

        if res.get("success"):
            sent_count += 1
            data = res.get("data", {})
            mid = data.get("message_id", "sent")
            print(f"       ✅ DM DELIVERED! (Message ID: {mid[:35]}...)")
            mark_comment_processed(
                comment_id=cid,
                media_id=media_id,
                username=uname,
                comment_text=text,
                reply_sent=MESSAGE_TEMPLATE
            )
        else:
            failed_count += 1
            print(f"       ❌ FAILED: {res.get('error')}")

        # Anti-flag jitter delay if more remaining
        if idx < total:
            delay = round(random.uniform(min_delay, max_delay), 2)
            print(f"       ⏳ Anti-flag cooldown: sleeping {delay}s...")
            time.sleep(delay)

    print("\n" + "=" * 65)
    print(f"🎉 BATCH COMPLETE: {sent_count} Delivered, {failed_count} Failed.")
    print("=" * 65)


if __name__ == "__main__":
    run_batch_sender(min_delay=10.0, max_delay=16.0)
