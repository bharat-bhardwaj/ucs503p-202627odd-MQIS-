# MQIS Project Journal — Asmita (RAG/Reporting Track)

## Week 4 : Embedding Pipeline — Inconsistent Vector Dimensions on Rebuild

### Error:
```
chromadb.errors.InvalidDimensionException: Embedding dimension 384 does not match collection dimensionality 768
```

### Relevant Context
While implementing the embedding pipeline for the knowledge base (feeding into Chroma collection build in Week 5), the Chroma collection had been created earlier in testing using a placeholder embedding function, then the actual pipeline switched models mid-week (see Week 1 decision) without recreating the collection.

### Key Observation
Chroma collections are bound to a fixed embedding dimensionality set at creation time. Swapping the embedding model (`all-mpnet-base-v2` → `all-MiniLM-L6-v2`, 768-dim vs 384-dim) after a collection already exists silently produces this mismatch on the next `add()` call rather than failing at model-selection time.

### Solution
Delete and recreate the collection whenever the embedding model changes, and pin the model name in a config constant referenced by both the ingestion script and any later query script, so this can't drift again:
```python
client.delete_collection("factory_kb")
collection = client.create_collection(
    name="factory_kb",
    embedding_function=minilm_ef  # single source of truth
)
```

**Because**
The mismatch isn't a bug in Chroma — it's a consistency requirement between whatever function embedded the stored vectors and whatever function embeds the query vector at retrieval time. Since Week 1's decision and Week 4's implementation were separated by a few days, nothing enforced that the same model choice carried through; centralizing it in one config avoids this class of error recurring in Weeks 5–9.
