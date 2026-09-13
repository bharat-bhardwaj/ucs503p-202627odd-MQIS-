# MQIS Project Journal — Rishit (Database/Analytics Track)

## Week 6 : Milestone 1 — Logging Pipeline Integrated, But Timestamps Landing Out of Order

### Context
Week 6 milestone target was the logging pipeline fully integrated — detection output (via Week 5's adapter) flowing into the DB automatically, not just via manual test calls.

### Error / Confusion
Ran a short integration test simulating a burst of inspections and then queried the last 10 rows ordered by timestamp:
```python
query("SELECT * FROM inspections ORDER BY timestamp DESC LIMIT 10")
```
A few rows came back visibly out of order relative to the sequence they were actually logged in during the test run.

### Key Observation
`log()` was relying on SQLite's `DEFAULT CURRENT_TIMESTAMP` (set in Week 1's schema) to stamp each row, but `CURRENT_TIMESTAMP` in SQLite only has **second-level** resolution. During the burst test, several inspections were logged within the same second, so their timestamps were identical — and with ties, `ORDER BY timestamp` falls back to arbitrary/insertion-adjacent order, which isn't guaranteed to be stable across queries.

### Solution
Switched to generating timestamps in Python with sub-second precision at log time, rather than relying on SQLite's default:
```python
from datetime import datetime

def log(line_id, defect_type, severity, confidence, is_reject, timestamp=None):
    ts = timestamp or datetime.now().isoformat(timespec="milliseconds")
    conn.execute(
        "INSERT INTO inspections (line_id, defect_type, severity, confidence, is_reject, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (line_id, defect_type, severity, confidence, is_reject, ts)
    )
```
Re-ran the burst test — rows now sort correctly even when logged milliseconds apart.

**Because**
The MTTL metric (Section 6.1, target ≤ 2 seconds per inspection) and the hourly-trend analytics planned for Week 9 both depend on timestamp ordering being reliable at sub-second granularity, since the detection pipeline can realistically log multiple inspections within the same second under normal load — this needed fixing before the Week 11 full-analytics milestone builds on top of it.
