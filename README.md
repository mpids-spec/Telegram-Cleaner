# 🧹 TG Cleaner

**A beautiful web app to clean up your Telegram — leave unused groups, clear unread messages, and organize your chats with powerful filters.**

> Built with Python + Flask + Telethon. Runs locally on your machine — your data never leaves your computer.

![TG Cleaner Screenshot](https://i.imgur.com/placeholder.png)

---

## ✨ Features

- 🚪 **Leave groups & channels** — select multiple and exit in one click
- ✅ **Mark all as read** — clear unread counts across all chats
- 🔍 **Search** by chat name
- 📅 **Filter by inactivity** — find chats you haven't visited in 1, 3, 6, 12+ months
- 💬 **Filter by your activity** — find chats where you've never sent a message
- 📢 **Filter by type** — Channels / Groups / Supergroups
- 🔔 **Filter by unread** — show only chats with unread messages
- 👤 **Filter by your role** — Member / Admin / Creator
- 📊 **Sort** by any column
- ☑ **Bulk select** — select all, select filtered, or pick manually

---

## 🚀 Quick Start

### 1. Get your Telegram API keys (free, 1 minute)

1. Go to **https://my.telegram.org** and log in with your phone number
2. Click **App configuration**
3. Create a new app (name and short name can be anything)
4. Copy your **`App api_id`** (a number) and **`App api_hash`** (a string)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API keys

Open `tg_cleaner_app.py` and find these lines near the top:

```python
API_ID   = int(os.environ.get("TG_API_ID", 0))
API_HASH = os.environ.get("TG_API_HASH", "")
```

**Option A — paste directly (easiest):**
```python
API_ID   = 12345678
API_HASH = "your_api_hash_here"
```

**Option B — environment variables (more secure):**
```bash
# Windows
set TG_API_ID=12345678
set TG_API_HASH=your_api_hash_here

# Mac/Linux
export TG_API_ID=12345678
export TG_API_HASH=your_api_hash_here
```

### 4. Run

```bash
py tg_cleaner_app.py       # Windows
python tg_cleaner_app.py   # Mac/Linux
```

Then open **http://localhost:5000** in your browser.

On first launch, you'll be asked for your phone number and a Telegram verification code — this is normal, it's how the app connects to your account.

---

## 🔒 Privacy & Security

- **Your data never leaves your computer** — the app runs entirely locally
- **No servers, no cloud** — direct connection to Telegram API from your machine
- The session file (`tg_cleaner_session.session`) is saved locally so you don't need to log in every time
- Your API keys are never shared or transmitted anywhere
- Open source — you can read every line of code

---

## 📋 Requirements

- Python 3.8+
- A Telegram account
- Telegram API keys (free from my.telegram.org)

---

## 🛠 Tech Stack

- **[Telethon](https://github.com/LonamiWebs/Telethon)** — Telegram MTProto client
- **[Flask](https://flask.palletsprojects.com/)** — lightweight web server
- Vanilla JS + CSS — no frontend frameworks needed

---

## ⚠️ Important Notes

- **Do not share your `tg_cleaner_session.session` file** — it contains your login session
- **Do not commit your API keys to GitHub** — use environment variables or `.gitignore`
- Telegram may rate-limit leaving many groups quickly — the app adds a small delay between actions
- You cannot leave groups where you are the **sole creator** — you must transfer ownership or delete the group first

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests are welcome! Some ideas for improvements:
- [ ] Archive chats instead of leaving
- [ ] Export chat list to CSV
- [ ] Mute notifications for selected chats
- [ ] Dark/light theme toggle
- [ ] English / Russian language switch
