import os
import json
import ssl
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID", "1306178772583899")
IG_ID = os.getenv("IG_BUSINESS_ACCOUNT_ID", "17841415119954802")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ForgeBot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "detail": e.read().decode()}
    except Exception as e:
        return {"error": str(e)}

def find_target_reels():
    shortcodes = ["DbsJifchlUi", "Dbp5cpJhE08"]
    url = f"https://graph.facebook.com/v21.0/{IG_ID}/media?fields=id,caption,permalink,timestamp,comments_count&limit=50&access_token={PAGE_ACCESS_TOKEN}"
    
    found = {}
    
    while url and len(found) < len(shortcodes):
        data = fetch_json(url)
        if "error" in data:
            print("Error fetching media:", data)
            break
        
        for item in data.get("data", []):
            permalink = item.get("permalink", "")
            for code in shortcodes:
                if code in permalink:
                    found[code] = item
                    print(f"✅ Found reel {code}: ID {item['id']}, Comments: {item.get('comments_count', 0)}")
                    print(f"   Caption: {item.get('caption', '')[:60]}...")
                    print(f"   Timestamp: {item.get('timestamp')}")
                    
        url = data.get("paging", {}).get("next")
        
    return found

if __name__ == "__main__":
    reels = find_target_reels()
    print("\n--- Summary of Found Reels ---")
    print(json.dumps(reels, indent=2))
