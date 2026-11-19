import os
import json
import ssl
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

REELS = [
    {"name": "Reel 1 (DbsJifchlUi)", "id": "18159554401483315"},
    {"name": "Reel 2 (Dbp5cpJhE08)", "id": "17907781038461021"}
]

def get_all_7d_comments():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)
    
    all_comments = []
    
    for r in REELS:
        url = f"https://graph.facebook.com/v21.0/{r['id']}/comments?fields=id,text,username,timestamp&limit=50&access_token={PAGE_ACCESS_TOKEN}"
        while url:
            req = urllib.request.Request(url, headers={"User-Agent": "Mercury/1.0"})
            with urllib.request.urlopen(req, context=ctx) as resp:
                data = json.loads(resp.read().decode())
            
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
                    c["reel_name"] = r["name"]
                    c["media_id"] = r["id"]
                    all_comments.append(c)
                else:
                    reached_old = True
                    break
            if reached_old:
                break
            url = data.get("paging", {}).get("next")
            
    return all_comments

if __name__ == "__main__":
    comments = get_all_7d_comments()
    print(f"Total comments within 7 days: {len(comments)}")
    # Deduplicate by username
    seen_users = set()
    unique_user_comments = []
    for c in comments:
        u = c.get("username", "").lower()
        if u and u not in seen_users:
            seen_users.add(u)
            unique_user_comments.append(c)
            
    print(f"Unique users: {len(unique_user_comments)}")
    for i, c in enumerate(unique_user_comments, 1):
        print(f"{i:02d}. @{c['username']} ({c['reel_name']}): \"{c['text']}\" [CID: {c['id']}, TS: {c['timestamp']}]")
