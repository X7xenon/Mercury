"""
Mercury Autonomous Polling Worker
Periodically scans recent reels and posts for new comments and dispatches ManyChat-style automated DMs.
Runs 100% locally with zero webhook setup required!
"""

import time
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

from meta_api import get_recent_media, get_media_comments
from bot_engine import process_incoming_comment
from database import is_comment_processed, get_all_processed_count


def scan_recent_comments(limit_media: int = 10, dry_run: bool = False):
    """Scan latest posts and process any new comments."""
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scanning recent media...")
    media_list = get_recent_media(limit=limit_media)
    
    if not media_list:
        print("No media returned from Graph API.")
        return 0

    new_comments_count = 0

    for item in media_list:
        media_id = item.get("id")
        caption = (item.get("caption") or "").replace("\n", " ")[:50]
        comments_count = item.get("comments_count", 0)

        # Skip if 0 comments reported
        if comments_count == 0:
            continue

        try:
            comments = get_media_comments(media_id)
        except Exception as e:
            print(f"Error fetching comments for media {media_id}: {e}")
            continue

        if not isinstance(comments, list):
            continue

        for c in comments:
            cid = c.get("id")
            uname = c.get("username", "user")
            text = c.get("text", "")
            from_obj = c.get("from") or c.get("user") or {}
            user_id = from_obj.get("id")

            if not is_comment_processed(cid):
                new_comments_count += 1
                print(f"\n🔔 New Comment Found on Reel [{caption}...]:")
                print(f"   From: @{uname} (ID: {user_id or 'unknown'})")
                print(f"   Comment ID: {cid}")
                print(f"   Text: \"{text}\"")

                if not dry_run:
                    res = process_incoming_comment(
                        comment_id=cid,
                        media_id=media_id,
                        username=uname,
                        comment_text=text,
                        post_public_reply=True,
                        user_id=user_id
                    )
                    print(f"   Result: {res.get('status')}")
                else:
                    print("   [DRY RUN] Would send automated DM and public reply.")

    return new_comments_count


def run_poll_loop(interval_seconds: int = 60):
    print("=" * 60)
    print("☿ Mercury Instagram Automation Engine Started")
    print(f"📡 Polling interval: {interval_seconds}s")
    print(f"📊 Currently processed comments in DB: {get_all_processed_count()}")
    print("=" * 60)

    try:
        while True:
            scan_recent_comments()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nMercury engine stopped by user.")


if __name__ == "__main__":
    # Perform single scan check
    scan_recent_comments(limit_media=10, dry_run=True)
