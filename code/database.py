import sqlite3
from datetime import datetime

DB = "defects.db"

def init():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS defect_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            line_id TEXT,
            defect_type TEXT,
            severity TEXT,
            confidence REAL,
            rejected INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_event(line_id, defect_type, severity, confidence, rejected):
    conn = sqlite3.connect(DB)
    conn.execute("""
        INSERT INTO defect_events 
        (timestamp, line_id, defect_type, severity, confidence, rejected)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        line_id,
        defect_type,
        severity,
        confidence,
        int(rejected)
    ))
    conn.commit()
    conn.close()

def get_today():
    conn = sqlite3.connect(DB)
    today = datetime.now().strftime("%Y-%m-%d")
    rows = conn.execute("""
        SELECT * FROM defect_events 
        WHERE timestamp LIKE ?
        ORDER BY timestamp DESC
    """, (f"{today}%",)).fetchall()
    conn.close()
    return rows

def get_all():
    conn = sqlite3.connect(DB)
    rows = conn.execute("""
        SELECT * FROM defect_events 
        ORDER BY timestamp DESC
        LIMIT 100
    """).fetchall()
    conn.close()
    return rows

def clear_today():
    conn = sqlite3.connect(DB)
    today = datetime.now().strftime("%Y-%m-%d")
    conn.execute("""
        DELETE FROM defect_events 
        WHERE timestamp LIKE ?
    """, (f"{today}%",))
    conn.commit()
    conn.close()