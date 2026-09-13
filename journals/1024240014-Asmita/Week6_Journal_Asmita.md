# MQIS Project Journal — Asmita (RAG/Reporting Track)

## Week 6 : Milestone 1 — Retrieval Returns Relevant Chunks (But Ranked Oddly)

### Context
Week 6 milestone target was retrieval returning relevant chunks from the knowledge base built in Weeks 3–5. Ran the first end-to-end retrieval test:
```python
results = collection.query(
    query_texts=["why does Line 2 have scratches?"],
    n_results=3
)
```

### Error / Confusion
Retrieval technically "worked" — no exceptions, results came back — but the top-ranked chunk was a generic maintenance-schedule note, not the specific `Line 2 / scratch / worn clamp` entry from Week 3, which showed up third.

### Key Observation
The query embedding for "why does Line 2 have scratches?" is a natural-language question, while the stored chunks are terse structured facts (`Defect: Scratch pattern... Line: 2... Likely Cause: Worn clamp`). The phrasing mismatch between conversational queries and note-style chunks was pulling similarity scores toward chunks that happened to share more surface vocabulary (e.g., "maintenance," "schedule") rather than the semantically correct one.

### Solution
Two changes, tested independently:
1. Added a short natural-language restatement line to each chunk at ingestion time so chunk phrasing is closer to how questions will actually be asked:
   ```
   Defect: Scratch pattern (linear, shallow)
   Line: 2
   Likely Cause: Worn clamp
   Action: Inspect/replace clamp; check every 2 weeks
   Summary: Line 2 scratches are usually caused by a worn clamp.
   ```
2. Increased `n_results` from 3 to 5 and re-ranked by filtering to chunks whose `Line` metadata matches any line number mentioned in the query, when present.

Re-ran the same test query — the correct chunk moved to rank 1.

**Because**
Milestone 1 only requires "retrieval returns relevant chunks," not perfect ranking, but catching this now — while the knowledge base is still small (a handful of notes) — is far cheaper than debugging ranking quality later once report generation (Week 8) depends on retrieval actually surfacing the right fact first.
