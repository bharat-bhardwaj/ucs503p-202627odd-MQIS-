
## Relevant Context
`database.py` defines the schema in `init()`:
```python
CREATE TABLE IF NOT EXISTS defect_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    line_id TEXT,
    defect_type TEXT,
    severity TEXT,
    confidence REAL,
    rejected INTEGER
)
```
This table had already been created earlier in development, before the
`confidence` column was added to the schema. `CREATE TABLE IF NOT EXISTS`
does not alter an existing table, so the old `defects.db` file on disk
still had the outdated schema, missing the new column entirely.

## Key Observation
`init()` only creates the table if it doesn't already exist — it never
migrates an existing table to match schema changes made later in
development. Since `defects.db` persisted across multiple runs, it
silently kept the stale structure.

## Solution
Deleted the stale local database file so it would be recreated fresh
with the correct up-to-date schema:
```bash
rm defects.db
```
Re-ran `database.init()` (via `streamlit run app.py`), confirmed the new
`confidence` column existed using:
```bash
sqlite3 defects.db ".schema defect_events"
```

**Because:** `CREATE TABLE IF NOT EXISTS` is not a migration tool — schema
changes during development require either deleting the old database file
(fine pre-launch) or writing an explicit `ALTER TABLE` migration once
real data needs to be preserved.
