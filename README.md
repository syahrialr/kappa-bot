# 🤖 KappaBot — Discord Exploit & Gemstone Monitor

KappaBot is a **Discord bot built with Python (discord.py)** designed to:

- 🔎 Check **exploit status** (Windows & Android) from weao.xyz API  
- 💎 Detect **Gemstone keywords** in messages and embeds  
- 🧵 Show detailed results inside **auto-created threads**  
- 🛡️ Stay safe from **rate limits & spam** (cooldown + async delay)  
- 🌱 Use **Environment Variables** for secure configuration  

---

## ✨ Features

### 📊 /status
- Displays exploit information:
  - Updated / Down status
  - Version
  - Last update date
  - Free / Paid
  - Key system
  - Detection status
- Supports:
  - All exploits
  - Specific exploit search (`/status fluxus`)
- Auto buttons for **Website** and **Discord** (if available)

---

### 💎 /gemstone
- Scans channel messages and embeds
- Keyword detection: `gemstone`
- Summary alert in the channel
- Full details inside a **thread**
- Auto-delete for messages and threads
- Cooldown protection to prevent spam

---

## 🧠 Tech Stack

- Python 3.10+
- discord.py (slash commands / app_commands)
- aiohttp (async HTTP requests)
- AsyncIO
- Environment Variables (.env / hosting panel)

---

## 📦 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/username/kappabot.git
cd kappabot
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

Example `requirements.txt`:
```
discord.py
aiohttp
python-dotenv
```

---

## 🔐 Environment Variables (REQUIRED)

⚠️ **Never hard-code your Discord bot token**

### Required variables:

| Name | Description |
|----|------------|
| BOT_TOKEN | Discord bot token |
| API_ALL | Exploit status API endpoint |

### Example .env (LOCAL ONLY)
```env
BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
API_ALL=https://weao.xyz/api/status/exploits
```

📌 **Do not commit .env to GitHub**

---

## ▶️ Running the Bot

```bash
python WEAO.py
```

Successful output:
```
✅ Bot online as KappaBot#2945
```

---

## 🛡️ Security

- Slash command cooldown (anti-spam)
- Async delay to prevent rate limits
- Dedicated cooldown error handling
- Environment-based configuration

---

## 📂 Project Structure

```
kappabot/
├── WEAO.py
├── requirements.txt
├── README.md
└── .env (local only)
```

---

## ⚠️ Disclaimer

This bot is not affiliated with Discord Inc.
It does not provide or distribute exploits.
It only displays public data from a third-party API.

---

## 👨‍💻 Author

Muhammad Syahrial Rukmana  
Indonesia 🇮🇩
