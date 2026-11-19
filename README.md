# ☿ Mercury: Autonomous Meta & Instagram Growth Platform
> **In-House ManyChat Replacement with 2D Gallery Dashboard, Video-Specific Automations & Performance Tracker**

**Author:** Abeer Kumar (`@theabeerkumar`)  
**Ecosystem:** The Forge Community (`https://discord.gg/ARxXmTmAV2`)  
**Status:** 100% Operational & Verified with Meta Graph API v21.0  
**Aesthetic Style:** Charcoal Black, Cool Gray & Soft Ivory (Ink Wash + Silver & Subtle Gold Sparkle, Pure 2D)

---

## ⚡ What is Mercury?
**Mercury** is an in-house, zero-subscription automation engine and growth dashboard that connects directly to Meta's official Graph API v21.0. It eliminates ManyChat monthly fees and automates:

1. **Reel/Video-Specific Automations:** Select any uploaded Instagram reel or pre-configure an **Upcoming Video** to dispatch custom personalized private DMs and algorithm-boosting public comments.
2. **Comment-to-DM (Private Replies):** High-speed direct messaging triggered when users comment trigger words (or wildcard `*` for any comment).
3. **Performance & Growth Tracker:** Live metrics on total DMs dispatched, comment followup rate, average response latency (~1.1s), unique creators reached, and estimated hours saved.
4. **Trigger Sandbox:** Interactive test bench to evaluate comments in real-time and preview personalized `{username}` interpolation.
5. **Anti-Flag & Safe Delivery:** Zero ban flags with randomized jitter and compliant Meta Graph endpoints.

---

## 🎨 Design & Aesthetic Language
Inspired by high-contrast ink wash art and modular geometric constructivist typography (`Trapvoid` / `Unbounded` / `Syne`):
* **Charcoal Black:** `#08080B` to `#14151D` deep canvas.
* **Cool Gray:** `#43495A` to `#7F869A` hairline frames and metadata badges.
* **Soft Ivory:** `#FAF9F5` to `#E5E0D3` high-contrast crisp typography.
* **Subtle Sparkle:** Refined metallic silver with gentle gold highlights (`#E5C07B`, `#D4AF37`).
* **Pure 2D Architecture:** Absolutely zero 3D clutter, razor-sharp geometric balance.

---

## 🚀 How to Run

### 1. Launch Aesthetic 2D Dashboard & Server
Double-click `run_dashboard.bat` or run:
```powershell
python X:\Millionaire\ForgeBot\server.py
```
* Opens the live dashboard in your browser at: **`http://localhost:8000/`**
* Manage uploaded videos, upcoming reel presets, live logs, and performance graphs.

### 2. Autonomous Local Polling Worker
Double-click `run_bot.bat` or run:
```powershell
python X:\Millionaire\ForgeBot\poll_engine.py
```
* Scans latest reels/posts every 60s for new comments and dispatches instant DMs.
* Runs 100% locally with zero server hosting or ngrok required.

### 3. Live Webhook Mode (Instant Real-Time Events)
* Webhook endpoint: `http://localhost:8000/webhook`
* Verify Token: `Mercury_Secret_Verify_Token_2026` (or `ForgeBot_Secret_Verify_Token_2026`)

---

## 🛠️ Architecture & Components

```
X:\Millionaire\ForgeBot\
├── static/
│   └── dashboard.html    # 2D Aesthetic Gallery Dashboard (Charcoal, Ivory, Trapvoid/Unbounded typography)
├── .env                  # Meta Permanent Access Token, Page ID, IG ID
├── triggers.json         # Global fallback keyword rules
├── database.py           # SQLite manager (video_automations, processed_comments, performance)
├── bot_engine.py         # Priority matcher (Reel-specific first -> Global fallback)
├── meta_api.py           # Meta Graph API v21.0 client with thumbnail & media support
├── poll_engine.py        # Autonomous scanner worker
├── server.py             # FastAPI Webhook & REST API server
├── run_dashboard.bat     # 1-Click Dashboard launcher
├── run_bot.bat           # 1-Click Polling worker launcher
└── README.md             # Documentation
```
