import json
from datetime import datetime

from db_init_ import get_db


def get_transcription(session_id):
    row = get_db().execute(
        """
        SELECT session_id, path_in_webserver, report_path_in_webserver, status
        FROM transcription_table
        WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()
    return dict(row) if row else None


def save_transcription(session_id, path, report_path, status):
    connection = get_db()
    connection.execute(
        """
        INSERT INTO transcription_table (
            session_id, path_in_webserver, report_path_in_webserver, status
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            path_in_webserver = excluded.path_in_webserver,
            report_path_in_webserver = excluded.report_path_in_webserver,
            status = excluded.status
        """,
        (session_id, path, report_path, status),
    )
    connection.commit()


def get_history(session_id):
    row = get_db().execute(
        """
        SELECT session_id, history, updated_at
        FROM history_table
        WHERE session_id = ?
        """,
        (session_id,),
    ).fetchone()
    if row is None:
        return None

    result = dict(row)
    if result["history"] is not None:
        result["history"] = json.loads(result["history"])
    if result["updated_at"]:
        result["updated_at"] = datetime.fromisoformat(result["updated_at"])
    return result


def save_history(session_id, history):
    connection = get_db()
    connection.execute(
        """
        INSERT INTO history_table (session_id, history, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(session_id) DO UPDATE SET
            history = excluded.history,
            updated_at = CURRENT_TIMESTAMP
        """,
        (session_id, json.dumps(history)),
    )
    connection.commit()


def get_sessions():
    rows = get_db().execute(
        """
        SELECT
            history_table.session_id,
            history_table.history,
            history_table.updated_at,
            transcription_table.status
        FROM history_table
        LEFT JOIN transcription_table
            ON transcription_table.session_id = history_table.session_id
        ORDER BY history_table.updated_at DESC
        """
    ).fetchall()

    sessions = []
    for row in rows:
        session = dict(row)
        if session["history"] is not None:
            session["history"] = json.loads(session["history"])
        if session["updated_at"]:
            session["updated_at"] = datetime.fromisoformat(session["updated_at"])
        sessions.append(session)
    return sessions


def save_completed_analysis(session_id, report_path, history):
    connection = get_db()
    try:
        row = connection.execute(
            "SELECT 1 FROM transcription_table WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            return False

        connection.execute(
            """
            UPDATE transcription_table
            SET report_path_in_webserver = ?, status = ?
            WHERE session_id = ?
            """,
            (report_path, "completed", session_id),
        )
        connection.execute(
            """
            INSERT INTO history_table (session_id, history, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(session_id) DO UPDATE SET
                history = excluded.history,
                updated_at = CURRENT_TIMESTAMP
            """,
            (session_id, json.dumps(history)),
        )
        connection.commit()
        return True
    except Exception:
        connection.rollback()
        raise
