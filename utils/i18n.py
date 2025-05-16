MESSAGES = {
    "fa": {
        "welcome": "🎵 به @SpotyMateBot خوش اومدی! حالا می‌تونی از امکانات بات استفاده کنی. 🎧\nبرای شروع، یه لینک اسپاتیفای بفرست یا از دستور /help استفاده کن.",
        "language_selected": "زبان {language} انتخاب شد! حالا می‌تونی از امکانات بات استفاده کنی. 🎧",
        "help": "🎵 @SpotyMateBot - دوست موسیقایی تو!\nدستورات:\n/start - شروع بات\n/help - راهنما\nلینک اسپاتیفای بفرست تا اطلاعاتش رو ببینیم!",
        "track_info": "🎵 آهنگ: {title}\n🎤 خواننده: {artist}",
        "unsupported_link": "لینک ارسالی پشتیبانی نمی‌شه. فقط لینک آهنگ (track) قبول می‌شه!",
        "error": "خطا: {error}",
    },
    "en": {
        "welcome": "🎵 Welcome to @SpotyMateBot! Now you can enjoy the bot's features. 🎧\nSend a Spotify link or use /help to get started.",
        "language_selected": "Language set to {language}! Now you can enjoy the bot's features. 🎧",
        "help": "🎵 @SpotyMateBot - Your music buddy!\nCommands:\n/start - Start the bot\n/help - Show help\nSend a Spotify link to get its details!",
        "track_info": "🎵 Track: {title}\n🎤 Artist: {artist}",
        "unsupported_link": "This link is not supported. Only track links are accepted!",
        "error": "Error: {error}",
    },
}

def get_message(language: str, key: str) -> str:
    """Retrieve a message in the specified language."""
    return MESSAGES.get(language, MESSAGES["en"]).get(key, MESSAGES["en"]["error"].format(error="Message not found"))