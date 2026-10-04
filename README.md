<div align="center">

# 📥 Telegram-Restricted-Content-Downloader

**An open-source Telegram bot to download photos, videos & documents from public, private & invite-only channels/groups — even when forwarding is disabled.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telethon](https://img.shields.io/badge/Telethon-1.34%2B-green?style=for-the-badge)](https://github.com/LonamiWebs/Telethon)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/Chenuka-Sankalpa/Telegram-Restricted-Content-Downloader?style=for-the-badge&logo=github)](https://github.com/Chenuka-Sankalpa/Telegram-Restricted-Content-Downloader/stargazers)
[![Forks](https://img.shields.io/github/forks/Chenuka-Sankalpa/Telegram-Restricted-Content-Downloader?style=for-the-badge&logo=github)](https://github.com/Chenuka-Sankalpa/Telegram-Restricted-Content-Downloader/network/members)
[![Issues](https://img.shields.io/github/issues/Chenuka-Sankalpa/Telegram-Restricted-Content-Downloader?style=for-the-badge&logo=github)](https://github.com/Chenuka-Sankalpa/Telegram-Restricted-Content-Downloader/issues)

[Features](#-features) • [How It Works](#-how-it-works) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack) • [Disclaimer](#-disclaimer) • [License](#-license)

</div>

---

## 📖 Table of Contents

- [About](#-about)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Step 1: Clone the Repository](#step-1-clone-the-repository)
  - [Step 2: Install Dependencies](#step-2-install-dependencies)
  - [Step 3: Get Telegram API Credentials](#step-3-get-telegram-api-credentials)
  - [Step 4: Create a Bot](#step-4-create-a-bot)
  - [Step 5: Configure Environment](#step-5-configure-environment)
  - [Step 6: Set Up Local Bot API Server](#step-6-set-up-local-bot-api-server)
  - [Step 7: Run the Bot](#step-7-run-the-bot)
- [Usage](#-usage)
  - [Commands](#commands)
  - [Supported Links](#supported-links)
  - [Private Channel Flow](#private-channel-flow)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Disclaimer](#-disclaimer)
- [License](#-license)
- [Author](#-author)

---

## 🎯 About

**Telegram-Restricted-Content-Downloader** is a self-hosted Telegram bot that lets you download media from Telegram channels and groups — **even when the admin has disabled forwarding and copying**.

This bot uses **Telethon** (MTProto API) combined with a **Local Bot API Server** to bypass Telegram's default 50MB Bot API limit, allowing downloads up to **2GB**.

Whether it's a public channel, a private invite-only group, or a restricted channel with `noforwards` protection — this bot handles them all.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖼️ **Multi-Media Support** | Photos, videos, and documents |
| 🔓 **Auto-Join** | Automatically joins via invite links (`t.me/+xxx`) |
| 🚪 **Auto-Leave** | Leaves the channel after download (only if it joined) |
| 🔐 **Private Channel Support** | Handles `t.me/c/...` internal links via invite flow |
| 🚫 **Bypass `noforwards`** | Downloads content even when forwarding is disabled |
| ⏱️ **Live Timer + Speed** | Real-time download/upload progress with MB/s speed |
| 📦 **2GB File Support** | Via Local Bot API Server (vs 50MB default) |
| 👑 **Access Control** | Owner + Allowed users system |
| 🌐 **Open Source** | MIT License — free to use, modify, distribute |
| 🐳 **Docker Ready** | One-command setup for Local Bot API Server |

---

## 🔄 How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Telegram   │────▶│  This Bot    │────▶│  Local Bot API   │
│   Channel    │     │  (Telethon)  │     │  Server (Docker) │
└──────────────┘     └──────────────┘     └──────────────────┘
       │                    │                      │
       │ 1. Send link       │                      │
       │───────────────────▶│                      │
       │                    │ 2. Join if needed    │
       │                    │─────────────────────▶│
       │                    │ 3. Download media    │
       │◀───────────────────│                      │
       │                    │ 4. Upload via API    │
       │                    │─────────────────────▶│
       │                    │ 5. Send to user      │
       │◀───────────────────────────────────────────│
       │                    │ 6. Leave channel     │
       │                    │─────────────────────▶│
```

### Flow Explained

1. **User sends a link** to the bot
2. **Bot detects link type** (public / private / invite)
3. **If private (`t.me/c/...`)**, bot asks for an invite link (`t.me/+xxx`) within 60s
4. **Bot joins the channel** using the user account (via Telethon)
5. **Bot downloads the media** from the original message
6. **Bot uploads it** to the user via Local Bot API Server (up to 2GB)
7. **Bot leaves the channel** (only if it joined for this request)

---

## 📸 Screenshots

> _Coming soon — feel free to contribute screenshots by opening a PR!_

<!--
Add screenshots here:
![Download Progress](screenshots/progress.png)
![Final Summary](screenshots/summary.png)
-->

---

## 🚀 Installation

### Prerequisites

Before you begin, make sure you have:

- **Python 3.9+** — [Download](https://www.python.org/downloads/)
- **Docker** (for Local Bot API Server) — [Download](https://www.docker.com/products/docker-desktop/)
- **A Telegram account** — for API credentials
- **A Telegram bot** — created via [@BotFather](https://t.me/BotFather)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/Chenuka-Sankalpa/Telegram-Restricted-Content-Downloader.git
cd Telegram-Restricted-Content-Downloader
```

---

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Or using a virtual environment (recommended):**

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

---

### Step 3: Get Telegram API Credentials

1. Go to [https://my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click **"API Development Tools"**
4. Fill in the form (App title, Short name, etc.)
5. Copy your **`api_id`** and **`api_hash`**

---

### Step 4: Create a Bot

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a **name** and **username** for your bot
4. Copy the **Bot Token** (looks like `123456:ABC-DEF...`)

---

### Step 5: Configure Environment

```bash
cp .env.example .env
nano .env
```

Fill in the values:

```env
# Telegram API credentials (from https://my.telegram.org)
API_ID=1234567
API_HASH=your_api_hash_here

# Bot token (from @BotFather)
BOT_TOKEN=123456:ABC-DEF...

# User session name (will create user_session.session)
SESSION_NAME=user_session

# Local Bot API Server URL (for files > 50MB)
LOCAL_API_URL=http://localhost:3333

# Owner Telegram user ID (your own ID from @userinfobot)
OWNER_ID=8888047326

# Pending link timeout in seconds
PENDING_LINK_TIMEOUT=60

# Access wait timeout in seconds
ACCESS_WAIT_SECONDS=10
```

---

### Step 6: Set Up Local Bot API Server

This is **required** for files larger than 50MB. Skip this step if you only need small files.

```bash
docker run -d --name telegram-bot-api \
  -e TELEGRAM_API_ID=YOUR_API_ID \
  -e TELEGRAM_API_HASH=YOUR_API_HASH \
  -e TELEGRAM_LOCAL=true \
  -p 3333:8081 \
  -v "$PWD/data:/var/lib/telegram-bot-api" \
  aiogram/telegram-bot-api:latest
```

Verify it's running:

```bash
docker ps
curl http://localhost:3333/bot<YOUR_BOT_TOKEN>/getMe
```

You should see a JSON response with your bot's info.

---

### Step 7: Run the Bot

```bash
python bot.py
```

**On the first run**, you'll be asked for:

```
Please enter your phone (or bot token): +94XXXXXXXXX
Please enter the code you received: 12345
Please enter your password: your_2fa_password
```

After successful login:

```
==================================================
✅ User client ready!
🤖 Bot is running
📡 Local Bot API URL: http://localhost:3333
📦 Max file size: 2GB
🖼️ Media: Photo + Video + Document
⏱️ LIVE Timer + Speed: ENABLED
👑 Owner ID: 8888047326
👥 Allowed Users: 1
⏳ Pending Link Timeout: 60s
🔓 Auto-Join + 🚪 Auto-Leave: ENABLED
⚡ Developed By Chenuxx
==================================================
```

---

## 📱 Usage

### Commands

| Command | Access | Description |
|---------|--------|-------------|
| `/start` | Allowed users | Start the bot and show help |
| `/add @username` | **Owner only** | Add a user to allowed list |
| `/remove @username` | **Owner only** | Remove a user from allowed list |
| `/list` | **Owner only** | List all allowed users |

---

### Supported Links

| Format | Type | Example |
|--------|------|---------|
| `t.me/channelname/123` | Public | Public channel post |
| `t.me/c/1234567890/123` | Private | Private channel internal link |
| `t.me/+xxxxxxxxx` | Invite | Invite link |

---

### Private Channel Flow

**Step 1:** Send a private channel link:

```
https://t.me/c/3959794143/412
```

**Step 2:** Bot replies:

```
❌ Cannot access this private channel.

This is an internal link (t.me/c/...). The bot cannot join it directly.

📩 Please send the invite link (t.me/+xxx) for this channel within 60 seconds.

The bot will join, download the content from your original link, then leave.
```

**Step 3:** Send the invite link:

```
https://t.me/+o1Lm3ZFYL4o3YzU9
```

**Step 4:** Bot joins, downloads, uploads, and leaves:

```
✅ 🎥 Video sent successfully!

📦 Size: 245.30 MB
⬇️ Download: 12.4s (19.78 MB/s)
⬆️ Upload: 28.7s (8.55 MB/s)
⏱️ Total Time: 41.1s
🚪 Left the channel (auto-leave)

⚡ Developed By Chenuxx
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.9+** | Main language |
| **Telethon** | MTProto client for Telegram |
| **aiohttp** | Async HTTP for Local Bot API |
| **python-dotenv** | Environment variable management |
| **Docker** | For running Local Bot API Server |
| **Local Bot API Server** | 2GB file size support |

---

## 📁 Project Structure

```
Telegram-Restricted-Content-Downloader/
│
├── bot.py                    # Main bot code
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── LICENSE                  # MIT License
│
└── (runtime files — NOT committed)
    ├── allowed_users.json   # User access list
    ├── user_session.session # User account session (SENSITIVE)
    ├── bot_session.session  # Bot session (SENSITIVE)
    └── downloads/           # Temporary download folder
```

---

## ⚙️ Configuration

All configuration is done via the `.env` file.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_ID` | ✅ | — | Telegram API ID from my.telegram.org |
| `API_HASH` | ✅ | — | Telegram API Hash from my.telegram.org |
| `BOT_TOKEN` | ✅ | — | Bot token from @BotFather |
| `SESSION_NAME` | ❌ | `user_session` | Session file name |
| `LOCAL_API_URL` | ❌ | `http://localhost:3333` | Local Bot API Server URL |
| `OWNER_ID` | ✅ | `0` | Your Telegram user ID |
| `PENDING_LINK_TIMEOUT` | ❌ | `60` | Seconds to wait for invite link |
| `ACCESS_WAIT_SECONDS` | ❌ | `10` | Seconds to wait for channel access |

---

## 🐛 Troubleshooting

### ❌ `Cannot find any entity corresponding to...`

**Cause:** Your user account is not a member of the channel.

**Fix:** Join the channel manually using your Telegram account, then try again.

---

### ❌ `Channel mismatch!`

**Cause:** The invite link doesn't match the original `t.me/c/...` link.

**Fix:** Make sure the invite link belongs to the same channel as the original link.

---

### ❌ `Upload failed: ...`

**Cause:** Local Bot API Server is not running, or file is too large.

**Fix:**

```bash
# Check if server is running
docker ps

# Restart if needed
docker restart telegram-bot-api

# Test API
curl http://localhost:3333/bot<YOUR_BOT_TOKEN>/getMe
```

---

### ❌ `Invite link has expired`

**Cause:** The invite link is no longer valid.

**Fix:** Get a fresh invite link from the channel admin.

---

### ❌ `Too many channels joined`

**Cause:** Your Telegram account has joined too many channels (Telegram limit: ~500).

**Fix:** Leave some old channels using the Telegram app.

---

### ❌ `The asyncio event loop must not change after connection`

**Cause:** Telethon client was started outside of `asyncio.run()`.

**Fix:** Make sure all `client.start()` calls are inside the `main()` function.

---

## 🤝 Contributing

Contributions are always welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit** your changes:
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push** to the branch:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open** a Pull Request

### Contribution Ideas

- 🌍 Add multi-language support
- 📊 Add progress bar (instead of live timer)
- 🗄️ Add database support (SQLite/PostgreSQL)
- 🎨 Add inline keyboard buttons
- 🐳 Add Docker Compose setup
- 📝 Improve documentation

---

## ⚠️ Disclaimer

**This bot is for educational purposes only.**

- ❌ Do **not** use it to download copyrighted content without permission
- ❌ Do **not** use it to violate anyone's privacy
- ❌ Do **not** use it to bypass Telegram's Terms of Service
- ✅ Use it only for content you have legal access to

The developer is **not responsible** for any misuse of this software. Use at your own risk.

Respect [Telegram's Terms of Service](https://telegram.org/tos).

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 Chenuxx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 👨‍💻 Author

<div align="center">

**Chenuka Sankalpa (Chenuxx)**

[![Telegram](https://img.shields.io/badge/Telegram-@chenuxx-blue?style=for-the-badge&logo=telegram)](https://t.me/chenuxx)
[![GitHub](https://img.shields.io/badge/GitHub-Chenuka--Sankalpa-black?style=for-the-badge&logo=github)](https://github.com/Chenuka-Sankalpa)

</div>

---

## ⭐ Show Your Support

If this project helped you, please give it a **⭐ star** on GitHub — it means a lot!

<div align="center">

**[⬆ Back to Top](#-telegram-restricted-content-downloader)**

Made with ❤️ by [Chenuxx](https://t.me/chenuxx)

</div>
