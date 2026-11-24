# ☿ Mercury: Complete Setup & Deployment Guide

> **Zero-Subscription, Self-Hosted Meta & Instagram Growth Platform**  
> *Official Step-by-Step Production Guide from Zero to Live Deployment*

---

## 📋 Table of Contents
1. [Overview & Core Architecture](#1-overview--core-architecture)
2. [Prerequisites Checklist](#2-prerequisites-checklist)
3. [Phase 1: Meta Developer Portal & App Creation](#phase-1-meta-developer-portal--app-creation)
4. [Phase 2: Connecting Facebook Page & Instagram Account](#phase-2-connecting-facebook-page--instagram-account)
5. [Phase 3: Generating a Permanent System User Token](#phase-3-generating-a-permanent-system-user-token)
6. [Phase 4: Finding Your Numeric IDs](#phase-4-finding-your-numeric-ids)
7. [Phase 5: Local Installation & Running Mercury](#phase-5-local-installation--running-mercury)
8. [Phase 6: In-App Credentials & Live Connection Test](#phase-6-in-app-credentials--live-connection-test)
9. [Phase 7: Live Webhook Setup (Instant Real-Time Mode)](#phase-7-live-webhook-setup-instant-real-time-mode)
10. [Phase 8: Autonomous Polling Daemon (Zero-Port Mode)](#phase-8-autonomous-polling-daemon-zero-port-mode)
11. [Phase 9: Creating Video Automations & Follow-Gates](#phase-9-creating-video-automations--follow-gates)
12. [Phase 10: Serverless Cloud Deployment (Vercel)](#phase-10-serverless-cloud-deployment-vercel)
13. [Security, Privacy & Data Compliance](#security-privacy--data-compliance)
14. [Troubleshooting & Frequently Asked Questions](#troubleshooting--frequently-asked-questions)

---

## 1. Overview & Core Architecture

Mercury connects directly to Meta's official **Graph API v21.0**. It replaces ManyChat by providing:
* **Comment-to-DM Private Replies:** Dispatches direct messages in response to public comments on your Reels and Posts within ~1.1 seconds.
* **Algorithm-Boosting Public Replies:** Simultaneously drops contextual public comments under users' comments to trigger Instagram's viral ranking algorithm.
* **Dual-Message Sequence:** Sends a two-part structured message (e.g. Greeting + Resource Link) with natural human pause to prevent spam filtering.
* **Follow-Gate Unlocking:** Asks non-followers to follow your profile first, and automatically unlocks secret links once they reply `FOLLOWED` in DM.
* **2D Aesthetic Dashboard:** Ultra-fast, zero-framework, hardware-accelerated dashboard styled in high-contrast Charcoal Black (`#08080B`), Cool Gray (`#43495A`), Soft Ivory (`#FAF9F5`), and Accent Purple (`#8B6CFF`).

---

## 2. Prerequisites Checklist

Before you begin, ensure you have:
1. **Python 3.9 or higher** installed (`python --version`).
2. An **Instagram Professional Account** (Creator or Business) — personal accounts do not support Graph API.
3. A **Facebook Page** linked to that Instagram account (required by Meta's Graph API structure).
4. A **Meta Developer Account** (free registration at [developers.facebook.com](https://developers.facebook.com)).

---

## Phase 1: Meta Developer Portal & App Creation

### Step 1.1: Register as a Meta Developer
1. Visit [Meta for Developers](https://developers.facebook.com/) and log in with the Facebook account that owns your Facebook Page.
2. Complete developer registration if this is your first time.

### Step 1.2: Create a Business App
1. Click **My Apps** > **Create App**.
2. When asked *"What do you want your app to do?"*, select **Other**, then click **Next**.
3. Select **Business** as the App Type.
4. Give your app a display name (e.g. `Mercury Growth Studio`) and enter your contact email.
5. Click **Create App** and complete the security check.

### Step 1.3: Add Required Products
1. In the App Dashboard sidebar, click **Add Product**.
2. Find **Instagram Graph API** and click **Set Up**.
3. Find **Webhooks** and click **Set Up**.

---

## Phase 2: Connecting Facebook Page & Instagram Account

Meta requires your Instagram account to be connected to a Facebook Page:
1. Open your Facebook Page on desktop.
2. Go to **Settings & Privacy** > **Settings** > **Linked Accounts**.
3. Click **Instagram** and click **Connect Account**.
4. Log into your Instagram account and toggle **Allow access to Instagram messages in Inbox** to **ON**.
5. Ensure your Instagram account is switched to a **Professional (Creator or Business)** account.

---

## Phase 3: Generating a Permanent System User Token

> [!IMPORTANT]
> User Access Tokens generated from Graph API Explorer expire after 1 to 60 days. System User Access Tokens **never expire**, making them mandatory for reliable 24/7 automation.

### Step 3.1: Open Meta Business Suite Settings
1. Go to [Meta Business Suite Settings](https://business.facebook.com/settings).
2. Select your Business Account.

### Step 3.2: Create a System User
1. In the left navigation, navigate to **Users** > **System Users**.
2. Click **Add**.
3. Enter a System Username: `mercury-operator`.
4. Role: Select **Admin**.
5. Click **Create System User**.

### Step 3.3: Assign Assets to the System User
1. Click **Add Assets** on the newly created System User.
2. Under **Pages**, select your Facebook Page and grant **Full Control (Manage Page)**.
3. Under **Instagram Accounts**, select your Instagram account and grant **Full Control**.
4. Click **Save Changes**.

### Step 3.4: Generate the Permanent Token
1. Click **Generate New Token**.
2. Select your App (`Mercury Growth Studio`).
3. Set Token Expiration to: **Never**.
4. Check the following **6 essential permissions**:
   * `instagram_basic`
   * `instagram_manage_comments`
   * `instagram_manage_messages`
   * `pages_manage_metadata`
   * `pages_read_engagement`
   * `pages_show_list`
5. Click **Generate Token**.
6. Copy the token immediately (starts with `EAAY...` or `EAA...`). Store it safely in your password manager.

---

## Phase 4: Finding Your Numeric IDs

Mercury requires two numeric IDs to route messages accurately:

### Finding Facebook Page ID (`PAGE_ID`):
1. Open your Facebook Page in a browser.
2. Click **About** > **Page Transparency** or inspect the URL.
3. Your numeric **Page ID** is displayed (e.g. `1306178772583899`).

### Finding Instagram Business Account ID (`IG_BUSINESS_ACCOUNT_ID`):
1. Go to the [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2. Select your App and paste your System User Token.
3. In the query box, enter:
   ```text
   GET /v21.0/me/accounts?fields=id,name,instagram_business_account
   ```
4. Click **Submit**. The JSON response will show:
   ```json
   {
     "data": [
       {
         "id": "1306178772583899",
         "name": "Your Page Name",
         "instagram_business_account": {
           "id": "17841415119954802"
         }
       }
     ]
   }
   ```
5. Note down both `PAGE_ID` and `instagram_business_account.id`.

---

## Phase 5: Local Installation & Running Mercury

### 5.1 Clone the Codebase
```bash
git clone https://github.com/X7xenon/ForgeBot.git
cd ForgeBot
```

### 5.2 Install Python Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5.3 Configure Environment Template (Optional)
You can configure credentials directly through the web UI in Phase 6, or pre-seed them in `.env`:
```bash
# Copy template
cp .env.example .env
```
Fill in your credentials:
```env
PAGE_ACCESS_TOKEN=your_permanent_access_token_here
PAGE_ID=your_page_id_here
IG_BUSINESS_ACCOUNT_ID=your_instagram_account_id_here
APP_ID=your_app_id_here
WEBHOOK_VERIFY_TOKEN=Mercury_Secret_Verify_Token_2026
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=YourSecurePassword123!
```

### 5.4 Launch Mercury Dashboard & Server
```bash
# Windows 1-Click Launcher:
run_dashboard.bat

# Or via Command Line:
python server.py
```
* Mercury starts at: **`http://localhost:8000/`**
* Log in with your configured `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD`.

---

## Phase 6: In-App Credentials & Live Connection Test

Mercury features a built-in configuration UI so you never have to edit code or restart servers when updating tokens:

1. Open **`http://localhost:8000`** in your browser.
2. In the left navigation, click **`Credentials & Tokens`**.
3. Enter your:
   * **Page Access Token** (use the *Show Token* or *Paste* button).
   * **Instagram Business Account ID**
   * **Facebook Page ID**
   * **Your Instagram Handle** (`@your_handle`)
   * **Dashboard Password** (optional update)
4. Click **`Test Connection`**.
   * Mercury performs a live handshake with Meta Graph API v21.0.
   * If successful, an inline diagnostic box confirms your Facebook Page Name, Instagram Account Handle, and token validity.
5. Click **`Save Credentials`**. The settings are persisted in SQLite `bot_data.db` and synchronized to `.env` dynamically.

---

## Phase 7: Live Webhook Setup (Instant Real-Time Mode)

For zero-latency instant replies (~1.1 seconds from user comment to DM):

### Step 7.1: Expose Your Local Server (if running locally)
If running locally, expose port 8000 using Cloudflare Tunnel or ngrok:
```bash
# Using Cloudflare Tunnel:
cloudflared tunnel --url http://localhost:8000

# Or using ngrok:
ngrok http 8000
```
Note your public HTTPS URL (e.g. `https://mercury.yourdomain.com`).

### Step 7.2: Configure Webhook in Meta Developer Portal
1. In Meta App Dashboard, go to **Webhooks** > Select **Instagram** from the dropdown.
2. Click **Subscribe to this object**.
3. **Callback URL:** `https://your-domain.com/webhook`
4. **Verify Token:** `Mercury_Secret_Verify_Token_2026` (or the custom verify token set in Settings).
5. Click **Verify and Save**.
6. In the Webhooks table, subscribe to:
   * **`comments`** (captures all incoming comments on Reels & Posts)
   * **`messages`** (captures direct messages & Follow-Gate confirmations)

---

## Phase 8: Autonomous Polling Daemon (Zero-Port Mode)

If you cannot expose a public HTTPS URL or prefer running 100% locally without cloud tunnels:
1. Double-click `run_bot.bat` or run:
   ```bash
   python poll_engine.py
   ```
2. **How it works:**
   * Scans your active configured reels and recent posts every 60 seconds.
   * Fetches comments in parallel using multithreaded workers (<2s execution).
   * Automatically identifies new comments, matches keywords, and dispatches DMs.
   * Zero server hosting, zero tunnels, zero domain costs.

---

## Phase 9: Creating Video Automations & Follow-Gates

### 9.1 Automate an Uploaded Reel
1. Navigate to **Video Automations** in the dashboard.
2. Click **Configure** on any uploaded Instagram Reel.
3. Configure:
   * **Keywords:** Words that trigger the DM (e.g. `LINK, DEMO, WORKFLOW, *` for any comment).
   * **Match Type:** `Contains` (recommended) or `Exact`.
   * **Private DM 1:** First message dispatched to user's inbox (supports `{username}` interpolation).
   * **Private DM 2:** Optional second follow-up message dispatched with human pause.
   * **Public Reply:** Contextual comment posted under user's comment.
4. Click **Save Automation**.

### 9.2 Pre-Configure an Upcoming Reel
1. Click **+ Add Upcoming Video Preset** in the top right.
2. Prepare your trigger rules, DMs, and public replies *before* publishing your video.
3. Once published on Instagram, Mercury matches incoming comments immediately!

### 9.3 Setting Up the Follow-Gate
1. In the automation editor, toggle **Enable Follow-Gate**.
2. When a user comments:
   * If they don't follow you yet, Mercury sends an interactive DM with a direct profile link asking them to follow.
   * As soon as they hit Follow and reply `FOLLOWED` in DM, Mercury verifies and unlocks the secret link!

---

## Phase 10: Serverless Cloud Deployment (Vercel)

Mercury includes pre-configured serverless handlers for Vercel deployment:

### 10.1 Deploy to Vercel
```bash
npm install -g vercel
vercel
```

### 10.2 Configure Environment Variables in Vercel Dashboard
In **Project Settings** > **Environment Variables**, add:
* `PAGE_ACCESS_TOKEN`
* `PAGE_ID`
* `IG_BUSINESS_ACCOUNT_ID`
* `APP_ID`
* `WEBHOOK_VERIFY_TOKEN`
* `DASHBOARD_USERNAME`
* `DASHBOARD_PASSWORD`
* `AUTH_SECRET`

### 10.3 24/7 Serverless Cron Polling
Mercury includes `.github/workflows/mercury-cron.yml` which pings your Vercel `/api/cron/poll` endpoint every 5 minutes from GitHub Actions, guaranteeing 24/7 background comment coverage with zero idle server costs!

---

## Security, Privacy & Data Compliance

* **Token Protection:** Tokens are masked both in the UI and across API endpoints (`EAAY••••••••••••••••3zwL`).
* **Git Safe:** `.env` and `*.db` are strictly excluded from source control.
* **Meta Data Deletion Compliance:** Includes official Meta-compliant data deletion endpoint at `/privacy`. Commenters can request data purge by sending `DELETE DATA`.

---

## Troubleshooting & Frequently Asked Questions

### Q1: Error 190 — "Invalid OAuth access token"
* **Cause:** Your token has expired or was revoked.
* **Fix:** Generate a **System User Token** with expiration set to **Never** (see Phase 3). Paste the new token into **Credentials & Tokens** in the dashboard and click **Save Credentials**.

### Q2: Error 100 — "Unsupported post request" or "Permissions error"
* **Cause:** Your Facebook Page is not linked to your Instagram Business account, or permissions were missing during token generation.
* **Fix:** Ensure all 6 permissions (`instagram_manage_comments`, `instagram_manage_messages`, etc.) are checked and the System User is assigned Full Control of both Page and Instagram assets.

### Q3: Comments are received but no DM is sent
* **Cause:** User has strict message privacy settings, or your Meta App is in Development Mode and the recipient is not added as a Test User.
* **Fix:** Switch your Meta App to **Live Mode** in the App Dashboard header, or add yourself as a tester in Development Mode.

---

## 📄 License
Mercury is licensed under the **MIT License**. Free for personal and commercial use.
