"""
SQLite Database manager for ForgeBot
Keeps track of processed comments and conversations to prevent duplicate replies.
"""

import os
import tempfile
import sqlite3
from pathlib import Path
from datetime import datetime

if os.getenv("VERCEL"):
    DB_PATH = Path(tempfile.gettempdir()) / "bot_data.db"
else:
    DB_PATH = Path(__file__).parent / "bot_data.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_comments (
                comment_id TEXT PRIMARY KEY,
                media_id TEXT,
                username TEXT,
                comment_text TEXT,
                reply_sent TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                sender_id TEXT PRIMARY KEY,
                username TEXT,
                last_message TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def is_comment_processed(comment_id: str) -> bool:
    with get_db() as conn:
        cur = conn.execute("SELECT 1 FROM processed_comments WHERE comment_id = ?", (comment_id,))
        return cur.fetchone() is not None


def mark_comment_processed(comment_id: str, media_id: str, username: str, comment_text: str, reply_sent: str):
    with get_db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO processed_comments 
            (comment_id, media_id, username, comment_text, reply_sent, processed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (comment_id, media_id, username, comment_text, reply_sent, datetime.utcnow()))
        conn.commit()


def get_all_processed_count() -> int:
    with get_db() as conn:
        cur = conn.execute("SELECT count(*) as count FROM processed_comments")
        row = cur.fetchone()
        return row["count"] if row else 0


init_db()
