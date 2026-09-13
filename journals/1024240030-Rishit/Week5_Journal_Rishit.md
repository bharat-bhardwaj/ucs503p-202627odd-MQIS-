# MQIS Project Journal — Rishit (Database/Analytics Track)

## Week 5 : Wiring Detection Output into DB Logging — Field Mismatch at the Integration Boundary

### Error:
```
TypeError: log() got an unexpected keyword argument 'label'
```

### Relevant Context
This week's task was to wire the detection module's output into `database.py`'s `log()` function — the first real integration point between Bharat's module and the DB layer. The detection module returned results shaped like:
```python
{
    "label": "scratch",
    "conf": 0.87,
    "sev": 0.4,
    "bbox": [x, y, w, h]
}
```
while `log()` (from Week 1) was defined expecting:
```python
def log(line_id, defect_type, severity, confidence, is_reject, timestamp=None):
    ...
```
Calling `log(line_id=..., **detection_result)` failed immediately since none of the key names matched.

### Key Observation
This is exactly the interface mismatch the proposal flags as a risk (Section 12: "three independently developed modules may have interface mismatches"), and the mitigation calls for a data-contract fixed by Week 3 — which slipped, since the schema was defined solo in Week 1 without checking the detection module's actual output shape.

### Solution
Rather than patching field names inline at the call site (which just relocates the mismatch), added a small adapter function as the single translation point between the two modules:
```python
def from_detection_result(result, line_id):
    return {
        "line_id": line_id,
        "defect_type": result.get("label"),
        "severity": result.get("sev"),
        "confidence": result.get("conf"),
        "is_reject": 1 if result.get("label") else 0,
    }

def log_detection(result, line_id):
    log(**from_detection_result(result, line_id))
```
Also wrote down the agreed field names (`label`, `conf`, `sev`, `bbox`) in a shared `CONTRACT.md` so both sides can catch drift before Week 6's milestone integration.

**Because**
An adapter function isolates schema drift to one place — if the detection module's output format changes again before the Week 11 full-integration milestone, only `from_detection_result()` needs updating, not every call site across the codebase.
