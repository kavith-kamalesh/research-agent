import sqlite3
import json
from datetime import datetime

DB_PATH = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_message(role, content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sessions (timestamp, role, content) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), role, content)
    )
    conn.commit()
    conn.close()

def load_recent_history(limit=6):
    # Reduced default limit — long old reports were contaminating casual chat
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT role, content FROM sessions ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    rows.reverse()
    return [{"role": role, "content": content} for role, content in rows]

def clear_history():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()

init_db()
