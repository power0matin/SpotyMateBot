import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
from utils.i18n import get_message

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global Spotify client
_spotify_client = None


def get_spotify_client():
    """Get or initialize the global Spotify client."""
    global _spotify_client
    if _spotify_client is None:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        if not client_id or not client_secret:
            logger.error("Spotify client ID or secret not set")
            raise ValueError("Spotify client ID or secret not set")
        _spotify_client = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id, client_secret=client_secret
            )
        )
        logger.info("Spotify client initialized")
    return _spotify_client


def process_spotify_link(
    link: str, language: str, get_recommendations: bool = False
) -> dict | str | list:
    """Process a Spotify link and return track information or recommendations."""
    logger.info(
        f"Processing Spotify link: {link}, recommendations: {get_recommendations}"
    )
    try:
        sp = get_spotify_client()
        if get_recommendations:
            track_id = link.split(":")[-1]
            try:
                recommendations = sp.recommendations(
                    seed_tracks=[track_id], limit=3, market="US"
                )
                if not recommendations["tracks"]:
                    logger.warning(f"No recommendations found for track_id: {track_id}")
                    return get_message(language, "similar_songs_placeholder")
                logger.info(
                    f"Fetched {len(recommendations['tracks'])} recommendations for track_id: {track_id}"
                )
                return [
                    {
                        "title": track["name"],
                        "artist": track["artists"][0]["name"],
                        "track_id": track["id"],
                    }
                    for track in recommendations["tracks"]
                ]
            except spotipy.exceptions.SpotifyException as e:
                logger.error(
                    f"Spotify API error for recommendations, track_id: {track_id}: {str(e)}"
                )
                return get_message(language, "error").format(
                    error="Failed to fetch similar songs"
                )
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
            track_info = {
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
            logger.info(
                f"Processed track info: {track_info['title']} by {track_info['artist']}"
            )
            return track_info
        else:
            logger.warning(f"Unsupported Spotify link: {link}")
            return get_message(language, "unsupported_link")
    except spotipy.exceptions.SpotifyException as e:
        logger.error(f"Spotify API error for link {link}: {str(e)}")
        return get_message(language, "error").format(
            error="Failed to process Spotify link"
        )
    except Exception as e:
        logger.error(f"Error processing Spotify link {link}: {str(e)}")
        return get_message(language, "error").format(error=str(e))
