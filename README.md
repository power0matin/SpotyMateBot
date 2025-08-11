# SpotyMateBot 🎧🤖

A powerful and multilingual Telegram bot that interacts with Spotify links, displays song and artist information, and stores user preferences. Supports both Persian and English.

## 🌟 Features

- 🌍 Multilingual support (🇮🇷 Persian / 🇺🇸 English)
- 🔗 Recognizes and processes Spotify track links
- 🎵 Displays detailed info about songs and artists
- 💬 /start command with language selection
- 🆘 /help command with user guidance
- 🗂️ Stores user preferences in a local SQLite database

> ### ⚠️ Important: Run Spotify API Test Script Before Using the Bot
> Before running the bot, please run the [Spotify-API-Test](https://github.com/power0matin/Spotify-API-Test) script to verify your Spotify API connectivity.

## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/power0matin/SpotyMateBot
cd SpotyMateBot
````


### 2. Create virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```


### 3. Install dependencies

```bash
pip install -r requirements.txt
```


### 4. Create a `.env` file

```bash
nano .env
```

Paste the following content and replace values accordingly:

```env
TELEGRAM_TOKEN=your_telegram_token_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```


## 🔑 How to get the credentials

### 🟢 1. Get `TELEGRAM_TOKEN`

1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send `/start`, then `/newbot` to create a new bot.
3. Follow instructions to set a name and username.
4. You'll receive a `TELEGRAM_TOKEN` like:

   ```
   7547563872:AAFDK0MkTbPGU9WsJxim5ezbyeCzrBxQ5Ig
   ```
5. Copy it and paste it into the `.env` file.


### 🟣 2. Get Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
2. Log in with your Spotify account.
3. Click **"Create an App"** → Fill in name & description → Agree & Submit.
4. Open the app, and you'll see:

   * **Client ID**
   * **Client Secret**
5. Click "Edit Settings" and add the following redirect URI:

   ```
   http://localhost:8888/callback
   ```
6. Save, and copy the `Client ID` and `Client Secret` into the `.env` file.


### 5. Run the bot



```bash
python main.py
```

## 🛠 Tech Stack

* **Python** 🐍
* **python-telegram-bot** – Telegram Bot Framework
* **Spotipy** – Spotify Web API wrapper
* **SQLite** – Lightweight database
* **dotenv** – Manage environment variables


## 📁 Project Structure

```
SpotyMateBot/
├── core/               # Main bot logic and handlers
├── data/               # SQLite database file
├── database/           # DB interaction layer
├── services/           # Spotify API service
├── tests/              # Unit tests
├── utils/              # Utility files (e.g. i18n)
├── main.py             # Entry point
├── requirements.txt    # Dependencies
├── .env                # Environment variables (excluded from git)
└── README.md
```


## 📜 License

This project is licensed under the [MIT License](LICENSE).


## 🙌 Contributions

Feel free to open issues or submit pull requests. Your feedback helps improve the bot!


## 🔗 Links

* **GitHub:** [@power0matin](https://github.com/power0matin)
* **Discord Support:** [Join](https://discord.com/invite/bkApFpXyQh)
