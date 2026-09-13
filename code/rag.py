import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import os

# Load embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Create vector DB
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name="factory_knowledge"
)

# Build knowledge base
def build_knowledge_base():
    knowledge_dir = "knowledge"
    all_ids = collection.get()["ids"]

    if len(all_ids) > 0:
        return

    print("Building knowledge base...")

    for fname in os.listdir(knowledge_dir):
        if not fname.endswith(".txt"):
            continue

        with open(f"{knowledge_dir}/{fname}", "r") as f:
            text = f.read()

        chunks = [
            p.strip()
            for p in text.split("\n\n")
            if len(p.strip()) > 30
        ]

        for i, chunk in enumerate(chunks):
            embedding = embedder.encode(chunk).tolist()
            doc_id = f"{fname}_{i}"

            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[doc_id]
            )

    print("Knowledge base ready.")

# Retrieve relevant knowledge
def retrieve(query, n_results=4):
    embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    return results["documents"][0]

# Generate full report
def generate_report(summary):
    if not summary:
        return "No production data recorded yet today."

    defect_types = [
        k for k in summary["by_type"].keys()
        if k != "none"
    ]

    if not defect_types:
        query = "metal nut quality inspection all clear"
    else:
        query = (
            f"causes maintenance recommendations for "
            f"{' '.join(defect_types)} defects in metal nuts"
        )

    retrieved = retrieve(query)
    knowledge_text = "\n\n".join(retrieved)

    line_text = "\n".join([
        f"{l['line_id']}: {l['inspected']} inspected, "
        f"{l['rejected']} rejected ({l['rejection_rate']}%) — {l['status']}"
        for l in summary["by_line"]
    ])

    defect_text = "\n".join([
        f"{k}: {v} occurrences"
        for k, v in summary["by_type"].items()
        if k != "none"
    ]) or "No defects found"

    prompt = f"""You are a manufacturing quality control AI.

Production data:
Total inspected: {summary['total_inspected']}
Rejected: {summary['total_rejected']}
Rejection rate: {summary['overall_rejection_rate']}%

Line status:
{line_text}

Defects:
{defect_text}

Factory knowledge:
{knowledge_text}

Write a clear report explaining:
- current status
- causes
- actions required
"""

    response = ollama.chat(
        model='llama3.2',
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']['content']

# Answer specific question
def answer_question(question, summary):
    if not summary:
        return "No production data yet."

    retrieved = retrieve(question)
    knowledge_text = "\n\n".join(retrieved)

    summary_text = (
        f"Total inspected: {summary['total_inspected']}\n"
        f"Total rejected: {summary['total_rejected']}\n"
        f"Rejection rate: {summary['overall_rejection_rate']}%\n"
        f"Defects: {summary['by_type']}"
    )

    prompt = f"""
You are a manufacturing quality control AI.

{summary_text}

Knowledge:
{knowledge_text}

Question: {question}
"""

    response = ollama.chat(
        model='llama3.2',
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']['content']