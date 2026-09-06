# MQIS Project Journal — Asmita (RAG/Reporting Track)

## Week 1 : Choosing the Embedding Model for the RAG Stack

### Context
Task for the week was to survey the RAG stack (Chroma, embeddings, Ollama) and lock in a plan before implementation starts in Week 4.

### Error / Confusion
Initial plan was to use `sentence-transformers/all-mpnet-base-v2` for embeddings since it's the most commonly cited model in tutorials. On checking system constraints (Section 4.3 of the proposal — no dedicated GPU, laptop-class hardware only), this model is noticeably slower on CPU-only inference for a knowledge base that will keep growing.

### Key Observation
The proposal explicitly commits to open, inspectable, lightweight components (Section 8) and a dataset-agnostic, extensible knowledge base (Section 7.2). A heavier embedding model works against both constraints even if it's marginally more accurate.

### Solution
Standardized on `all-MiniLM-L6-v2` (also via `sentence-transformers`) — smaller, CPU-friendly, and fast enough for repeated re-embedding as factory notes are added incrementally.

**Because**
> For a system that must stay responsive on standard hardware with no GPU (Op. Constraint 1), embedding model choice should optimize for inference speed per document over marginal retrieval-quality gains, since the knowledge base is small (factory notes, not a large corpus).
