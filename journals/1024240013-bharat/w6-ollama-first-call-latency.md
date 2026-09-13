# Week 6 : Shift Report Generation Appearing to Hang

## Error
No exception — the Streamlit spinner ("Analyzing data and generating
report... takes 20-30 seconds") stayed active far longer than expected
on the very first report request after starting the app, occasionally
past a minute, making it look frozen during integration testing.

## Relevant Context
`rag.generate_report()` calls:
```python
response = ollama.chat(
    model='llama3.2',
    messages=[{"role": "user", "content": prompt}]
)
```
Subsequent report requests in the same session consistently returned in
the expected 20-30 second range, but the very first call after Ollama
itself had been freshly started was much slower.

## Key Observation
Ollama loads the full model weights into memory only on the first
inference call after the Ollama service starts (or after the model has
been idle long enough to be unloaded); this cold-start cost was being
misread as a bug in the report-generation pipeline, when it was actually
expected one-time model-loading latency outside the application's
control.

## Solution
Confirmed this by running a manual warm-up call directly against Ollama
immediately after starting it and before opening the dashboard:
```bash
ollama run llama3.2 "hello"
```
This forced the model to load once ahead of time. After that, every
report generated through the dashboard — including the first one in a
new Streamlit session — returned within the normal 20-30 second range.
Documented this as a required step in the run instructions rather than
treating it as an application bug.

**Because:** local LLM inference tools commonly pay a one-time cold-start
cost to load model weights into memory; distinguishing that from an
actual application performance bug avoids wasted debugging time and
sets correct expectations during a live demo.
