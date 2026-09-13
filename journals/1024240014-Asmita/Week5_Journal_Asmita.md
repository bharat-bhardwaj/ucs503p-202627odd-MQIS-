# MQIS Project Journal — Asmita (RAG/Reporting Track)

## Week 5 : Chroma Collection Build/Query — Duplicate Entries on Repeated Ingestion

### Error:
```
Add of existing embedding ID: chunk_014
(No exception raised — Chroma just silently skipped/duplicated depending on call)
```

### Relevant Context
Implementing the Chroma collection build and query functions on top of the Week 3 knowledge-base notes and Week 4 embedding pipeline:
```python
def build_collection(chunks):
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embed(chunk)],
            ids=[f"chunk_{i}"]
        )
```
Re-running the ingestion script (e.g., after adding two new factory notes) either warned about existing IDs or, when IDs were generated fresh each run (`chunk_{i}` re-numbered from scratch), silently created duplicate entries with different IDs for the same underlying text.

### Key Observation
The knowledge base is meant to be iteratively expanded (Section 7.2: "extended with additional factory documentation without code changes"), which means ingestion will be re-run many times over the semester — not just once. IDs need to be stable and content-derived, not positional, or every re-run either collides or duplicates.

### Solution
Switched to content-hash IDs so the same note always maps to the same ID, and used `upsert()` instead of `add()` so re-ingesting an edited note updates it in place rather than duplicating:
```python
import hashlib

def make_id(chunk_text):
    return hashlib.sha256(chunk_text.encode()).hexdigest()[:12]

def build_collection(chunks):
    ids = [make_id(c) for c in chunks]
    collection.upsert(
        documents=chunks,
        embeddings=[embed(c) for c in chunks],
        ids=ids
    )
```
Query side (`collection.query(query_texts=[...], n_results=3)`) needed no changes once ingestion was fixed.

**Because**
Since factory notes will be edited and appended incrementally as gaps are found during testing (Section 12, "Knowledge base quality" risk mitigation), the ingestion step has to be idempotent — re-running it on a partially changed note set should converge to the correct state, not accumulate stale duplicate chunks that degrade retrieval quality over time.
