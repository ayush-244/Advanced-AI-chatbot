import sqlite3
import os


class ChatMemory:

    def __init__(self):

        # Database file path
        self.db_path = "chat_memory.db"

        # Create database if not exists
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)

        self.cursor = self.conn.cursor()

        # Create table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_text TEXT,
                bot_text TEXT
            )
        """)

        self.conn.commit()


    def save(self, user_text, bot_text):

        self.cursor.execute(
            "INSERT INTO memory (user_text, bot_text) VALUES (?, ?)",
            (user_text, bot_text)
        )

        self.conn.commit()


    def get_last_messages(self, limit=5):

        self.cursor.execute(
            "SELECT user_text, bot_text FROM memory ORDER BY id DESC LIMIT ?",
            (limit,)
        )

        rows = self.cursor.fetchall()

        rows.reverse()

        return rows
