# MQIS Project Journal — Asmita (RAG/Reporting Track)

## Week 2 : Ollama Local Model Not Responding on First Call

### Error:
```
Error: could not connect to ollama server, run 'ollama serve' to start it
```

### Relevant Context
Following the plan to set up Llama 3.2 locally via Ollama and test a basic chat call:
```python
import ollama
response = ollama.chat(model='llama3.2', messages=[
    {'role': 'user', 'content': 'Summarize: Line 1 rejected 12 parts today.'}
])
```
This failed immediately, even though `ollama pull llama3.2` had completed successfully.

### Key Observation
`ollama pull` only downloads the model weights — it does not start the background server process. The Python client (`ollama` package) expects the daemon to already be running on `localhost:11434`.

### Solution
Start the daemon explicitly (or as a background service) before any client calls:
```bash
ollama serve &
```
Then the same `ollama.chat()` call succeeds.

**Because**
The `ollama` Python library is a thin client — it does not manage the model server's lifecycle. Any script relying on it (including the eventual `generate_report()` function planned for Week 8) needs the daemon confirmed alive first, ideally with a startup check rather than assuming it's already running.
