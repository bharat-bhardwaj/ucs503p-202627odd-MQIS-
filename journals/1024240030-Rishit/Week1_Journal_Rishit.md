# MQIS Project Journal — Rishit (Database/Analytics Track)

## Week 1 : Defining the Event Logging Schema

### Context
Task for the week was to define the database schema for event logging — the table(s) that every inspection (pass or reject) gets written to, which the analytics engine and RAG assistant will both read from later.

### Error / Confusion
First draft of the schema stored `severity` and `confidence` as free-text fields:
```sql
CREATE TABLE inspections (
    id INTEGER PRIMARY KEY,
    line_id TEXT,
    defect_type TEXT,
    severity TEXT,
    confidence TEXT,
    timestamp TEXT
);
```
This looked fine for a single insert, but the moment the analytics module tries to compute per-line rejection rates or bucket by confidence threshold (Section 4.1, live analytics engine), text fields can't be aggregated or filtered numerically without a cast on every query.

### Key Observation
The proposal treats analytics as a first-class consumer of this table (rejection rate, status flags, hourly trend data), not just a log. The schema needs to be designed for the read pattern (aggregation), not just the write pattern (one row per inspection).

### Solution
Revised schema to use proper numeric and datetime types:
```sql
CREATE TABLE inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_id TEXT NOT NULL,
    defect_type TEXT,
    severity REAL,
    confidence REAL,
    is_reject INTEGER NOT NULL,  -- 0/1, avoids parsing pass/fail strings later
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
Also added `is_reject` as an explicit boolean flag rather than inferring it from defect_type, since "pass" inspections still need to be logged (Section 4.1: "every inspection — pass or reject").

**Because**
> A schema decided in isolation from its downstream queries tends to force costly rewrites later — since Rishit's own Week 7–9 tasks (rejection rate, by-line/by-type/by-hour breakdowns, status flags) all read directly from this table, getting types and the reject flag right now avoids re-migrating data mid-semester.
