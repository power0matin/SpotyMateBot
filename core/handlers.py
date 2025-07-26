from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_user_language, save_user_language
from utils.i18n import get_message
from services.spotify import process_spotify_link
import re
import requests
import os
import tempfile
import shutil
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
        try:
            _spotdl_client = Spotdl(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                downloader_settings=DownloaderOptions(
                    output="data/downloads/{chat_id}_{message_id}"
                ),
            )
            logger.info("Spotdl client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize spotdl client: {str(e)}")
            raise
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
    language = query.data.split("_")[1]
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
                        callback_data=f"select_quality_{track_info['track_id']}_{update.effective_chat.id}_{update.message.message_id}",
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
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
        try:
            recommendations = process_spotify_link(
                f"spotify:track:{track_id}", language, get_recommendations=True
            )
            if isinstance(recommendations, list) and recommendations:
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
        except Exception as e:
            logger.error(
                f"Error fetching similar songs for user {user_id}, track_id: {track_id}: {str(e)}"
            )
            await query.message.reply_text(
                get_message(language, "error").format(
                    error="Failed to fetch similar songs. Please try again later."
                )
            )
    elif callback_data.startswith("download_preview_"):
        try:
            parts = callback_data.split("_", 2)
            if len(parts) != 3:
                raise ValueError("Invalid download_preview format")
            _, track_id, preview_url = parts
            logger.info(
                f"User {user_id} requested preview download, track_id: {track_id}, preview_url: {preview_url}"
            )
            if preview_url == "no_preview" or not preview_url:
                logger.warning(
                    f"No preview available for user {user_id}, track_id: {track_id}"
                )
                await query.message.reply_text(get_message(language, "no_preview"))
                return
            response = requests.get(preview_url, timeout=10)
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            with open(tmp_file_path, "rb") as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=get_message(language, "download_preview_caption"),
                )
            os.unlink(tmp_file_path)
            logger.info(f"Sent preview audio to user {user_id}, track_id: {track_id}")
        except ValueError as e:
            logger.error(
                f"Invalid callback_data format for user {user_id}: {callback_data}, error: {str(e)}"
            )
            await query.message.reply_text(
                get_message(language, "error").format(error="Invalid button data")
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
        try:
            parts = callback_data.split("_")
            if len(parts) != 5 or parts[1] != "quality":
                raise ValueError("Invalid select_quality format")
            _, _, track_id, chat_id, message_id = parts
            logger.info(
                f"User {user_id} requested quality selection for track_id: {track_id}, chat_id: {chat_id}, message_id: {message_id}"
            )
            keyboard = [
                [
                    InlineKeyboardButton(
                        "128 kbps",
                        callback_data=f"download_song_{track_id}_{chat_id}_{message_id}_128",
                    ),
                    InlineKeyboardButton(
                        "320 kbps",
                        callback_data=f"download_song_{track_id}_{chat_id}_{message_id}_320",
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                get_message(language, "select_quality_prompt"),
                reply_markup=reply_markup,
            )
            logger.info(f"Sent quality selection prompt to user {user_id}")
        except ValueError as e:
            logger.error(
                f"Invalid callback_data format for user {user_id}: {callback_data}, error: {str(e)}"
            )
            await query.message.reply_text(
                get_message(language, "error").format(error="Invalid button data")
            )
    elif callback_data.startswith("download_song_"):
        try:
            parts = callback_data.split("_")
            if len(parts) != 5 or parts[0] != "download" or parts[1] != "song":
                raise ValueError("Invalid download_song format")
            track_id, chat_id, message_id, quality = parts[2], parts[3], parts[4]
            if quality not in ["128", "320"]:
                raise ValueError("Invalid quality value")
            spotify_url = f"https://open.spotify.com/track/{track_id}"
            logger.info(
                f"User {user_id} requested song download, track_id: {track_id}, quality: {quality}kbps, url: {spotify_url}"
            )
            fetching_msg = await query.message.reply_text(
                get_message(language, "fetching")
            )
            spotdl = get_spotdl_client()
            download_dir = f"data/downloads/{chat_id}_{message_id}"
            os.makedirs(download_dir, exist_ok=True)
            try:
                songs = spotdl.search([spotify_url])
                if not songs:
                    logger.error(
                        f"Song search failed for user {user_id}, track_id: {track_id}: No songs found"
                    )
                    await fetching_msg.edit_text(
                        get_message(language, "download_error")
                    )
                    shutil.rmtree(download_dir, ignore_errors=True)
                    return
                song = songs[0]
                spotdl.downloader_settings.bitrate = f"{quality}k"
                song_path = spotdl.download(song)
                if os.path.exists(song_path):
                    with open(song_path, "rb") as audio_file:
                        await query.message.reply_audio(
                            audio=audio_file,
                            caption=get_message(
                                language, "download_song_caption"
                            ).format(title=song.name, artist=song.artist),
                            timeout=1000,
                        )
                    os.unlink(song_path)
                    logger.info(
                        f"Sent song audio to user {user_id}: {song.name} by {song.artist}, quality: {quality}kbps"
                    )
                else:
                    logger.error(
                        f"Song download failed for user {user_id}, track_id: {track_id}: File not found"
                    )
                    await fetching_msg.edit_text(
                        get_message(language, "download_error")
                    )
            except Exception as e:
                logger.error(
                    f"Spotdl download error for user {user_id}, track_id: {track_id}: {str(e)}"
                )
                await fetching_msg.edit_text(get_message(language, "download_error"))
            finally:
                shutil.rmtree(download_dir, ignore_errors=True)
        except ValueError as e:
            logger.error(
                f"Invalid callback_data format for user {user_id}: {callback_data}, error: {str(e)}"
            )
            await query.message.reply_text(
                get_message(language, "error").format(error="Invalid button data")
            )
        except Exception as e:
            logger.error(
                f"Error downloading song for user {user_id}, track_id: {track_id}, quality: {quality}kbps: {str(e)}"
            )
            await query.message.reply_text(
                get_message(language, "error").format(error=str(e))
            )
            shutil.rmtree(download_dir, ignore_errors=True)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    if update and update.message:
        await update.message.reply_text(error_message)
