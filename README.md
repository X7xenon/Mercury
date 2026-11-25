# ☿ Mercury: Autonomous Meta & Instagram Growth Platform

<p align="center">
  <b>The In-House, Zero-Subscription ManyChat Alternative for Creators, Developers & Agencies.</b><br>
  Built with FastAPI, SQLite, and Meta Graph API v21.0. Featuring an Aesthetic 2D Studio Dashboard.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Meta_Graph_API-v21.0-8B6CFF?style=flat-square&logo=meta" alt="Meta Graph API v21.0">
  <img src="https://img.shields.io/badge/Python-3.9+-08080B?style=flat-square&logo=python" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/FastAPI-2.0.0-009688?style=flat-square&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-C6FF3D?style=flat-square" alt="MIT License">
</p>

---

## ⚡ What is Mercury?

> 📖 **Full Step-by-Step Documentation:** For an exhaustive walkthrough covering Meta Developer setup, System User permanent tokens, webhooks, and cloud deployment, read the [Complete Setup & Deployment Guide](docs/FULL_SETUP_GUIDE.md).

**Mercury** is an autonomous, self-hosted Instagram automation platform and growth studio designed to completely eliminate monthly ManyChat subscription costs ($50–$300+/month). Built directly on Meta's official Graph API v21.0, Mercury operates with zero external SaaS dependencies, guarantees zero ban flags through safe jitter rate-limiting, and delivers private replies in under 1.2 seconds.

### 🌟 Key Capabilities

1. **Reel & Video-Specific Automations:** Browse your uploaded reels or pre-configure an **Upcoming Video Preset** with tailored keywords, dual-message private DM sequences, and algorithm-boosting public replies.
2. **Interactive Credentials & Tokens Panel:** Configure custom Meta Page Access Tokens, Instagram Business Account IDs, Page IDs, and dashboard passwords directly from the UI with an instant **"Test Connection"** diagnostic tool.
3. **Smart Follow-Gate Engine:** Ask commenters to follow your Instagram account first. When they follow and reply `FOLLOWED`, Mercury unlocks and dispatches their exclusive link automatically.
4. **Autonomous Local Polling & Webhooks:** Run 100% locally with zero open ports via the lightning-fast multithreaded polling daemon, or connect live Meta Webhooks for instantaneous real-time event dispatching.
5. **Interactive Trigger Sandbox:** Test your triggers, simulate user comments, and preview `{username}` token formatting in real-time before going live.
6. **Performance & Analytics Studio:** Track total DMs sent, comments replied, unique creators reached, and estimated hours saved with 2D activity volume charts.
7. **Meta Terms Compliant:** Includes official Data Deletion & Privacy Policy routes (`/privacy`) and anti-flag jitter protection.

---

## 🎨 Visual Design Language

Mercury features a 2D aesthetic inspired by Japanese ink wash minimalism and modular geometric constructivism:
* **Charcoal Canvas:** `#08080B` to `#14151D` deep matte backgrounds.
* **Soft Ivory:** `#FAF9F5` crisp high-contrast typography.
* **Cool Gray:** `#43495A` to `#7F869A` hairline frames and structural borders.
* **Accent Purple:** `#8B6CFF` glowing interactive highlights and focus rings.
* **Neon Lime:** `#C6FF3D` status indicator for online Meta Graph API handshakes.

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.9 or higher installed on your machine.
* A Meta Developer Account with a Facebook Page connected to an Instagram Professional/Creator account.

### 1. Clone the Repository
```bash
git clone https://github.com/X7xenon/Mercury.git
cd Mercury
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Dashboard & Server
```bash
# Windows 1-Click Launcher:
run_dashboard.bat

# Or via Command Line:
python server.py
```

* Open your browser at **`http://localhost:8000/`**
* Default Operator Username: `admin` (or configured in `.env`)
* Set your password in `.env` (`DASHBOARD_PASSWORD`) or configure it directly in the **Credentials & Tokens** tab.

### 4. Optional: Run Autonomous Local Polling Daemon
If you don't have a public HTTPS domain for webhooks, Mercury can poll Meta Graph API locally:
```bash
# Windows 1-Click Launcher:
run_bot.bat

# Or via Command Line:
python poll_engine.py
```

---

## 🔑 Adding Custom Tokens & Meta Setup

Mercury allows you to input your credentials directly inside the Dashboard under **`Credentials & Tokens`** or via `.env`:

### Step 1: Create Meta Developer App
1. Go to [Meta for Developers](https://developers.facebook.com/) and click **Create App**.
2. Select **Business** as the app type.
3. Add the **Instagram Graph API** product to your app.

### Step 2: Generate Permanent Page Access Token
1. Go to **Meta Business Suite** > **Settings** > **System Users**.
2. Create a System User (role: Admin) and click **Generate Token**.
3. Select your app and grant the following permissions:
   * `instagram_basic`
   * `instagram_manage_comments`
   * `instagram_manage_messages`
   * `pages_manage_metadata`
   * `pages_read_engagement`
4. Copy the permanent access token (starts with `EAAY...` or `EAA...`).

### Step 3: Enter Credentials in Mercury
1. Open the Mercury Dashboard (`http://localhost:8000`).
2. Navigate to **`Credentials & Tokens`** in the sidebar.
3. Paste your **Page Access Token**, **Instagram Business Account ID**, and **Facebook Page ID**.
4. Click **Test Connection** to verify with Meta Graph API in real-time.
5. Click **Save Credentials**. All changes apply immediately without restarting!

---

## ⚠️ Top Mistakes to Avoid During Setup

Before going live, make sure to avoid these common setup pitfalls:
* 🔴 **Short-Lived User Tokens:** Don't use Graph API Explorer tokens (they expire in 1–60 days). Always generate a **System User Token** with expiration set to **Never**.
* 🔴 **Disabled Inbox Access:** In Facebook Page Settings > Linked Accounts > Instagram, toggle **"Allow access to Instagram messages in Inbox"** to **ON**, otherwise Meta blocks outbound DMs.
* 🔴 **App in Development Mode:** In Dev Mode, Meta only sends DMs to registered **App Testers**. Switch your app to **Live Mode** in the Meta header to message regular followers.
* 🔴 **Swapped IDs:** `PAGE_ID` is your numeric Facebook Page ID; `IG_BUSINESS_ACCOUNT_ID` is your Instagram account ID. Use Mercury's **Test Connection** button to confirm.
* 🔴 **Unsubscribed Webhooks:** After entering the verify token, you must explicitly click **Subscribe** on both the **`comments`** and **`messages`** fields in Meta's Webhooks table.

👉 *Read the full detailed breakdown in the [Complete Setup Guide (Top 10 Mistakes & Fixes)](docs/FULL_SETUP_GUIDE.md#14-top-10-common-mistakes--pitfalls-to-avoid).*

---

## ⚙️ Configuration Reference (`.env.example`)

You can also pre-seed your configuration using environment variables:

```bash
# Meta Graph API Credentials
PAGE_ACCESS_TOKEN=your_permanent_page_access_token_here
PAGE_ID=your_facebook_page_id_here
IG_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id_here
APP_ID=your_meta_app_id_here

# Webhook Handshake Security
WEBHOOK_VERIFY_TOKEN=Mercury_Secret_Verify_Token_2026
PORT=8000

# Profile & Community Customization
IG_USERNAME=your_instagram_handle
DISCORD_INVITE_URL=https://discord.gg/your-community

# Dashboard Operator Security
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=YourSecurePassword123!
AUTH_SECRET=Mercury_Auth_Secret_Key_Secure_9988
```

---

## 🌐 Webhook Configuration (Real-Time Mode)

For zero-latency instantaneous comment replies:
1. In Meta App Dashboard, go to **Webhooks** > **Instagram**.
2. Set **Callback URL**: `https://<your-domain-or-tunnel>/webhook`
3. Set **Verify Token**: `Mercury_Secret_Verify_Token_2026` (or custom token from Settings).
4. Subscribe to the **`comments`** and **`messages`** fields.

---

## ☁️ Serverless Deployment (Vercel)

Mercury includes pre-configured serverless handlers for Vercel:
* `vercel.json` and `api/index.py` (via `Mangum`) are ready to deploy.
* Continuous 24/7 comment polling is supported via GitHub Actions workflow (`.github/workflows/mercury-cron.yml`).

---

## 🔒 Security & Privacy

* **Zero Hardcoded Secrets:** Tokens and credentials are never stored in git.
* **Token Masking:** The REST API and Settings UI always return masked tokens (`EAAY••••••••••••••••3zwL`) to prevent credential leakage.
* **Constant-Time Verification:** Login credentials use HMAC constant-time comparisons to prevent timing attacks.
* **Data Deletion Endpoint:** Meta-compliant data purge route at `/privacy`.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details. Built for builders, creators, and open-source growth hackers.
