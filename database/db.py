import sqlite3

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect("spotymatebot/data/users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user_language(user_id: int, language: str):
    """Save user's language preference."""
    conn = sqlite3.connect("spotymatebot/data/users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)",
        (user_id, language)
    )
    conn.commit()
    conn.close()

def get_user_language(user_id: int) -> str:
    """Retrieve user's language preference."""
    conn = sqlite3.connect("spotymatebot/data/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None