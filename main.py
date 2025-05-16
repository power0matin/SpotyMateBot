import os
from telegram.ext import Application
from dotenv import load_dotenv
from core.bot import setup_bot

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


def main():
    """Main function to run the bot."""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN is not set in .env file")

    # Initialize the bot application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Setup bot handlers
    setup_bot(application)

    # Start polling
    print("Starting bot...")
    application.run_polling()


if __name__ == "__main__":
    main()
