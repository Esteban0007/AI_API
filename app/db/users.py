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
            password_reset_token TEXT,
            password_reset_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """
    )

    # Create consent_records table for GDPR compliance
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS consent_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_email TEXT NOT NULL,
            consent_status BOOLEAN DEFAULT 1,
            consent_type TEXT DEFAULT 'privacy_policy',
            privacy_version TEXT NOT NULL,
            consent_method TEXT DEFAULT 'Web Form',
            consent_ip TEXT,
            user_agent TEXT,
            consent_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
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


def regenerate_confirmation_token(email: str) -> dict:
    """Generate new confirmation token for unconfirmed user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if user exists and is not confirmed
    c.execute(
        "SELECT id, is_confirmed FROM users WHERE email = ?",
        (email,),
    )
    user = c.fetchone()

    if not user:
        conn.close()
        return {"success": False, "message": "Email not found."}

    user_id, is_confirmed = user

    if is_confirmed:
        conn.close()
        return {"success": False, "message": "Account already confirmed."}

    # Generate new token
    confirmation_token, token_expires = generate_confirmation_token()

    # Update user with new token
    c.execute(
        """
        UPDATE users 
        SET confirmation_token = ?, confirmation_token_expires = ?
        WHERE id = ?
    """,
        (confirmation_token, token_expires, user_id),
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "New confirmation email sent.",
        "confirmation_token": confirmation_token,
    }


def request_password_reset(email: str) -> dict:
    """Request password reset. Generate token and return it."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if user exists
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = c.fetchone()

    if not user:
        conn.close()
        return {"success": False, "message": "Email not found."}

    user_id = user[0]

    # Generate reset token (24h validity)
    reset_token, token_expires = generate_confirmation_token()

    # Update user with reset token
    c.execute(
        """
        UPDATE users 
        SET password_reset_token = ?, password_reset_expires = ?
        WHERE id = ?
    """,
        (reset_token, token_expires, user_id),
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Password reset email sent.",
        "reset_token": reset_token,
    }


def reset_password_with_token(reset_token: str, new_password: str) -> dict:
    """Reset password using token."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT id, email, password_reset_expires 
        FROM users 
        WHERE password_reset_token = ?
    """,
        (reset_token,),
    )

    user = c.fetchone()

    if not user:
        conn.close()
        return {"success": False, "message": "Invalid reset token."}

    user_id, email, expires = user

    # Check if token expired
    if datetime.fromisoformat(expires) < datetime.utcnow():
        conn.close()
        return {"success": False, "message": "Reset token expired."}

    # Update password and clear reset token
    new_password_hash = hash_password(new_password)
    c.execute(
        """
        UPDATE users 
        SET password_hash = ?, password_reset_token = NULL, password_reset_expires = NULL
        WHERE id = ?
    """,
        (new_password_hash, user_id),
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Password reset successfully for {email}.",
        "email": email,
    }


def update_password(email: str, new_password: str) -> dict:
    """Update user password when logged in."""
    conn = get_db_connection()
    c = conn.cursor()

    # Check if user exists
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = c.fetchone()

    if not user:
        conn.close()
        return {"success": False, "message": "User not found."}

    user_id = user[0]
    new_password_hash = hash_password(new_password)

    # Update password
    c.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (new_password_hash, user_id),
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Password updated successfully.",
    }


def save_consent_record(
    user_email: str,
    consent_status: bool = True,
    consent_type: str = "privacy_policy",
    privacy_version: str = "v1.0",
    consent_method: str = "Web Form",
    consent_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    user_id: Optional[int] = None,
) -> dict:
    """
    Save user consent record for GDPR compliance.

    Args:
        user_email: Email of the user giving consent
        consent_status: True if accepting, False if withdrawing
        consent_type: Type of consent (default: privacy_policy)
        privacy_version: Version of policy being accepted (e.g., v1.0)
        consent_method: How consent was given (default: Web Form)
        consent_ip: IP address of the consent action
        user_agent: Browser/User-Agent information
        user_id: Optional user ID if already registered

    Returns:
        dict with success status and message
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        consent_timestamp = datetime.utcnow().isoformat()

        c.execute(
            """
            INSERT INTO consent_records 
            (user_id, user_email, consent_status, consent_type, privacy_version, 
             consent_method, consent_ip, user_agent, consent_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                user_email,
                consent_status,
                consent_type,
                privacy_version,
                consent_method,
                consent_ip,
                user_agent,
                consent_timestamp,
            ),
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": "Consent record saved successfully.",
            "timestamp": consent_timestamp,
        }
    except Exception as e:
        return {"success": False, "message": f"Error saving consent: {str(e)}"}


def get_consent_records(user_email: str) -> list[dict]:
    """Get all consent records for a user (for audit trail)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        c.execute(
            """
            SELECT id, user_id, user_email, consent_status, consent_type, 
                   privacy_version, consent_method, consent_ip, user_agent, 
                   consent_timestamp, created_at
            FROM consent_records
            WHERE user_email = ?
            ORDER BY consent_timestamp DESC
        """,
            (user_email,),
        )

        rows = c.fetchall()
        conn.close()

        return [dict(row) for row in rows]
    except Exception as e:
        return []


# Initialize DB on import
init_db()
