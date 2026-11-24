import sqlite3
import hashlib
import secrets

DB_NAME = "users.db"


def initialize_db():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_user(username, password):

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    ).hex()

    try:
        conn = sqlite3.connect(DB_NAME)

        conn.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )

        conn.commit()
        conn.close()

        return True

    except sqlite3.IntegrityError:
        return False


def verify_user(username, password):

    conn = sqlite3.connect(DB_NAME)

    result = conn.execute(
        "SELECT password_hash, salt FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    conn.close()

    if result is None:
        return False

    stored_hash, salt = result

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    ).hex()

    return secrets.compare_digest(stored_hash, password_hash)