"""User management with SQLite database."""

import os
import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = "./data/users.db"


def init_db():
    """Initialize database with users table."""
    os.makedirs("./data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            is_confirmed BOOLEAN DEFAULT 0,
            confirmation_token TEXT,
            confirmation_token_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash password with SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_api_key() -> str:
    """Generate a random API key like rapi_..."""
    token = secrets.token_urlsafe(32)
    return f"rapi_{token}"


def generate_confirmation_token() -> tuple[str, datetime]:
    """Generate confirmation token and expiry (24 hours)."""
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=24)
    return token, expires


def register_user(email: str, password: str) -> dict:
    """Register a new user. Returns dict with success, message, api_key."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Check if email already exists
        c.execute("SELECT id FROM users WHERE email = ?", (email,))
        if c.fetchone():
            return {"success": False, "message": "Email ya registrado"}

        # Generate credentials
        password_hash = hash_password(password)
        api_key = generate_api_key()
        confirmation_token, token_expires = generate_confirmation_token()

        # Insert user
        c.execute(
            """
            INSERT INTO users (email, password_hash, api_key, confirmation_token, confirmation_token_expires)
            VALUES (?, ?, ?, ?, ?)
        """,
            (email, password_hash, api_key, confirmation_token, token_expires),
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": "Registro exitoso. Revisa tu email para confirmar.",
            "email": email,
            "confirmation_token": confirmation_token,
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


def get_user(email: str) -> Optional[dict]:
    """Get user by email."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()

    return dict(user) if user else None


def verify_password(email: str, password: str) -> bool:
    """Verify user password."""
    user = get_user(email)
    if not user:
        return False
    return user["password_hash"] == hash_password(password)


def confirm_user(confirmation_token: str) -> dict:
    """Confirm user email with token."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT id, email, confirmation_token_expires 
        FROM users 
        WHERE confirmation_token = ?
    """,
        (confirmation_token,),
    )

    user = c.fetchone()

    if not user:
        return {"success": False, "message": "Token inválido"}

    user_id, email, expires = user

    # Check if token expired
    if datetime.fromisoformat(expires) < datetime.utcnow():
        return {"success": False, "message": "Token expirado"}

    # Mark as confirmed
    c.execute(
        """
        UPDATE users 
        SET is_confirmed = 1, confirmation_token = NULL, confirmation_token_expires = NULL
        WHERE id = ?
    """,
        (user_id,),
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Email confirmado. ¡Bienvenido {email}!",
        "email": email,
    }


def get_user_by_api_key(api_key: str) -> Optional[dict]:
    """Get user by API key (only if confirmed)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE api_key = ? AND is_confirmed = 1", (api_key,))
    user = c.fetchone()
    conn.close()

    return dict(user) if user else None


def update_last_login(email: str):
    """Update last login timestamp."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE email = ?", (email,)
    )
    conn.commit()
    conn.close()


# Initialize DB on import
init_db()
