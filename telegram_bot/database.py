"""
PrintMaster A4 - User Tracking & Analytics Database
Tracks user profiles, interaction frequency, uploads, and exports using SQLite.
"""

import sqlite3
import io
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from telegram import User

from .config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Creates a connection to the SQLite database with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables for users and event logging."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Users summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT,
                bot_language TEXT DEFAULT 'en',
                first_seen TIMESTAMP,
                last_seen TIMESTAMP,
                interaction_count INTEGER DEFAULT 1,
                images_uploaded INTEGER DEFAULT 0,
                pdf_exports INTEGER DEFAULT 0,
                image_exports INTEGER DEFAULT 0
            )
        """)

        # Migration: ensure bot_language column exists if table was created previously
        cursor.execute("PRAGMA table_info(users)")
        existing_cols = [r["name"] for r in cursor.fetchall()]
        if "bot_language" not in existing_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN bot_language TEXT DEFAULT 'en'")

        # Detailed event activity log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type TEXT,
                details TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Indices for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_time ON activity_log(created_at)")
        conn.commit()


def record_user_interaction(user: User, event_type: str = "interaction", details: Optional[str] = None):
    """
    Upserts the user profile, increments interaction counter, and logs the specific event.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT user_id, interaction_count FROM users WHERE user_id = ?", (user.id,))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE users
                SET username = ?,
                    first_name = ?,
                    last_name = ?,
                    language_code = ?,
                    last_seen = ?,
                    interaction_count = interaction_count + 1
                WHERE user_id = ?
            """, (user.username, user.first_name, user.last_name, user.language_code, now, user.id))
        else:
            cursor.execute("""
                INSERT INTO users (
                    user_id, username, first_name, last_name, language_code,
                    first_seen, last_seen, interaction_count, images_uploaded, pdf_exports, image_exports
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, 0, 0)
            """, (user.id, user.username, user.first_name, user.last_name, user.language_code, now, now))

        # Log detailed event
        cursor.execute("""
            INSERT INTO activity_log (user_id, event_type, details, created_at)
            VALUES (?, ?, ?, ?)
        """, (user.id, event_type, details or "", now))

        conn.commit()


def record_upload(user_id: int):
    """Increments the uploaded images count for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET images_uploaded = images_uploaded + 1 WHERE user_id = ?
        """, (user_id,))
        conn.commit()


def record_export(user_id: int, export_type: str):
    """Increments export count (pdf or image) for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if export_type == "pdf":
            cursor.execute("UPDATE users SET pdf_exports = pdf_exports + 1 WHERE user_id = ?", (user_id,))
        elif export_type == "image":
            cursor.execute("UPDATE users SET image_exports = image_exports + 1 WHERE user_id = ?", (user_id,))
        conn.commit()


def set_user_language(user_id: int, lang: str):
    """Updates the user's preferred bot interface language."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET bot_language = ? WHERE user_id = ?", (lang, user_id))
        conn.commit()


def get_user_language(user_id: int, default_lang: str = "en") -> str:
    """Retrieves the preferred language for a user from database, falling back to Telegram locale or default."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT bot_language, language_code FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row and row["bot_language"]:
                return row["bot_language"]
            if row and row["language_code"]:
                code = str(row["language_code"]).lower()
                if code.startswith("ar"):
                    return "ar"
                elif code.startswith("fr"):
                    return "fr"
    except Exception:
        pass
    return default_lang



def get_overview_stats() -> Dict[str, Any]:
    """Retrieves high-level summary metrics across all users."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

        cursor.execute("SELECT SUM(interaction_count) AS total_interactions FROM users")
        total_interactions = cursor.fetchone()["total_interactions"] or 0

        cursor.execute("SELECT SUM(images_uploaded) AS total_uploads FROM users")
        total_uploads = cursor.fetchone()["total_uploads"] or 0

        cursor.execute("SELECT SUM(pdf_exports) AS total_pdfs FROM users")
        total_pdfs = cursor.fetchone()["total_pdfs"] or 0

        cursor.execute("SELECT SUM(image_exports) AS total_images FROM users")
        total_images = cursor.fetchone()["total_images"] or 0

        # Active users in last 24 hours
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) AS active_24h
            FROM activity_log
            WHERE created_at >= datetime('now', '-1 day')
        """)
        active_24h = cursor.fetchone()["active_24h"]

        # Active users in last 7 days
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) AS active_7d
            FROM activity_log
            WHERE created_at >= datetime('now', '-7 days')
        """)
        active_7d = cursor.fetchone()["active_7d"]

    return {
        "total_users": total_users,
        "total_interactions": total_interactions,
        "total_uploads": total_uploads,
        "total_pdfs": total_pdfs,
        "total_images": total_images,
        "active_24h": active_24h,
        "active_7d": active_7d,
    }


def get_top_users(limit: int = 15) -> List[Dict[str, Any]]:
    """Returns the most active users ordered by total interactions."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username, first_name, last_name,
                   interaction_count, images_uploaded, pdf_exports, image_exports,
                   first_seen, last_seen
            FROM users
            ORDER BY interaction_count DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

    return [dict(row) for row in rows]


def get_recent_activity(limit: int = 15) -> List[Dict[str, Any]]:
    """Returns the most recent events with user details."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.created_at, a.event_type, a.details, u.user_id, u.username, u.first_name
            FROM activity_log a
            LEFT JOIN users u ON a.user_id = u.user_id
            ORDER BY a.id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

    return [dict(row) for row in rows]


def export_users_csv() -> io.BytesIO:
    """Generates an in-memory CSV report containing all users and their metrics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username, first_name, last_name, language_code,
                   first_seen, last_seen, interaction_count,
                   images_uploaded, pdf_exports, image_exports
            FROM users
            ORDER BY last_seen DESC
        """)
        rows = cursor.fetchall()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "User ID", "Username", "First Name", "Last Name", "Language",
        "First Seen (UTC)", "Last Seen (UTC)", "Total Interactions",
        "Images Uploaded", "PDF Exports", "300 DPI Exports"
    ])

    for r in rows:
        uname = f"@{r['username']}" if r["username"] else "N/A"
        writer.writerow([
            r["user_id"],
            uname,
            r["first_name"] or "",
            r["last_name"] or "",
            r["language_code"] or "",
            r["first_seen"],
            r["last_seen"],
            r["interaction_count"],
            r["images_uploaded"],
            r["pdf_exports"],
            r["image_exports"],
        ])

    bytes_buf = io.BytesIO(buf.getvalue().encode("utf-8-sig"))
    bytes_buf.seek(0)
    return bytes_buf
