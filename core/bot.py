from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from core.handlers import (
    start,
    set_language,
    help_command,
    handle_message,
    handle_callback,
    error_handler,
)
from database.db import init_db


def setup_bot(application: Application):
    """Setup bot handlers and initialize database."""
    # Initialize database
    init_db()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setlanguage", set_language))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_error_handler(error_handler)
