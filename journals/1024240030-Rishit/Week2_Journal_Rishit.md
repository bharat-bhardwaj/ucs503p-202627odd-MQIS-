# MQIS Project Journal — Rishit (Database/Analytics Track)

## Week 2 : `database.py` — `sqlite3.OperationalError: database is locked`

### Error:
```
sqlite3.OperationalError: database is locked
```

### Relevant Context
Implementing `database.py` with the core `init()`, `log()`, and `query()` functions. Each function was opening its own connection:
```python
def log(line_id, defect_type, severity, confidence, is_reject):
    conn = sqlite3.connect("mqis.db")
    conn.execute(
        "INSERT INTO inspections (line_id, defect_type, severity, confidence, is_reject) VALUES (?, ?, ?, ?, ?)",
        (line_id, defect_type, severity, confidence, is_reject)
    )
    conn.commit()
    conn.close()
```
While testing with a quick loop simulating rapid back-to-back inspections, some `log()` calls started throwing the lock error.

### Key Observation
SQLite allows only one writer at a time, and opening a fresh connection per call (rather than reusing one, or at least serializing writes) increases the chance of overlapping write transactions when calls happen close together — which is exactly the access pattern the detection module will produce once integrated (Section 6.1: MTTL target ≤ 2s per inspection, meaning frequent writes).

### Solution
Set `check_same_thread=False` isn't the fix here — the real fix is enabling WAL mode so reads and writes don't block each other, and adding a short busy timeout so concurrent writes retry instead of failing immediately:
```python
def get_connection():
    conn = sqlite3.connect("mqis.db", timeout=5)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn
```

**Because**
Once the Streamlit dashboard (reading via `query()`) and the detection pipeline (writing via `log()`) run concurrently, WAL mode lets a read not block on an in-progress write. A busy timeout handles the rarer case of two writes overlapping, rather than surfacing the error straight to the caller.
