
## Relevant Context
`analytics.py` computes the peak rejection hour as:
```python
by_hour = df[df["rejected"] == 1].groupby("hour")["rejected"].sum().to_dict()

peak_hour = (
    max(by_hour, key=by_hour.get)
    if by_hour else "N/A"
)
```
This worked correctly once rejections existed, but early in a fresh
testing session — right after clearing the database — every inspection
so far had passed, so `by_hour` was legitimately empty.

## Key Observation
The `if by_hour else "N/A"` guard looked correct at a glance, but the
actual crash was happening one line earlier, inside `get_today_summary()`,
where `by_line["rejection_rate"]` division was being computed before
checking whether `total` (total inspections) was greater than zero in a
nested code path — a separate, but related, empty-data assumption bug
triggered by the same "no data yet" test scenario.

## Solution
Added an explicit guard at the top of `get_today_summary()` (already
partially present for `rows`, but not consistently applied to derived
aggregates):
```python
if not rows:
    return None
```
and confirmed every downstream computation (`by_line`, `by_hour`,
`peak_hour`) only runs after this early return, so partial/empty data
never reaches the aggregation logic in the first place.

**Because:** analytics code that aggregates real-world event logs must
treat "zero events so far" as a normal, expected state — not an edge
case to patch reactively after it crashes the dashboard.
