"""
Database Manager
----------------
Handles all SQLite communication.

No other file should connect directly to SQLite.
"""

import sqlite3
from pathlib import Path


class DatabaseManager:

    def __init__(self, database_path: Path):

        self.database_path = database_path
        self.connection = None
        self.cursor = None

    def connect(self):

        if self.connection is None:

            self.connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False
            )

            self.connection.row_factory = sqlite3.Row

            self.cursor = self.connection.cursor()

    def execute(self, query, parameters=()):

        self.connect()

        self.cursor.execute(query, parameters)

        return self.cursor.fetchall()

    def execute_one(self, query, parameters=()):

        self.connect()

        self.cursor.execute(query, parameters)

        return self.cursor.fetchone()

    def close(self):

        if self.connection:

            self.connection.close()

            self.connection = None

            self.cursor = None
