# Week 1 : Virtual Environment Not Resolving Correctly

## Error

zsh: command not found: streamlit

and later,

/Library/Frameworks/Python.framework/Versions/3.13/bin/python3: No module named streamlit


## Relevant Context
The project uses a virtual environment named `manufacturing_detection.venv`
(Python 3.9.6). Streamlit was confirmed installed inside this venv via
`pip install streamlit ...`, and a check inside a Jupyter notebook confirmed
the package existed at:

/Users/bharatbhardwaj/Desktop/sem 5/manufacturing_detection/manufacturing_detection.venv/lib/python3.9/site-packages

However, running `streamlit run app.py` or `python -m streamlit run app.py`
directly in the terminal failed, even with the venv apparently activated.

## Key Observation
Two separate issues were compounding:
1. The shell's `python`/`python3` commands were resolving to the **system**
   Python (`/Library/Frameworks/Python.framework/Versions/3.13/bin/python3`)
   rather than the venv's Python, because the venv's `bin` directory wasn't
   correctly prioritized on `PATH`.
2. The venv itself had been created inside a folder previously named
   `sem 4`, and later renamed to `sem 5`. Since a venv's `activate` script
   hardcodes the absolute path at creation time, `VIRTUAL_ENV` still pointed
   to the old, non-existent `sem 4` path — silently breaking PATH resolution
   even after activation.

## Solution
Recreated the virtual environment fresh, inside the correct (`sem 5`) path,
so all internal path references were generated correctly:
```bash
deactivate
rm -rf manufacturing_detection.venv
python3 -m venv manufacturing_detection.venv
source manufacturing_detection.venv/bin/activate
pip install streamlit opencv-python pandas Pillow chromadb sentence-transformers ollama
```
Verified resolution with:
```bash
which python
which streamlit
```
Both correctly pointed inside `sem 5/manufacturing_detection/manufacturing_detection.venv/bin/`,
after which the standard command worked as expected:
```bash
streamlit run app.py
```

**Because:** a Python venv's `activate` script embeds an absolute
`VIRTUAL_ENV` path at creation time. Moving or renaming the parent folder
after creation does not update this path, so the safest fix is recreating
the venv in its final location rather than manually patching internal files.


