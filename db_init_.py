from contextlib import closing
import os
import sqlite3

from flask import current_app, g


def get_db():
    if "sqlite_db" not in g:
        connection = sqlite3.connect(current_app.config["SQLITE_DATABASE_PATH"])
        connection.row_factory = sqlite3.Row
        g.sqlite_db = connection
    return g.sqlite_db


def close_db(error=None):
    connection = g.pop("sqlite_db", None)
    if connection is not None:
        connection.close()


def init_db(app):
    database_path = app.config["SQLITE_DATABASE_PATH"]
    os.makedirs(os.path.dirname(database_path) or ".", exist_ok=True)

    with closing(sqlite3.connect(database_path)) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS transcription_table (
                session_id TEXT PRIMARY KEY,
                path_in_webserver TEXT,
                report_path_in_webserver TEXT,
                status TEXT
            );

            CREATE TABLE IF NOT EXISTS history_table (
                session_id TEXT PRIMARY KEY,
                history TEXT,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

    app.teardown_appcontext(close_db)
