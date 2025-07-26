# SpotyMateBot 🎧🤖

A powerful and multilingual Telegram bot that interacts with Spotify links, displays song and artist information, and stores user preferences. Supports both **Persian** and **English**.


## 🌟 Features

- 🌍 Multilingual support (🇮🇷 Persian / 🇬🇧 English)
- 🔗 Recognizes and processes Spotify track links
- 🎵 Displays detailed info about songs and artists
- 💬 `/start` command with language selection
- 🆘 `/help` command with user guidance
- 🗂️ Stores user preferences in a local SQLite database


## 🚀 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/power0matin/SpotyMateBot
cd SpotyMateBot
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` File

```bash
nano .env
```

Add the following environment variables:

```env
TELEGRAM_TOKEN=your_telegram_token_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback  # or your deployed domain
```

### 4. Run the Bot

```bash
python main.py
```


## ☁️ Deployment

You can deploy this bot to platforms like **Heroku**, **Render**, or your own VPS.

> Sample `Procfile` for Heroku:

```
worker: python main.py
```

Make sure environment variables are added in the platform’s configuration panel.


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
