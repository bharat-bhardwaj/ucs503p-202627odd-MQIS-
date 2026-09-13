# MQIS Project Journal — Rishit (Database/Analytics Track)

## Week 3 : Testing DB Read/Write — Dummy Data Skewing Later Analytics Tests

### Problem
Testing `database.py`'s read/write path with dummy data before wiring in real detection output. Quick test script inserted dummy rows like:
```python
for i in range(20):
    log("Line-1", "scratch", 0.5, 0.9, 1)  # same line, same defect every time
```
The read/write path itself worked, but this dummy set is a poor stand-in for what the analytics module will need to validate against later (Section 6.3: validation plan requires ≥50 inspections across three simulated lines).

### Key Observation
If dummy data doesn't vary line ID, defect type, `is_reject`, and timestamp, it can't catch bugs in `query()` filters (e.g., "get rejections for Line 2 in the last hour") — those queries would trivially "pass" against uniform data even if the WHERE clause were wrong.

### Solution
Rewrote the dummy dataset generator to vary all relevant fields and spread timestamps across a realistic window:
```python
import random
from datetime import datetime, timedelta

lines = ["Line-1", "Line-2", "Line-3"]
defects = ["scratch", "dent", "discoloration", None]  # None = pass

for i in range(60):
    line = random.choice(lines)
    defect = random.choice(defects)
    is_reject = 0 if defect is None else 1
    ts = datetime.now() - timedelta(minutes=random.randint(0, 180))
    log(line, defect, random.uniform(0.1, 1.0), random.uniform(0.5, 1.0), is_reject, ts)
```
Re-ran `query()` calls filtered by line, by hour, and by reject status against this set and confirmed each returns the expected subset.

**Because**
Test data that mirrors the shape of real production variance (multiple lines, mixed pass/reject, spread-out timestamps) is what actually exercises `query()`'s filtering logic — uniform dummy data would have let a filtering bug slip through undetected until Week 13's live validation, which is much later to catch it.
