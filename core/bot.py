from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from spotymatebot.core.handlers import start, help_command, handle_message, language_selection
from spotymatebot.database.db import init_db

def setup_bot(application: Application):
    """Setup bot handlers and initialize database."""
    # Initialize database
    init_db()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(language_selection, pattern="lang_.*"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))