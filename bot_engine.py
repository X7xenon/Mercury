"""
Mercury Rules & Automation Engine
Handles keyword matching, DM dispatching, and reply formatting.
"""

import os
import tempfile
import json
import re
from pathlib import Path
import meta_api
import database
from meta_api import send_private_reply, reply_to_comment, send_direct_message
from database import is_comment_processed, mark_comment_processed, get_video_automation

if os.getenv("VERCEL"):
    TRIGGERS_FILE = Path(tempfile.gettempdir()) / "triggers.json"
    bundled_triggers = Path(__file__).parent / "triggers.json"
    if not TRIGGERS_FILE.exists() and bundled_triggers.exists():
        import shutil
        try:
            shutil.copy2(bundled_triggers, TRIGGERS_FILE)
        except Exception:
            pass
else:
    TRIGGERS_FILE = Path(__file__).parent / "triggers.json"


def load_triggers():
    with open(TRIGGERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_matching_rule(text: str, triggers: dict) -> dict:
    clean_text = text.upper().strip()
    words = set(re.findall(r"\w+", clean_text))

    for rule in triggers.get("rules", []):
        for kw in rule.get("keywords", []):
            kw_upper = kw.upper().strip()
            if rule.get("match_type") == "exact":
                if clean_text == kw_upper:
                    return rule
            else:  # contains
                if kw_upper in clean_text or kw_upper in words:
                    return rule

    return triggers.get("default_rule", {})


def match_comment(comment_text: str, media_id: str = None) -> dict:
    """
    Find matching rule:
    1. Checks video-specific automation first (if media_id provided).
    2. Fallbacks to global triggers in triggers.json.
    """
    if media_id:
        video_rule = get_video_automation(media_id)
        if video_rule and video_rule.get("is_active"):
            keywords = video_rule.get("keywords", [])
            match_type = video_rule.get("match_type", "contains")
            clean_text = comment_text.upper().strip()
            words = set(re.findall(r"\w+", clean_text))

            base_res = {
                "source": f"video:{media_id}",
                "caption": video_rule.get("caption", ""),
                "reply_dm": video_rule.get("reply_dm", ""),
                "reply_dm_2": video_rule.get("reply_dm_2", ""),
                "enable_follow_gate": bool(video_rule.get("enable_follow_gate")),
                "follow_gate_message": video_rule.get("follow_gate_message", ""),
                "unlocked_dm": video_rule.get("unlocked_dm", ""),
                "public_reply": video_rule.get("public_reply", "")
            }

            # Match wildcard or empty keywords = matches all comments on this video
            if not keywords or "*" in keywords or match_type == "any":
                base_res["matched_keyword"] = "ANY_COMMENT"
                return base_res

            for kw in keywords:
                kw_upper = kw.upper().strip()
                if match_type == "exact" and clean_text == kw_upper:
                    base_res["matched_keyword"] = kw
                    return base_res
                elif kw_upper in clean_text or kw_upper in words:
                    base_res["matched_keyword"] = kw
                    return base_res

    # Fallback to global triggers
    triggers = load_triggers()
    rule = find_matching_rule(comment_text, triggers)
    if rule:
        return {
            "source": "global",
            "reply_dm": rule.get("reply_dm", ""),
            "reply_dm_2": rule.get("reply_dm_2", ""),
            "enable_follow_gate": False,
            "public_reply": rule.get("public_reply", ""),
            "matched_keyword": rule.get("keywords", ["DEFAULT"])[0] if rule.get("keywords") else "DEFAULT"
        }

    return None


def safe_format(template: str, username: str) -> str:
    """Safe token interpolator that never crashes on unmatched braces."""
    if not template:
        return ""
    u = username or "there"
    return template.replace("{username}", u).replace("{name}", u)


def process_incoming_comment(
    comment_id: str,
    media_id: str,
    username: str,
    comment_text: str,
    post_public_reply: bool = True,
    user_id: str = None
) -> dict:
    """
    Process an Instagram comment:
    1. Check if comment is a Follow-Gate confirmation ('FOLLOWED', 'DONE').
    2. Check if already processed.
    3. Match video-specific rule or global keyword.
    4. Handle Follow-Gate logic & 2-message sequence.
    5. Dispatch DM & Public Reply.
    6. Save to database.
    """
    clean_text = comment_text.upper().strip()
    words = set(re.findall(r"\w+", clean_text))

    # --- 1. Follow-Gate Unlock Check ---
    follow_confirm_tokens = {"FOLLOWED", "FOLLOW", "DONE", "UNLOCKED", "YES"}
    if words.intersection(follow_confirm_tokens) or "FOLLOWED" in clean_text:
        pending = database.get_pending_follow_gate(username)
        if pending and pending.get("status") == "pending":
            database.unlock_follow_gate(username)
            unlocked_template = pending.get("unlocked_dm") or "Awesome! Thanks for following @theabeerkumar. Here is your link:\nhttps://github.com/theabeerkumar"
            unlocked_text = safe_format(unlocked_template, username)
            
            print(f"\n[FOLLOW-GATE UNLOCKED] User: @{username} confirmed follow!")
            dm_res = send_private_reply(comment_id=comment_id, message_text=unlocked_text)
            
            pub_res = None
            if post_public_reply:
                pub_res = reply_to_comment(comment_id=comment_id, reply_text="Verified! Sent your unlocked link to DMs!")

            mark_comment_processed(
                comment_id=comment_id,
                media_id=media_id,
                username=username,
                comment_text=comment_text,
                reply_sent=unlocked_text
            )
            return {
                "status": "follow_gate_unlocked",
                "username": username,
                "comment_id": comment_id,
                "dm_response": dm_res,
                "public_response": pub_res
            }

    if is_comment_processed(comment_id):
        return {"status": "skipped", "reason": "already_processed", "comment_id": comment_id}

    rule = match_comment(comment_text, media_id=media_id)
    if not rule:
        return {"status": "no_match", "comment_id": comment_id}

    # --- 2. Follow-Gate Check for this Reel ---
    is_gate_active = rule.get("enable_follow_gate", False)
    if is_gate_active:
        user_already_unlocked = database.is_user_unlocked(username, media_id)
        api_follows = meta_api.check_user_follows(user_id) if user_id else None

        if not user_already_unlocked and api_follows is not True:
            # User must follow first!
            unlocked_content = rule.get("unlocked_dm") or rule.get("reply_dm") or "Here is your link: https://github.com/theabeerkumar"
            database.set_pending_follow_gate(
                username=username,
                media_id=media_id,
                comment_id=comment_id,
                unlocked_dm=unlocked_content,
                user_id=user_id or ""
            )

            gate_prompt = rule.get("follow_gate_message") or (
                "Hey {username}! To unlock this link/guide, please follow @theabeerkumar first:\n\n"
                "1. Follow: https://www.instagram.com/theabeerkumar/\n"
                "2. Once followed, reply 'FOLLOWED' to this DM to instantly get your link!"
            )
            reply_dm = safe_format(gate_prompt, username)
            public_reply = "Check your DMs to unlock the link!"

            print(f"\n[FOLLOW-GATE SENT] User: @{username} | Asking to follow @theabeerkumar")
            dm_res = meta_api.send_follow_gate_message(
                comment_id=comment_id,
                text=reply_dm,
                account_username="theabeerkumar",
                user_id=user_id
            )
            
            pub_res = None
            if post_public_reply and public_reply:
                pub_res = reply_to_comment(comment_id=comment_id, reply_text=public_reply)

            mark_comment_processed(
                comment_id=comment_id,
                media_id=media_id,
                username=username,
                comment_text=comment_text,
                reply_sent=reply_dm
            )
            return {
                "status": "follow_gate_sent",
                "username": username,
                "comment_id": comment_id,
                "dm_response": dm_res,
                "public_response": pub_res
            }

    # --- 3. Standard / 2-Message DM Sequence Dispatch ---
    reply_dm = safe_format(rule.get("reply_dm", ""), username)
    reply_dm_2 = safe_format(rule.get("reply_dm_2", ""), username)
    public_reply = safe_format(rule.get("public_reply", ""), username)

    print(f"\n[MERCURY TRIGGER] User: @{username} | Media: {media_id} | Source: {rule.get('source')}")
    print(f"[COMMENT] '{comment_text}' -> Matched: {rule.get('matched_keyword')}")

    if reply_dm_2:
        print(f"[DISPATCHING 2-MESSAGE DM SEQUENCE]")
        dm_res = meta_api.send_two_dms(
            comment_id=comment_id,
            message1=reply_dm,
            message2=reply_dm_2,
            user_id=user_id
        )
    else:
        print(f"[DISPATCHING SINGLE DM] Text: {reply_dm[:60]}...")
        dm_res = send_private_reply(comment_id=comment_id, message_text=reply_dm)

    print(f"[DM RESULT] {dm_res}")

    # Check if DM was delivered successfully
    dm_succeeded = False
    if isinstance(dm_res, dict):
        if dm_res.get("status") == "success":
            inner_res = dm_res.get("response", {})
            if isinstance(inner_res, dict) and "error" not in inner_res:
                dm_succeeded = True
            elif "error" not in dm_res:
                dm_succeeded = True
        elif bool(dm_res.get("recipient_id") or dm_res.get("message_id")):
            dm_succeeded = True

    # Public Reply (only post if DM was actually delivered)
    pub_res = None
    if post_public_reply and public_reply and dm_succeeded:
        pub_res = reply_to_comment(comment_id=comment_id, reply_text=public_reply)
        print(f"[PUBLIC REPLY RESULT] {pub_res}")

    # Mark processed
    mark_comment_processed(
        comment_id=comment_id,
        media_id=media_id,
        username=username,
        comment_text=comment_text,
        reply_sent=f"{reply_dm} | {reply_dm_2}" if reply_dm_2 else reply_dm
    )

    return {
        "status": "success",
        "comment_id": comment_id,
        "username": username,
        "source": rule.get("source"),
        "matched_keyword": rule.get("matched_keyword"),
        "has_two_messages": bool(reply_dm_2),
        "dm_response": dm_res,
        "public_response": pub_res
    }
