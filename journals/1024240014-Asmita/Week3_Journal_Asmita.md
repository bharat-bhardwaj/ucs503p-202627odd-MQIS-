# MQIS Project Journal — Asmita (RAG/Reporting Track)

## Week 3 : Structuring the Factory Knowledge Base for Retrieval

### Problem
Drafting the initial `.txt` factory knowledge base (defect causes, maintenance notes) for later embedding. First draft was written as free-flowing paragraphs, e.g.:

> "Sometimes scratches appear on parts from Line 2, this is usually because the clamp holding the part has worn down over time and needs replacing, which maintenance should check every few weeks..."

### Key Observation
Long, multi-fact paragraphs are a bad unit for retrieval — if a chunk gets split mid-paragraph (or embedded as one large chunk), the retriever either returns irrelevant context or misses the specific fact needed to answer a targeted question like "why is Line 1 rejecting more today?"

### Solution
Rewrote notes as short, single-fact entries, one defect-cause pattern per block, consistently structured:
```
Defect: Scratch pattern (linear, shallow)
Line: 2
Likely Cause: Worn clamp
Action: Inspect/replace clamp; check every 2 weeks
```
This keeps each retrievable unit self-contained and maps naturally onto later embedding + chunk metadata (line ID, defect type) for filtered retrieval.

**Because**
Retrieval quality in RAG depends heavily on chunk granularity matching query granularity — a query about one line/defect type should map to one clean chunk, not require correctly slicing a paragraph, since the vector store (Chroma) is going to be doing similarity search on these units directly (Week 5).
