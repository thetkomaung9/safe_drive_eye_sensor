"""SQLite 데이터베이스: 졸음 기록 저장"""
import sqlite3
from datetime import datetime


def now():
    return datetime.now().isoformat(timespec="seconds")


class EventDB:
    def __init__(self, path="drowsiness.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS sessions(
            id INTEGER PRIMARY KEY AUTOINCREMENT, start_time TEXT, end_time TEXT)""")
        self.conn.execute("""CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER,
            time TEXT, event_type TEXT, closed_sec REAL,
            FOREIGN KEY(session_id) REFERENCES sessions(id))""")
        self.conn.commit()

    def start_session(self):
        cur = self.conn.execute("INSERT INTO sessions(start_time) VALUES(?)", (now(),))
        self.conn.commit()
        return cur.lastrowid

    def end_session(self, session_id):
        self.conn.execute("UPDATE sessions SET end_time=? WHERE id=?", (now(), session_id))
        self.conn.commit()

    def log_event(self, session_id, event_type, closed_sec):
        self.conn.execute(
            "INSERT INTO events(session_id, time, event_type, closed_sec) VALUES(?,?,?,?)",
            (session_id, now(), event_type, round(closed_sec, 2)))
        self.conn.commit()

    def session_summary(self):
        """세션별 졸음 횟수와 최대 지속 시간"""
        return self.conn.execute("""
            SELECT s.id, s.start_time, s.end_time, COUNT(e.id), COALESCE(MAX(e.closed_sec), 0)
            FROM sessions s LEFT JOIN events e ON e.session_id = s.id
            GROUP BY s.id ORDER BY s.id DESC""").fetchall()

    def recent_events(self, limit=10):
        return self.conn.execute(
            "SELECT session_id, time, event_type, closed_sec FROM events ORDER BY id DESC LIMIT ?",
            (limit,)).fetchall()

    def close(self):
        self.conn.close()
