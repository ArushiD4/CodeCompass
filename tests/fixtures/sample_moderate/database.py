"""Lightweight database wrapper used alongside the user manager demo.

Demo purpose: clean module - adds call-graph structure without adding
additional flagged issues, so this project's score stays purely
attributable to user_manager.py.
"""
import sqlite3


def connect(db_path="users.db"):
    return sqlite3.connect(db_path)


def create_table(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)"
    )


def insert_user(conn, username):
    conn.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()


def fetch_all_users(conn):
    cursor = conn.execute("SELECT username FROM users")
    return cursor.fetchall()
