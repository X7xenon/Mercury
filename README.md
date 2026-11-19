# 🔨 ForgeBot: In-House ManyChat Alternative for Instagram & Facebook

**Author:** Abeer Kumar (`@theabeerkumar`)  
**Ecosystem:** The Forge Community (`https://discord.gg/ARxXmTmAV2`)  
**Status:** 100% Operational & Tested with Meta Graph API v21.0  

---

## ⚡ What is ForgeBot?
ForgeBot is a custom, zero-subscription replacement for ManyChat. It connects directly to Meta's official Graph API to automate:
1. **Comment-to-DM (Private Replies):** When someone comments trigger words like `LINK`, `RES`, `AI`, `FORGE`, or `AUDIOBOOK` on any of your Instagram Reels or posts, ForgeBot automatically sends them a private DM with the requested links, GitHub repos, and community invite.
2. **Public Comment Follow-up:** Automatically replies under the comment (e.g. *"Check your DMs! Just sent you the link 📩"*), increasing reel engagement and algorithm signals.
3. **Synergy with "The Forge" Discord:** Every outgoing DM cross-promotes your official community server (`discord.gg/ARxXmTmAV2`).
4. **Synergy with "The Audio Syllabus" YouTube Channel:** Promotes your latest master audiobooks (e.g. *Chanakya Niti*, *Osho*) when users request book/audio content.

---

## 🛠️ Architecture & Components

```
X:\Millionaire\ForgeBot\
├── .env                # Permanent Meta System User Token, Page ID, IG ID
├── triggers.json       # Keyword rules, matching logic, and reply templates
├── meta_api.py         # Official Meta Graph API v21.0 client
├── bot_engine.py       # Core automation logic & keyword matcher
├── database.py         # SQLite tracking database (prevents duplicate DMs)
├── poll_engine.py      # Autonomous local polling worker (Zero setup required)
├── server.py           # FastAPI Webhook server (For real-time Meta Webhooks)
├── run_bot.bat         # 1-Click launcher
└── README.md           # Documentation
```

---

## 🔑 Configured Meta Credentials

* **System User:** `ForgeBotForgeBot` (`ID: 61596617254169` / `122099763261553908`)
* **Facebook Page:** `Abeer Kumar` (`ID: 1306178772583899`)
* **Instagram Business Account:** `theabeerkumar` (`ID: 17841415119954802`)
* **Meta Developer App:** `DM automation` (`ID: 1746074716477366`)
* **System User Access Token:** Permanent (Expiry set to **Never**).

---

## 🚀 How to Run

### Mode 1: Autonomous Local Polling (Recommended — Works Immediately)
Double click `run_bot.bat` or run:
```powershell
python X:\Millionaire\ForgeBot\poll_engine.py
```
* Scans your latest reels/posts every 60 seconds.
* Automatically identifies new comments, checks against `triggers.json`, dispatches DMs, and marks them in `bot_data.db`.
* **Zero port forwarding, zero ngrok, zero server hosting needed!**

### Mode 2: Live Webhook Server (Real-time Instant DMs)
Run:
```powershell
python X:\Millionaire\ForgeBot\server.py
```
* Listens on `http://localhost:8000/webhook`.
* Expose with ngrok (`ngrok http 8000`) and paste the URL into Meta Developer App > Webhooks.
* Verify Token: `ForgeBot_Secret_Verify_Token_2026`.

---

## 📝 Customizing Keywords (`triggers.json`)
You can add new keywords anytime in `triggers.json`:
```json
{
  "keywords": ["NEWKEYWORD"],
  "match_type": "contains",
  "reply_dm": "Hey {username}! Here is your resource: https://...",
  "public_reply": "Check your DMs! 📩"
}
```
