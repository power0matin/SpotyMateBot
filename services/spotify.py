from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_user_language, save_user_language
from utils.i18n import get_message
from services.spotify import process_spotify_link
import re


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_language = get_user_language(user_id)

    if current_language:
        await update.message.reply_text(
            get_message(current_language, "welcome").format(
                language=current_language.upper()
            )
        )
    else:
        keyboard = [
            [
                InlineKeyboardButton("فارسی 🇮🇷", callback_data="lang_fa"),
                InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🎵 Welcome to @SpotyMateBot! Please choose your language:\nبه @SpotyMateBot خوش اومدی! لطفاً زبانت رو انتخاب کن:",
            reply_markup=reply_markup,
        )


async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = query.data.split("_")[1]  # Extract 'fa' or 'en'
    language_name = "فارسی" if language == "fa" else "English"

    save_user_language(user_id, language)
    await query.message.edit_text(
        get_message(language, "language_selected").format(language=language_name)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_user_language(user_id) or "en"
    await update.message.reply_text(get_message(language, "help"))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_user_language(user_id) or "en"
    message_text = update.message.text

    spotify_pattern = r"https?://open\.spotify\.com/(track|album|playlist)/[a-zA-Z0-9]+"
    if re.search(spotify_pattern, message_text):
        response = process_spotify_link(message_text, language)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text(get_message(language, "help"))
