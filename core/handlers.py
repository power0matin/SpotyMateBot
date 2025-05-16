from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_user_language, save_user_language
from utils.i18n import get_message
from services.spotify import process_spotify_link
import re
import requests
import os
import tempfile
from spotdl import Spotdl
from spotdl.types.options import DownloaderOptions

# Global spotdl client
_spotdl_client = None


def get_spotdl_client():
    """Get or initialize the global spotdl client."""
    global _spotdl_client
    if _spotdl_client is None:
        _spotdl_client = Spotdl(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            downloader_settings=DownloaderOptions(output="data/downloads"),
        )
    return _spotdl_client


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


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = [
        [
            InlineKeyboardButton("فارسی 🇮🇷", callback_data="lang_fa"),
            InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    language = get_user_language(user_id) or "en"
    await update.message.reply_text(
        get_message(language, "set_language_prompt"), reply_markup=reply_markup
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
        track_info = process_spotify_link(message_text, language)
        if isinstance(track_info, dict):
            # Create inline buttons
            keyboard = [
                [
                    InlineKeyboardButton(
                        get_message(language, "similar_songs_button"),
                        callback_data=f"similar_{track_info['track_id']}",
                    ),
                    InlineKeyboardButton(
                        get_message(language, "more_info_button"), url=message_text
                    ),
                ],
                [
                    InlineKeyboardButton(
                        get_message(language, "download_preview_button"),
                        callback_data=f"download_preview_{track_info['track_id']}_{track_info['preview_url'] or 'no_preview'}",
                    ),
                    InlineKeyboardButton(
                        get_message(language, "download_song_button"),
                        callback_data=f"download_song_{track_info['track_id']}",
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            # Send message with track info and cover image
            try:
                await update.message.reply_photo(
                    photo=track_info["cover_url"],
                    caption=get_message(language, "track_info").format(
                        title=track_info["title"],
                        artist=track_info["artist"],
                        genre=track_info["genre"] or get_message(language, "no_genre"),
                        duration=track_info["duration"],
                        release_date=track_info["release_date"],
                        preview_url=track_info["preview_url"]
                        or get_message(language, "no_preview"),
                    ),
                    reply_markup=reply_markup,
                )
            except Exception as e:
                await update.message.reply_text(
                    get_message(language, "error").format(error=str(e))
                )
        else:
            await update.message.reply_text(track_info)
    else:
        await update.message.reply_text(get_message(language, "help"))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    language = get_user_language(query.from_user.id) or "en"
    callback_data = query.data

    if callback_data.startswith("lang_"):
        await language_selection(update, context)
    elif callback_data.startswith("similar_"):
        track_id = callback_data.split("_")[1]
        recommendations = process_spotify_link(
            f"spotify:track:{track_id}", language, get_recommendations=True
        )
        if isinstance(recommendations, list):
            response = get_message(language, "similar_songs").format(
                songs="\n".join(
                    [
                        f"🎵 {track['title']} - {track['artist']}"
                        for track in recommendations
                    ]
                )
            )
            await query.message.reply_text(response)
        else:
            await query.message.reply_text(
                get_message(language, "similar_songs_placeholder")
            )
    elif callback_data.startswith("download_preview_"):
        _, track_id, preview_url = callback_data.split("_", 2)
        if preview_url == "no_preview" or not preview_url:
            await query.message.reply_text(get_message(language, "no_preview"))
        else:
            try:
                response = requests.get(preview_url, timeout=10)
                response.raise_for_status()
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3"
                ) as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file_path = tmp_file.name
                with open(tmp_file_path, "rb") as audio_file:
                    await query.message.reply_audio(
                        audio=audio_file,
                        caption=get_message(language, "download_preview_caption"),
                    )
                os.unlink(tmp_file_path)  # Delete temporary file
            except requests.RequestException as e:
                await query.message.reply_text(
                    get_message(language, "download_error").format(error=str(e))
                )
            except Exception as e:
                await query.message.reply_text(
                    get_message(language, "error").format(error=str(e))
                )
    elif callback_data.startswith("download_song_"):
        track_id = callback_data.split("_")[1]
        spotify_url = f"https://open.spotify.com/track/{track_id}"
        try:
            # Get spotdl client
            spotdl = get_spotdl_client()
            # Create downloads directory if it doesn't exist
            os.makedirs("data/downloads", exist_ok=True)
            # Download the song
            songs = spotdl.search([spotify_url])
            if songs:
                song = songs[0]
                song_path = spotdl.download(song)
                if os.path.exists(song_path):
                    with open(song_path, "rb") as audio_file:
                        await query.message.reply_audio(
                            audio=audio_file,
                            caption=get_message(
                                language, "download_song_caption"
                            ).format(title=song.name, artist=song.artist),
                        )
                    os.unlink(song_path)  # Delete the file after sending
                    # Clean up downloads directory if empty
                    if not os.listdir("data/downloads"):
                        os.rmdir("data/downloads")
                else:
                    await query.message.reply_text(
                        get_message(language, "download_error")
                    )
            else:
                await query.message.reply_text(get_message(language, "download_error"))
        except Exception as e:
            await query.message.reply_text(
                get_message(language, "error").format(error=str(e))
            )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors and notify the user."""
    language = (
        get_user_language(update.effective_user.id)
        if update and update.effective_user
        else "en"
    )
    error_message = str(context.error)
    if "BadRequest" in error_message:
        error_message = get_message(language, "telegram_error")
    (
        await update.message.reply_text(error_message)
        if update and update.message
        else None
    )
