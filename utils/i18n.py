MESSAGES = {
    "fa": {
        "welcome": "🎵 به @SpotyMateBot خوش اومدی! حالا می‌تونی از امکانات بات استفاده کنی. 🎧\nبرای شروع، یه لینک اسپاتیفای بفرست یا از دستور /help استفاده کن.",
        "language_selected": "زبان {language} انتخاب شد! حالا می‌تونی از امکانات بات استفاده کنی. 🎧",
        "help": "🎵 @SpotyMateBot - دوست موسیقایی تو!\nدستورات:\n/start - شروع بات\n/setlanguage - تغییر زبان بات\n/help - نمایش راهنما\nلینک اسپاتیفای بفرست تا اطلاعاتش رو ببینیم!",
        "set_language_prompt": "لطفاً زبان موردنظرت رو انتخاب کن:",
        "track_info": (
            "🎵 آهنگ: {title}\n"
            "🎤 خواننده: {artist}\n"
            "🎸 ژانر: {genre}\n"
            "⏱ مدت زمان: {duration}\n"
            "📅 تاریخ انتشار: {release_date}\n"
            "🔊 پیش‌نمایش: {preview_url}"
        ),
        "unsupported_link": "لینک ارسالی پشتیبانی نمی‌شه. فقط لینک آهنگ (track) قبول می‌شه!",
        "error": "خطا: {error}",
        "telegram_error": "خطایی در تلگرام رخ داد. لطفاً دوباره امتحان کنید یا با پشتیبانی تماس بگیرید.",
        "similar_songs_button": "آهنگ‌های مشابه",
        "more_info_button": "اطلاعات بیشتر",
        "download_preview_button": "دانلود پیش‌نمایش",
        "download_song_button": "دانلود آهنگ",
        "similar_songs": "🎶 آهنگ‌های مشابه:\n{songs}",
        "similar_songs_placeholder": "این قابلیت هنوز پیاده‌سازی نشده! به‌زودی اضافه می‌شه. 🎶",
        "no_preview": "بدون پیش‌نمایش",
        "no_genre": "بدون ژانر",
        "download_preview_caption": "پیش‌نمایش 30 ثانیه‌ای آهنگ 🎶",
        "download_song_caption": "آهنگ: {title} - {artist} 🎶",
        "download_error": "خطا در دانلود آهنگ. لطفاً دوباره امتحان کنید.",
    },
    "en": {
        "welcome": "🎵 Welcome to @SpotyMateBot! Now you can enjoy the bot's features. 🎧\nSend a Spotify link or use /help to get started.",
        "language_selected": "Language set to {language}! Now you can enjoy the bot's features. 🎧",
        "help": "🎵 @SpotyMateBot - Your music buddy!\nCommands:\n/start - Start the bot\n/setlanguage - Change bot language\n/help - Show help\nSend a Spotify link to get its details!",
        "set_language_prompt": "Please choose your language:",
        "track_info": (
            "🎵 Track: {title}\n"
            "🎤 Artist: {artist}\n"
            "🎸 Genre: {genre}\n"
            "⏱ Duration: {duration}\n"
            "📅 Release Date: {release_date}\n"
            "🔊 Preview: {preview_url}"
        ),
        "unsupported_link": "This link is not supported. Only track links are accepted!",
        "error": "Error: {error}",
        "telegram_error": "An error occurred with Telegram. Please try again or contact support.",
        "similar_songs_button": "Similar Songs",
        "more_info_button": "More Info",
        "download_preview_button": "Download Preview",
        "download_song_button": "Download Song",
        "similar_songs": "🎶 Similar songs:\n{songs}",
        "similar_songs_placeholder": "This feature is not implemented yet! Coming soon. 🎶",
        "no_preview": "No preview available",
        "no_genre": "No genre available",
        "download_preview_caption": "30-second preview of the track 🎶",
        "download_song_caption": "Song: {title} - {artist} 🎶",
        "download_error": "Error downloading song. Please try again.",
    },
}


def get_message(language: str, key: str) -> str:
    """Retrieve a message in the specified language."""
    return MESSAGES.get(language, MESSAGES["en"]).get(
        key, MESSAGES["en"]["error"].format(error="Message not found")
    )
