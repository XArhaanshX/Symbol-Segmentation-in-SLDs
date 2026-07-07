# Pipeline Error Report

**Timestamp**: 2026-07-07 12:20:25  
**Stage**: chamfer_matching  
**Error Type**: `FileNotFoundError`

## What Happened

[Errno 2] No such file or directory: 'c:\\Users\\arhaa\\OneDrive\\Symbol Segmentor\\config\\chamfer.yaml'

## Possible Cause

A required file or directory is missing.

## Suggested Fix

Ensure the dataset is in place under `data/raw/` and run `python install.py` to regenerate directories.

## Technical Details

```
Traceback (most recent call last):
  File "C:\Users\arhaa\OneDrive\Symbol Segmentor\run.py", line 182, in main
    stage.run(context)
    ~~~~~~~~~^^^^^^^^^
  File "C:\Users\arhaa\OneDrive\Symbol Segmentor\src\stages\s03_chamfer_matching.py", line 35, in run
    import src.template_matching.chamfer_matching as cm
  File "C:\Users\arhaa\OneDrive\Symbol Segmentor\src\template_matching\chamfer_matching.py", line 31, in <module>
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'c:\\Users\\arhaa\\OneDrive\\Symbol Segmentor\\config\\chamfer.yaml'
```
