# SpotyMateBot

A professional Telegram bot that interacts with Spotify links and supports multilingual (Persian/English) user interactions.

## Features

- Responds to `/start` with language selection (Persian/English).
- Processes Spotify track links to display song and artist information.
- Supports `/help` command for user guidance.
- Stores user language preferences in SQLite database.

## Setup

1. **Clone the repository:**
	```bash
	git clone <repository-url>
	cd spotymatebot
	```

2. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```

3. **Create a `.env` file with the following:**
	```env
	TELEGRAM_TOKEN=your_telegram_token_here
	SPOTIFY_CLIENT_ID=your_spotify_client_id_here
	SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
	SPOTIFY_REDIRECT_URI=https://your-app-name.herokuapp.com/callback
	```

4. **Run the bot:**
	```bash
	python spotymatebot/main.py
	```

## Deployment

**Deploy to Heroku:**
