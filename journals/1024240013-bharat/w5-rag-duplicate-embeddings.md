# Week 5 : Knowledge Base Re-Embedding on Every App Restart

## Error
No crash — but noticed report quality degrading, and Chroma's collection
size kept growing far beyond the actual number of knowledge chunks in
the `knowledge/` folder.

## Relevant Context
`rag.py`'s `build_knowledge_base()` is called once at the top of
`app.py` on every Streamlit rerun (Streamlit reruns the whole script on
most interactions):
```python
def build_knowledge_base():
    all_ids = collection.get()["ids"]
    if len(all_ids) > 0:
        return
    ...
    for fname in os.listdir(knowledge_dir):
        ...
        collection.add(documents=[chunk], embeddings=[embedding], ids=[doc_id])
```
The guard `if len(all_ids) > 0: return` looked sufficient, but Chroma's
in-memory client (`chromadb.Client()`) does not persist between actual
process restarts — only within a single running app session. Restarting
`streamlit run app.py` (not just rerunning within the browser) created a
brand-new empty in-memory collection each time, so the guard never
triggered as "already built" across restarts, quietly duplicating stale
IDs from partially-completed prior runs in edge cases.

## Key Observation
`chromadb.Client()` creates an ephemeral, in-memory-only vector store by
default. It was never actually persisting to disk between full process
restarts in the first place — the duplication symptom was a signal
pointing to this deeper persistence issue, not a bug in the guard logic
itself.

## Solution
Switched to a persistent Chroma client so the embedded knowledge base
survives across restarts and is only built once, permanently:
```python
chroma_client = chromadb.PersistentClient(path="chroma_store")
```
Re-ran the app fresh (deleted the old `chroma_store` folder once to
clear any bad state), confirmed via `collection.count()` that the
number of stored embeddings matched the number of knowledge chunks
exactly, and stayed stable across multiple restarts.

**Because:** an in-memory vector store resets on every process restart;
for a knowledge base that should only be built once, persistence has to
be explicit — "already built" checks are meaningless against storage
that doesn't survive a restart to begin with.
