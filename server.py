"""
ForgeBot Meta Webhook Server (FastAPI)
Handles official Meta Webhook verification & live event dispatching.
"""

import os
import sys
import json
from pathlib import Path
from fastapi import FastAPI, Request, Response, Query, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR))

load_dotenv(dotenv_path=BASE_DIR / ".env")

from bot_engine import process_incoming_comment
from database import get_all_processed_count

app = FastAPI(title="ForgeBot Meta Automation Engine", version="1.0.0")

VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "ForgeBot_Secret_Verify_Token_2026")


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "ForgeBot ManyChat Alternative",
        "processed_comments_total": get_all_processed_count(),
        "discord_community": os.getenv("DISCORD_INVITE_URL")
    }


@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Meta Webhook Challenge Verification.
    When you configure Webhooks in Meta Developers, Meta calls:
    GET /webhook?hub.mode=subscribe&hub.challenge=...&hub.verify_token=...
    """
    print(f"[WEBHOOK VERIFY] mode={hub_mode}, token={hub_verify_token}, challenge={hub_challenge}")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return PlainTextResponse(content=hub_challenge)
    
    print("❌ Webhook verification failed. Invalid token.")
    raise HTTPException(status_code=403, detail="Verification token mismatch")


@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Receives real-time events from Meta:
    - Instagram comments
    - Instagram / Messenger DMs
    """
    payload = await request.json()
    print(f"\n[EVENT RECEIVED] {json.dumps(payload, indent=2)}")

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

                print(f"📩 Webhook Comment: @{username} on media {media_id}: '{text}'")
                res = process_incoming_comment(
                    comment_id=cid,
                    media_id=media_id,
                    username=username,
                    comment_text=text,
                    post_public_reply=True
                )
                results.append(res)

        # 2. Direct Messages (messaging events)
        messaging = entry.get("messaging", [])
        for msg_event in messaging:
            sender_id = msg_event.get("sender", {}).get("id")
            msg = msg_event.get("message", {})
            msg_text = msg.get("text", "")
            
            if msg_text and not msg.get("is_echo"):
                print(f"💬 Direct Message from {sender_id}: '{msg_text}'")
                # Can be routed to Gemini AI agent
                results.append({"status": "dm_received", "sender": sender_id, "text": msg_text})

    return {"status": "ok", "results": results}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting ForgeBot Webhook Server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
