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

def fetch_recent_comments(media_id, days=7):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    
    url = f"https://graph.facebook.com/v21.0/{media_id}/comments?fields=id,text,username,timestamp&limit=50&access_token={PAGE_ACCESS_TOKEN}"
    
    valid_comments = []
    total_scanned = 0
    
    while url:
        req = urllib.request.Request(url, headers={"User-Agent": "Mercury/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                data = json.loads(resp.read().decode())
        except Exception as e:
            print("Error fetching:", e)
            break
            
        items = data.get("data", [])
        if not items:
            break
            
        total_scanned += len(items)
        reached_old = False
        
        for c in items:
            ts_str = c.get("timestamp")
            if not ts_str:
                continue
            # Parse ISO 8601
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if dt >= cutoff:
                valid_comments.append(c)
            else:
                reached_old = True
                break
                
        if reached_old:
            break
            
        url = data.get("paging", {}).get("next")
        
    return valid_comments, total_scanned

if __name__ == "__main__":
    for r in REELS:
        comments, scanned = fetch_recent_comments(r["id"], days=7)
        print(f"=== {r['name']} ===")
        print(f"Total scanned: {scanned}, Comments within last 7 days: {len(comments)}")
        for c in comments[:10]:
            print(f"  @{c.get('username')}: \"{c.get('text')}\" ({c.get('timestamp')}) [ID: {c.get('id')}]")
        print()
