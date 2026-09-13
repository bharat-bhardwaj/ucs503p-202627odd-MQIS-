# MQIS Project Journal — Rishit (Database/Analytics Track)

## Week 4 : Streamlit Shell — App Re-running on Every Widget Interaction

### Error / Symptom
No traceback — the app just behaved unexpectedly. While building the minimal `app.py` skeleton (Section 9.1: "Minimal Streamlit dashboard showing the latest inspection result"), a placeholder "Refresh" button was added to re-fetch from the database:
```python
import streamlit as st
from database import query

st.title("MQIS Dashboard")

if st.button("Refresh"):
    data = query("SELECT * FROM inspections ORDER BY timestamp DESC LIMIT 1")
    st.write(data)
```
Clicking Refresh worked, but any *other* widget added later (even something unrelated like a dropdown to pick a line) caused the whole script to silently re-run from top to bottom, re-hitting the database every time.

### Key Observation
Streamlit's execution model re-runs the entire script top-to-bottom on any widget interaction — this isn't a bug, but it's easy to misdesign around if the mental model is "the script runs once and updates in place." For a dashboard that will later add live stats (Section 4.1: live analytics engine, real-time aggregation), unmanaged re-runs mean redundant DB queries every click, not just on the intended refresh.

### Solution
Used `st.session_state` to control when data actually gets re-fetched versus just re-rendered, isolating the DB call from unrelated widget re-runs:
```python
if "latest" not in st.session_state or st.button("Refresh"):
    st.session_state["latest"] = query(
        "SELECT * FROM inspections ORDER BY timestamp DESC LIMIT 1"
    )

st.write(st.session_state["latest"])
```

**Because**
Once the dashboard grows to include the live stats panel and AI assistant panel (Weeks 10–11) in the same script, every additional widget would otherwise trigger unnecessary re-queries against the database on every interaction. Establishing the session-state pattern now, at the skeleton stage, avoids restructuring the whole app later just to fix performance.
