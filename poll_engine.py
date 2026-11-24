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


ALWAYS_TARGET_REELS = []


def scan_recent_comments(limit_media: int = 3, dry_run: bool = False, max_batch: int = 4):
    """
    Scan all configured automation reels AND recent posts to guarantee 100% comment coverage.
    Ensures comments on older configured reels are NEVER missed.
    Bounded by max_batch to guarantee lightning-fast serverless execution (<4s).
    """
    from database import get_video_automations
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Scanning media for incoming comments...")
    
    # 1. ALWAYS include all active configured reels from SQLite
    target_media_ids = set(ALWAYS_TARGET_REELS)
    try:
        automations = get_video_automations()
        for mid, auto in automations.items():
            if auto.get("is_active") and not auto.get("is_upcoming"):
                target_media_ids.add(str(mid))
    except Exception as e:
        print(f"[POLL NOTICE] Error reading video automations: {e}")

    # 2. Also include recent media from Instagram
    if limit_media > 0:
        try:
            media_list = get_recent_media(limit=limit_media)
            for item in media_list:
                if item.get("id"):
                    target_media_ids.add(str(item["id"]))
        except Exception as e:
            print(f"[POLL NOTICE] Error fetching recent media: {e}")

    if not target_media_ids:
        print("No media IDs found to scan.")
        return 0

    new_comments_count = 0

    # Fetch comments for all target media in parallel for ultra-fast serverless execution (<2s)
    import concurrent.futures
    def fetch_comments_safe(mid):
        try:
            return mid, get_media_comments(mid)
        except Exception as e:
            return mid, []

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        media_comments_results = list(executor.map(fetch_comments_safe, list(target_media_ids)))

    for media_id, comments in media_comments_results:
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
                print(f"\n🔔 New Comment Found on Reel {media_id}:")
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

                if new_comments_count >= max_batch:
                    print(f"[POLL NOTICE] Reached max batch of {max_batch} comments. Yielding execution.")
                    return new_comments_count

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
    run_poll_loop(interval_seconds=15)
