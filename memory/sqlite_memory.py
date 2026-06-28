"""
Task 7: SQLite-based memory to store and retrieve customer conversation history.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "memory.db"


def init_db():
    """Initialize the SQLite database and create tables if not exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,           -- 'user' or 'assistant'
            message TEXT NOT NULL,
            intent TEXT,
            metadata TEXT                 -- JSON blob for extras
        )
    """)
    conn.commit()
    conn.close()
    print(f"[Memory] DB initialized at {DB_PATH}")


def save_turn(customer_id: str, user_msg: str, assistant_msg: str, intent: str = None):
    """Save a full conversation turn (user + assistant)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    ts = datetime.now().isoformat()

    cursor.execute(
        "INSERT INTO conversations (customer_id, timestamp, role, message, intent) VALUES (?, ?, ?, ?, ?)",
        (customer_id, ts, "user", user_msg, intent),
    )
    cursor.execute(
        "INSERT INTO conversations (customer_id, timestamp, role, message, intent) VALUES (?, ?, ?, ?, ?)",
        (customer_id, ts, "assistant", assistant_msg, intent),
    )
    conn.commit()
    conn.close()


def get_history(customer_id: str, limit: int = 10) -> list[dict]:
    """Retrieve last N conversation turns for a customer."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT role, message, intent, timestamp
        FROM conversations
        WHERE customer_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (customer_id, limit * 2),  # *2 because each turn = 2 rows
    )
    rows = cursor.fetchall()
    conn.close()

    history = []
    for role, message, intent, timestamp in reversed(rows):
        history.append({"role": role, "message": message, "intent": intent, "timestamp": timestamp})
    return history


def format_history_for_prompt(history: list[dict]) -> str:
    """Format history list into readable string for LLM context."""
    if not history:
        return "No previous conversation history."
    lines = []
    for h in history:
        lines.append(f"[{h['timestamp'][:19]}] {h['role'].upper()}: {h['message']}")
    return "\n".join(lines)
