"""
ForgeBot Rules & Automation Engine
Handles keyword matching, DM dispatching, and reply formatting.
"""

import json
import re
from pathlib import Path
from meta_api import send_private_reply, reply_to_comment, send_direct_message
from database import is_comment_processed, mark_comment_processed

TRIGGERS_FILE = Path(__file__).parent / "triggers.json"


def load_triggers():
    with open(TRIGGERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_matching_rule(text: str, triggers: dict) -> dict:
    clean_text = text.upper().strip()
    words = set(re.findall(r"\w+", clean_text))

    for rule in triggers.get("rules", []):
        for kw in rule.get("keywords", []):
            kw_upper = kw.upper()
            if rule.get("match_type") == "exact":
                if clean_text == kw_upper:
                    return rule
            else:  # contains
                if kw_upper in clean_text or kw_upper in words:
                    return rule

    return triggers.get("default_rule", {})


def process_incoming_comment(comment_id: str, media_id: str, username: str, comment_text: str, post_public_reply: bool = True) -> dict:
    """
    Process an Instagram comment:
    1. Check if already processed.
    2. Match keyword.
    3. Send Private Reply DM.
    4. Optionally reply to public comment.
    5. Save to database.
    """
    if is_comment_processed(comment_id):
        return {"status": "skipped", "reason": "already_processed", "comment_id": comment_id}

    triggers = load_triggers()
    rule = find_matching_rule(comment_text, triggers)

    if not rule:
        return {"status": "no_match", "comment_id": comment_id}

    reply_dm = rule.get("reply_dm", "").format(username=username or "there")
    public_reply = rule.get("public_reply", "").format(username=username or "there")

    print(f"\n[TRIGGER MATCH] User: @{username} | Comment: '{comment_text}'")
    print(f"[DISPATCHING DM] Text: {reply_dm[:60]}...")

    # 1. Send Private Reply DM
    dm_res = send_private_reply(comment_id=comment_id, message_text=reply_dm)
    print(f"[DM RESULT] {dm_res}")

    # 2. Public Reply (Optional)
    pub_res = None
    if post_public_reply and public_reply:
        pub_res = reply_to_comment(comment_id=comment_id, reply_text=public_reply)
        print(f"[PUBLIC REPLY RESULT] {pub_res}")

    # 3. Mark processed
    mark_comment_processed(
        comment_id=comment_id,
        media_id=media_id,
        username=username,
        comment_text=comment_text,
        reply_sent=reply_dm
    )

    return {
        "status": "success",
        "comment_id": comment_id,
        "username": username,
        "dm_response": dm_res,
        "public_response": pub_res
    }
