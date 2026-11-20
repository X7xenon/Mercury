"""
Mercury Meta Automation Engine (FastAPI)
Real-time Webhook Server, Video Automation Configurator, Performance Tracker, & Dashboard API.
"""

import os
import sys
import json
import re
import time
import threading
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, Response, Query, HTTPException, Body
from fastapi.responses import PlainTextResponse, JSONResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

load_dotenv(dotenv_path=BASE_DIR / ".env")

import meta_api
import bot_engine
import database
import poll_engine
import auth

app = FastAPI(title="Mercury Meta Automation Engine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VERIFY_TOKENS = {
    os.getenv("WEBHOOK_VERIFY_TOKEN", "").strip(),
    "Mercury_Secret_Verify_Token_2026",
    "ForgeBot_Secret_Verify_Token_2026"
}
VERIFY_TOKENS.discard("")

DASHBOARD_FILE = BASE_DIR / "static" / "dashboard.html"

# -------------------------------------------------------------
# AUTONOMOUS BACKGROUND COMMENT REPLIER ENGINE
# -------------------------------------------------------------

REPLIER_ACTIVE = True
LAST_SCAN_AT = None
TOTAL_SCANS = 0
COMMENTS_REPLIED_SESSION = 0
POLL_INTERVAL_SECONDS = 45


def autonomous_polling_worker():
    global LAST_SCAN_AT, TOTAL_SCANS, COMMENTS_REPLIED_SESSION
    print("[MERCURY AUTONOMOUS REPLIER] Polling daemon initiated.")
    time.sleep(3)  # Brief warmup
    while True:
        try:
            if REPLIER_ACTIVE:
                TOTAL_SCANS += 1
                LAST_SCAN_AT = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                new_found = poll_engine.scan_recent_comments(limit_media=12, dry_run=False)
                if new_found > 0:
                    COMMENTS_REPLIED_SESSION += new_found
                    print(f"[AUTONOMOUS REPLIER] {new_found} new comment(s) processed.")
        except Exception as e:
            print(f"[AUTONOMOUS REPLIER ERROR] {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


# Start autonomous daemon thread
_polling_thread = threading.Thread(target=autonomous_polling_worker, daemon=True)
_polling_thread.start()


# -------------------------------------------------------------
# DASHBOARD UI & AUTHENTICATION ROUTES
# -------------------------------------------------------------

@app.get("/favicon.ico")
async def favicon():
    return Response(content=b"", media_type="image/x-icon", status_code=204)


@app.post("/api/auth/login")
async def login(payload: dict = Body(...)):
    username = payload.get("username", "")
    password = payload.get("password", "")
    if not auth.verify_credentials(username, password):
        raise HTTPException(status_code=401, detail="Access denied: Invalid operator credentials")

    token = auth.create_session_token(username)
    resp = JSONResponse(content={"status": "authenticated", "user": username})
    resp.set_cookie(
        key=auth.COOKIE_NAME,
        value=token,
        max_age=auth.SESSION_DURATION_SECONDS,
        httponly=True,
        samesite="lax",
        secure=True if os.getenv("VERCEL") else False,
        path="/"
    )
    return resp


@app.post("/api/auth/logout")
def logout():
    resp = JSONResponse(content={"status": "logged_out"})
    resp.delete_cookie(key=auth.COOKIE_NAME, path="/")
    return resp


@app.get("/api/auth/me")
def get_current_operator(request: Request):
    if not auth.is_authenticated(request):
        raise HTTPException(status_code=401, detail="Unauthenticated")
    return {"authenticated": True, "username": os.getenv("DASHBOARD_USERNAME", "theabeerkumar")}


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    if auth.is_authenticated(request):
        for p in [BASE_DIR / "static" / "dashboard.html", BASE_DIR / "dashboard.html"]:
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read(), status_code=200)
        return HTMLResponse(content="<h1>Mercury Dashboard Loading...</h1>", status_code=200)

    # Operator not authenticated: serve login page
    for p in [BASE_DIR / "static" / "login.html", BASE_DIR / "login.html"]:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(content="<h1>Mercury Authentication Portal Loading...</h1>", status_code=401)


# -------------------------------------------------------------
# REST API: SYSTEM & ANALYTICS
# -------------------------------------------------------------

@app.get("/api/status")
def get_system_status():
    return {
        "status": "online",
        "brand": "Mercury",
        "version": "2.0.0",
        "service": "Mercury Instagram & Meta Growth Automation Engine",
        "instagram_account": "theabeerkumar",
        "page_id": meta_api.PAGE_ID,
        "ig_business_id": meta_api.IG_BUSINESS_ACCOUNT_ID,
        "graph_api_version": meta_api.GRAPH_API_VERSION,
        "processed_comments_total": database.get_all_processed_count(),
        "discord_community": os.getenv("DISCORD_INVITE_URL", "https://discord.gg/ARxXmTmAV2"),
        "webhook_url": "/webhook"
    }


@app.get("/api/analytics")
def get_analytics(request: Request):
    """Returns deep performance metrics for DMs and Comment Replies."""
    auth.require_auth(request)
    summary = database.get_analytics_summary()
    summary["brand"] = "Mercury"
    summary["engine_status"] = "Active & Polling"
    summary["replier_active"] = REPLIER_ACTIVE
    summary["last_scan_at"] = LAST_SCAN_AT or "Starting..."
    summary["total_scans"] = TOTAL_SCANS
    summary["session_processed"] = COMMENTS_REPLIED_SESSION
    return summary


@app.get("/api/replier/status")
def get_replier_status(request: Request):
    auth.require_auth(request)
    return {
        "active": REPLIER_ACTIVE,
        "last_scan_at": LAST_SCAN_AT or "Starting...",
        "total_scans": TOTAL_SCANS,
        "session_processed": COMMENTS_REPLIED_SESSION,
        "interval_seconds": POLL_INTERVAL_SECONDS,
        "total_processed_db": database.get_all_processed_count()
    }


@app.post("/api/replier/toggle")
def toggle_replier_status(request: Request):
    auth.require_auth(request)
    global REPLIER_ACTIVE
    REPLIER_ACTIVE = not REPLIER_ACTIVE
    return {
        "active": REPLIER_ACTIVE,
        "message": "Autonomous comment replier " + ("activated" if REPLIER_ACTIVE else "paused")
    }


# -------------------------------------------------------------
# REST API: VIDEO-SPECIFIC AUTOMATIONS
# -------------------------------------------------------------

@app.get("/api/videos")
def get_videos_with_automation(request: Request):
    """
    Fetches user's Instagram reels/videos from Meta Graph API
    and merges them with configured automations from SQLite DB.
    """
    auth.require_auth(request)
    try:
        remote_media = meta_api.get_recent_media(limit=30)
    except Exception as e:
        remote_media = []

    # Get local automations from DB
    automations = database.get_video_automations()

    # List of all media merged
    items = []
    seen_ids = set()

    # 1. First add any upcoming video presets that aren't yet on Instagram
    for mid, auto in automations.items():
        if auto.get("is_upcoming") == 1:
            items.append({
                "id": mid,
                "caption": auto.get("caption") or "Upcoming Video Preset",
                "permalink": auto.get("permalink") or "#",
                "thumbnail_url": auto.get("thumbnail_url") or "",
                "comments_count": 0,
                "media_type": "UPCOMING",
                "is_upcoming": True,
                "automation": auto
            })
            seen_ids.add(mid)

    # 2. Add real Instagram reels/posts
    for m in remote_media:
        mid = str(m.get("id"))
        auto = automations.get(mid)
        thumb = m.get("thumbnail_url") or m.get("media_url") or ""
        items.append({
            "id": mid,
            "caption": m.get("caption") or "",
            "permalink": m.get("permalink") or "",
            "thumbnail_url": thumb,
            "media_url": m.get("media_url") or "",
            "comments_count": m.get("comments_count", 0),
            "media_type": m.get("media_type", "VIDEO"),
            "timestamp": m.get("timestamp"),
            "is_upcoming": False,
            "automation": auto
        })
        seen_ids.add(mid)

    # 3. Add any other configured automations from DB not already in top 30
    for mid, auto in automations.items():
        if mid not in seen_ids and auto.get("is_active"):
            items.append({
                "id": mid,
                "caption": auto.get("caption") or "",
                "permalink": auto.get("permalink") or "",
                "thumbnail_url": auto.get("thumbnail_url") or "",
                "media_url": "",
                "comments_count": 0,
                "media_type": "VIDEO",
                "timestamp": auto.get("created_at"),
                "is_upcoming": False,
                "automation": auto
            })
            seen_ids.add(mid)

    return {
        "count": len(items),
        "active_automations_count": sum(1 for i in items if i.get("automation") and i["automation"].get("is_active")),
        "videos": items
    }


@app.post("/api/videos/automation")
async def set_video_automation(request: Request, payload: dict = Body(...)):
    auth.require_auth(request)
    """
    Sets or updates custom automation rules for a specific video or upcoming video.
    """
    media_id = payload.get("media_id")
    if not media_id:
        raise HTTPException(status_code=400, detail="media_id is required")

    keywords = payload.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    reply_dm = payload.get("reply_dm", "")
    reply_dm_2 = payload.get("reply_dm_2", "")
    public_reply = payload.get("public_reply", "")
    permalink = payload.get("permalink", "")
    caption = payload.get("caption", "")
    thumbnail_url = payload.get("thumbnail_url", "")
    match_type = payload.get("match_type", "contains")
    is_active = 1 if payload.get("is_active", True) else 0
    is_upcoming = 1 if payload.get("is_upcoming", False) else 0
    enable_follow_gate = 1 if payload.get("enable_follow_gate") else 0
    follow_gate_message = payload.get("follow_gate_message", "")
    unlocked_dm = payload.get("unlocked_dm", "")

    saved = database.save_video_automation(
        media_id=media_id,
        keywords=keywords,
        reply_dm=reply_dm,
        public_reply=public_reply,
        permalink=permalink,
        caption=caption,
        thumbnail_url=thumbnail_url,
        match_type=match_type,
        is_active=is_active,
        is_upcoming=is_upcoming,
        reply_dm_2=reply_dm_2,
        enable_follow_gate=enable_follow_gate,
        follow_gate_message=follow_gate_message,
        unlocked_dm=unlocked_dm
    )

    return {"status": "success", "automation": saved}


@app.delete("/api/videos/automation/{media_id}")
def delete_video_automation_by_path(media_id: str, request: Request):
    auth.require_auth(request)
    success = database.delete_video_automation(media_id)
    return {"status": "deleted" if success else "not_found", "media_id": media_id}


@app.delete("/api/videos/automation")
def delete_video_automation_by_query(request: Request, media_id: str = Query(...)):
    auth.require_auth(request)
    success = database.delete_video_automation(media_id)
    return {"status": "deleted" if success else "not_found", "media_id": media_id}


# -------------------------------------------------------------
# REST API: COMMENTS & DM LOGS
# -------------------------------------------------------------

@app.get("/api/comments")
def get_comments(request: Request, limit: int = 50, search: str = None):
    auth.require_auth(request)
    comments = database.get_recent_processed_comments(limit=limit, search=search)
    return {
        "count": len(comments),
        "comments": comments
    }


@app.delete("/api/comments/{comment_id}")
def delete_comment(comment_id: str, request: Request):
    auth.require_auth(request)
    success = database.delete_processed_comment(comment_id)
    return {"status": "deleted" if success else "not_found", "comment_id": comment_id}


# -------------------------------------------------------------
# REST API: GLOBAL TRIGGERS
# -------------------------------------------------------------

@app.get("/api/triggers")
def get_triggers(request: Request):
    auth.require_auth(request)
    return bot_engine.load_triggers()


@app.post("/api/triggers")
async def save_triggers(request: Request, payload: dict = Body(...)):
    auth.require_auth(request)
    triggers_file = bot_engine.TRIGGERS_FILE
    with open(triggers_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return {"status": "saved", "triggers": payload}


@app.get("/api/cron/poll")
def cron_poll(limit: int = 3):
    """
    Vercel Cron endpoint: triggered automatically by Vercel scheduler or external ping
    to poll for incoming comments on serverless deployment (kept ultra-fast for serverless timeout).
    """
    processed = poll_engine.scan_recent_comments(limit_media=limit, dry_run=False)
    return {
        "status": "success",
        "processed_comments": processed,
        "scanned_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }


# -------------------------------------------------------------
# REST API: INTERACTIVE TESTER & MANUAL ACTIONS
# -------------------------------------------------------------

@app.post("/api/test-trigger")
async def test_trigger(request: Request, payload: dict = Body(...)):
    auth.require_auth(request)
    comment_text = payload.get("comment_text", "")
    media_id = payload.get("media_id", "")
    username = payload.get("username", "creative_builder")

    clean_text = comment_text.upper().strip()
    words = set(re.findall(r"\w+", clean_text))

    # Follow-Gate simulation check
    if words.intersection({"FOLLOWED", "FOLLOW", "DONE", "UNLOCKED"}) or "FOLLOWED" in clean_text:
        pending = database.get_pending_follow_gate(username)
        unlocked_text = (pending.get("unlocked_dm") if pending else "") or "Awesome! Thanks for following @theabeerkumar. Here is your unlocked link:\nhttps://github.com/theabeerkumar"
        return {
            "matched": True,
            "source": "follow_gate_unlock",
            "matched_keyword": "FOLLOWED",
            "is_follow_gate": False,
            "is_unlocked": True,
            "rendered_dm": bot_engine.safe_format(unlocked_text, username),
            "rendered_dm_2": "",
            "rendered_public_reply": "Follow verified! Sent your unlocked link to DMs!"
        }

    match = bot_engine.match_comment(comment_text, media_id=media_id)
    if not match:
        return {
            "matched": False,
            "message": "No rule or keyword matched."
        }

    is_follow_gate = match.get("enable_follow_gate", False)
    if is_follow_gate:
        unlocked_template = match.get("unlocked_dm") or match.get("reply_dm", "")
        database.set_pending_follow_gate(
            username=username,
            user_id="test_sim_id",
            media_id=media_id or "test_media",
            comment_id=f"test_cmt_{int(time.time())}",
            unlocked_dm=unlocked_template
        )
        gate_msg = match.get("follow_gate_message") or (
            "Hey {username}! To unlock this link/guide, please make sure you follow @theabeerkumar first:\n\n"
            "1. Follow: https://www.instagram.com/theabeerkumar/\n"
            "2. Once followed, reply 'FOLLOWED' to this DM to instantly get your link!"
        )
        return {
            "matched": True,
            "source": match.get("source"),
            "matched_keyword": match.get("matched_keyword"),
            "is_follow_gate": True,
            "rendered_dm": bot_engine.safe_format(gate_msg, username),
            "rendered_dm_2": "",
            "unlocked_preview": bot_engine.safe_format(unlocked_template, username),
            "rendered_public_reply": "Check your DMs to unlock the link!"
        }

    reply_dm = bot_engine.safe_format(match.get("reply_dm", ""), username)
    reply_dm_2 = bot_engine.safe_format(match.get("reply_dm_2", ""), username)

    return {
        "matched": True,
        "source": match.get("source"),
        "matched_keyword": match.get("matched_keyword"),
        "is_follow_gate": False,
        "has_two_messages": bool(reply_dm_2),
        "rendered_dm": reply_dm,
        "rendered_dm_2": reply_dm_2,
        "rendered_public_reply": bot_engine.safe_format(match.get("public_reply", ""), username)
    }


@app.post("/api/scan")
def trigger_manual_scan(request: Request):
    auth.require_auth(request)
    """Runs an immediate scan across recent reels for new comments."""
    new_found = poll_engine.scan_recent_comments(limit_media=15, dry_run=False)
    return {
        "status": "completed",
        "new_comments_processed": new_found,
        "total_processed_now": database.get_all_processed_count()
    }


# -------------------------------------------------------------
# OFFICIAL META WEBHOOK HANDLERS
# -------------------------------------------------------------

@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    print(f"[MERCURY WEBHOOK VERIFY] mode={hub_mode}, token={hub_verify_token}, challenge={hub_challenge}")

    if hub_mode == "subscribe" and (hub_verify_token in VERIFY_TOKENS):
        print("✅ Mercury Webhook verified successfully!")
        return PlainTextResponse(content=hub_challenge)
    
    print("❌ Webhook verification failed. Token mismatch.")
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    print(f"\n[MERCURY EVENT RECEIVED] {json.dumps(payload, indent=2)}")

    entry_list = payload.get("entry", [])
    results = []

    for entry in entry_list:
        # 1. Instagram comments changes
        changes = entry.get("changes", [])
        for change in changes:
            field = change.get("field")
            val = change.get("value", {})

            if field == "comments":
                cid = val.get("id")
                text = val.get("text", "")
                media_id = val.get("media", {}).get("id")
                from_user = val.get("from", {})
                username = from_user.get("username", "user")
                user_id = from_user.get("id")

                print(f"📩 Mercury Comment Event: @{username} on media {media_id}: '{text}'")
                res = bot_engine.process_incoming_comment(
                    comment_id=cid,
                    media_id=media_id,
                    username=username,
                    comment_text=text,
                    post_public_reply=True,
                    user_id=user_id
                )
                results.append(res)

        # 2. Direct Messages (messaging events)
        messaging = entry.get("messaging", [])
        for msg_event in messaging:
            sender_id = msg_event.get("sender", {}).get("id")
            msg = msg_event.get("message", {})
            msg_text = msg.get("text", "")
            
            if msg_text and not msg.get("is_echo"):
                print(f"💬 Mercury Direct Message from {sender_id}: '{msg_text}'")
                clean_msg = msg_text.upper().strip()
                words = set(re.findall(r"\w+", clean_msg))

                # If user replied FOLLOWED / DONE / FOLLOW in DM, unlock their pending resource!
                if words.intersection({"FOLLOWED", "FOLLOW", "DONE", "UNLOCKED"}) or "FOLLOWED" in clean_msg:
                    unlocked_gate = database.unlock_follow_gate(user_id=sender_id)
                    if unlocked_gate:
                        unlocked_text = unlocked_gate.get("unlocked_dm") or "Awesome! Thanks for following @theabeerkumar. Here is your unlocked link:\nhttps://github.com/theabeerkumar"
                        print(f"🔓 Follow-Gate unlocked via DM for user {sender_id}! Sending unlocked link...")
                        meta_api.send_direct_message(recipient_id=sender_id, message_text=unlocked_text)
                        results.append({"status": "follow_gate_unlocked_via_dm", "user_id": sender_id})
                        continue

                results.append({"status": "dm_received", "sender": sender_id, "text": msg_text})

    return {"status": "ok", "results": results}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Mercury Meta Automation Server on port {port}...")
    print(f"Dashboard available at: http://localhost:{port}/")
    uvicorn.run(app, host="0.0.0.0", port=port)
