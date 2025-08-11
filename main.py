import os
import pytz
from dotenv import load_dotenv

# --- PATCH apscheduler before importing JobQueue ---
import apscheduler.util as aps_util
aps_util.astimezone = lambda tz=None: pytz.UTC  # Force UTC as pytz

from telegram.ext import Application, JobQueue
from core.bot import setup_bot

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    """Main function to run the bot."""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN is not set in .env file")

    # Create JobQueue (now safe because timezone is patched)
    job_queue = JobQueue()

    # Create bot application
    application = Application.builder().token(TELEGRAM_TOKEN).job_queue(job_queue).build()

    # Setup bot handlers
    setup_bot(application)

    # Start polling
    print("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
