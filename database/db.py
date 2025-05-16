import sqlite3
import os


def get_db_path():
    """Get the absolute path to the database file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "../data")
    os.makedirs(data_dir, exist_ok=True)  # Create data directory if it doesn't exist
    return os.path.join(data_dir, "users.db")


def init_db():
    """Initialize the SQLite database."""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT
            )
        """
        )
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except sqlite3.OperationalError as e:
        print(f"Error initializing database: {e}")
        raise


def save_user_language(user_id: int, language: str):
    """Save user's language preference."""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)",
            (user_id, language),
        )
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Error saving user language: {e}")
        raise


def get_user_language(user_id: int) -> str:
    """Retrieve user's language preference."""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.OperationalError as e:
        print(f"Error retrieving user language: {e}")
        raise
