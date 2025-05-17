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
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        logger.info("Spotdl client initialized")
    return _spotdl_client


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_language = get_user_language(user_id)
    logger.info(
        f"User {user_id} started bot, language: {current_language or 'not set'}"
    )

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
    language = get_user_language(user_id) or "en"
    logger.info(f"User {user_id} requested to set language, current: {language}")

    keyboard = [
        [
            InlineKeyboardButton("فارسی 🇮🇷", callback_data="lang_fa"),
            InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        get_message(language, "set_language_prompt"), reply_markup=reply_markup
    )


async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language = query.data.split("_")[1]  # Extract 'fa' or 'en'
    language_name = "فارسی" if language == "fa" else "English"
    logger.info(f"User {user_id} selected language: {language_name}")

    save_user_language(user_id, language)
    await query.message.edit_text(
        get_message(language, "language_selected").format(language=language_name)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_user_language(user_id) or "en"
    logger.info(f"User {user_id} requested help, language: {language}")
    await update.message.reply_text(get_message(language, "help"))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = get_user_language(user_id) or "en"
    message_text = update.message.text
    logger.info(f"User {user_id} sent message: {message_text}")

    spotify_pattern = r"https?://open\.spotify\.com/(track|album|playlist)/[a-zA-Z0-9]+"
    if re.search(spotify_pattern, message_text):
        logger.info(f"Processing Spotify link for user {user_id}: {message_text}")
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
                        callback_data=f"select_quality_{track_info['track_id']}",
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
                logger.info(
                    f"Sent track info to user {user_id}: {track_info['title']} by {track_info['artist']}"
                )
            except Exception as e:
                logger.error(f"Error sending track info to user {user_id}: {str(e)}")
                await update.message.reply_text(
                    get_message(language, "error").format(error=str(e))
                )
        else:
            logger.warning(
                f"Invalid Spotify link response for user {user_id}: {track_info}"
            )
            await update.message.reply_text(track_info)
    else:
        logger.info(f"Non-Spotify message from user {user_id}, sending help")
        await update.message.reply_text(get_message(language, "help"))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    language = get_user_language(user_id) or "en"
    callback_data = query.data
    logger.info(f"User {user_id} clicked button: {callback_data}")

    if callback_data.startswith("lang_"):
        await language_selection(update, context)
    elif callback_data.startswith("similar_"):
        track_id = callback_data.split("_")[1]
        logger.info(f"Fetching similar songs for user {user_id}, track_id: {track_id}")
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
            logger.info(f"Sent similar songs to user {user_id}")
        else:
            logger.warning(
                f"No similar songs found for user {user_id}, track_id: {track_id}"
            )
            await query.message.reply_text(
                get_message(language, "similar_songs_placeholder")
            )
    elif callback_data.startswith("download_preview_"):
        _, track_id, preview_url = callback_data.split("_", 2)
        logger.info(
            f"User {user_id} requested preview download, track_id: {track_id}, preview_url: {preview_url}"
        )
        if preview_url == "no_preview" or not preview_url:
            logger.warning(
                f"No preview available for user {user_id}, track_id: {track_id}"
            )
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
                logger.info(
                    f"Sent preview audio to user {user_id}, track_id: {track_id}"
                )
            except requests.RequestException as e:
                logger.error(
                    f"Preview download failed for user {user_id}, track_id: {track_id}: {str(e)}"
                )
                await query.message.reply_text(
                    get_message(language, "download_error").format(error=str(e))
                )
            except Exception as e:
                logger.error(
                    f"Error sending preview to user {user_id}, track_id: {track_id}: {str(e)}"
                )
                await query.message.reply_text(
                    get_message(language, "error").format(error=str(e))
                )
    elif callback_data.startswith("select_quality_"):
        track_id = callback_data.split("_")[1]
        logger.info(
            f"User {user_id} requested quality selection for track_id: {track_id}"
        )
        # Create quality selection buttons
        keyboard = [
            [
                InlineKeyboardButton(
                    "128 kbps", callback_data=f"download_song_{track_id}_128"
                ),
                InlineKeyboardButton(
                    "320 kbps", callback_data=f"download_song_{track_id}_320"
                ),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            get_message(language, "select_quality_prompt"), reply_markup=reply_markup
        )
        logger.info(f"Sent quality selection prompt to user {user_id}")
    elif callback_data.startswith("download_song_"):
        _, track_id, quality = callback_data.split("_")
        spotify_url = f"https://open.spotify.com/track/{track_id}"
        logger.info(
            f"User {user_id} requested song download, track_id: {track_id}, quality: {quality}kbps, url: {spotify_url}"
        )
        try:
            # Get spotdl client
            spotdl = get_spotdl_client()
            # Create downloads directory if it doesn't exist
            os.makedirs("data/downloads", exist_ok=True)
            # Download the song with specified bitrate
            songs = spotdl.search([spotify_url])
            if songs:
                song = songs[0]
                # Set bitrate in downloader settings
                spotdl.downloader_settings.bitrate = f"{quality}k"
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
                    logger.info(
                        f"Sent song audio to user {user_id}: {song.name} by {song.artist}, quality: {quality}kbps"
                    )
                else:
                    logger.error(
                        f"Song download failed for user {user_id}, track_id: {track_id}: File not found"
                    )
                    await query.message.reply_text(
                        get_message(language, "download_error")
                    )
            else:
                logger.error(
                    f"Song search failed for user {user_id}, track_id: {track_id}: No songs found"
                )
                await query.message.reply_text(get_message(language, "download_error"))
        except Exception as e:
            logger.error(
                f"Error downloading song for user {user_id}, track_id: {track_id}, quality: {quality}kbps: {str(e)}"
            )
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
    logger.error(
        f"Error occurred for user {update.effective_user.id if update and update.effective_user else 'unknown'}: {error_message}"
    )
    if "BadRequest" in error_message:
        error_message = get_message(language, "telegram_error")
    (
        await update.message.reply_text(error_message)
        if update and update.message
        else None
    )
