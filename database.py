"""SQLite 데이터베이스: 졸음 기록 저장"""
import sqlite3
from datetime import datetime


def now():
    return datetime.now().isoformat(timespec="seconds")


class EventDB:
    ALERT_LEVELS = ("WARNING", "PULL_OVER")

    def __init__(self, path="drowsiness.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS sessions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, start_time TEXT, end_time TEXT)""")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER,
            time TEXT, event_type TEXT, closed_sec REAL,
            alert_level TEXT CHECK(
                alert_level IS NULL OR alert_level IN ('WARNING', 'PULL_OVER')
            ),
            FOREIGN KEY(session_id) REFERENCES sessions(id))""")
        columns = {row[1] for row in self.conn.execute("PRAGMA table_info(events)")}
        if "alert_level" not in columns:
            self.conn.execute("ALTER TABLE events ADD COLUMN alert_level TEXT")
        self.conn.execute(
            """UPDATE events
               SET alert_level = event_type
               WHERE alert_level IS NULL AND event_type IN (?, ?)""",
            self.ALERT_LEVELS,
        )
        self.conn.commit()

    def start_session(self):
        cur = self.conn.execute("INSERT INTO sessions(start_time) VALUES(?)", (now(),))
        self.conn.commit()
        return cur.lastrowid

    def end_session(self, session_id):
        self.conn.execute("UPDATE sessions SET end_time=? WHERE id=?", (now(), session_id))
        self.conn.commit()

    def log_event(self, session_id, event_type, closed_sec, alert_level=None):
        if alert_level is not None and alert_level not in self.ALERT_LEVELS:
            raise ValueError(
                f"alert_level must be one of {self.ALERT_LEVELS}, got {alert_level!r}"
            )
        self.conn.execute(
            """INSERT INTO events(
                session_id, time, event_type, closed_sec, alert_level
            ) VALUES(?,?,?,?,?)""",
            (session_id, now(), event_type, round(closed_sec, 2), alert_level))
        self.conn.commit()

    def session_summary(self):
        """세션별 졸음 횟수와 최대 지속 시간"""
        return self.conn.execute("""
            SELECT s.id, s.start_time, s.end_time, COUNT(e.id), COALESCE(MAX(e.closed_sec), 0)
            FROM sessions s LEFT JOIN events e ON e.session_id = s.id
            GROUP BY s.id ORDER BY s.id DESC""").fetchall()

    def alert_summary(self):
        """Return total drowsy, warning, pull-over, and longest duration counts."""
        return self.conn.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(CASE WHEN alert_level = 'WARNING' THEN 1 ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN alert_level = 'PULL_OVER' THEN 1 ELSE 0 END), 0),
                COALESCE(MAX(closed_sec), 0)
            FROM events
            WHERE event_type = 'DROWSY'
        """).fetchone()

    def recent_events(self, limit=10, include_alert_level=False):
        columns = "session_id, time, event_type, closed_sec"
        if include_alert_level:
            columns += ", alert_level"
        return self.conn.execute(
            f"SELECT {columns} FROM events ORDER BY id DESC LIMIT ?",
            (limit,)).fetchall()

    def close(self):
        self.conn.close()
