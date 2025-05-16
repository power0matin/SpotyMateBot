from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_user_language, save_user_language
from utils.i18n import get_message
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os


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


def process_spotify_link(
    link: str, language: str, get_recommendations: bool = False
) -> dict | str | list:
    """Process a Spotify link and return track information or recommendations."""
    try:
        sp = get_spotify_client()
        if get_recommendations:
            track_id = link.split(":")[-1]
            recommendations = sp.recommendations(seed_tracks=[track_id], limit=3)
            return [
                {
                    "title": track["name"],
                    "artist": track["artists"][0]["name"],
                    "track_id": track["id"],
                }
                for track in recommendations["tracks"]
            ]
        if "track" in link:
            track = sp.track(link)
            album = sp.album(track["album"]["id"])
            # Convert duration from milliseconds to MM:SS
            duration_ms = track["duration_ms"]
            minutes = duration_ms // 60000
            seconds = (duration_ms % 60000) // 1000
            duration = f"{minutes}:{seconds:02d}"
            # Get genre (from album or artist, if available)
            genres = album.get("genres", []) or sp.artist(
                track["artists"][0]["id"]
            ).get("genres", [])
            genre = genres[0] if genres else None
            return {
                "track_id": track["id"],
                "title": track["name"],
                "artist": track["artists"][0]["name"],
                "cover_url": (
                    track["album"]["images"][0]["url"]
                    if track["album"]["images"]
                    else None
                ),
                "preview_url": track.get("preview_url", None),
                "genre": genre,
                "duration": duration,
                "release_date": album.get("release_date", "Unknown"),
            }
        else:
            return get_message(language, "unsupported_link")
    except Exception as e:
        return get_message(language, "error").format(error=str(e))


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


def get_spotify_client():
    """Get or initialize the global Spotify client."""
    global _spotify_client
    if _spotify_client is None:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        _spotify_client = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id, client_secret=client_secret
            )
        )
    return _spotify_client
