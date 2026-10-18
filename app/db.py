import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"]
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db

def init_db(app):
    db = sqlite3.connect(app.config["DATABASE"])

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL UNIQUE,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL DEFAULT '',
            is_public INTEGER NOT NULL DEFAULT 1,
            owner_id INTEGER
        )
    """)

    db.commit()
    db.close()
