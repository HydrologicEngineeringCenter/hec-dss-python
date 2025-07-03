---
name: Bug Report / Feature Request
about: Bug Report / Feature Request
title: ''
labels: ''
assignees: ''

---

# Bug Report

**IMPORTANT**  
If your bug involves a specific DSS file, please ZIP it and attach the ZIP archive to your issue.

## Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. **Environment**  
   - Python version: e.g. `3.9.12`  
   - Package version: e.g. `hecdss==0.1.10`  
   - Operating System: e.g. Windows 10, macOS 12  
2. **Script**  
   ```python
   from hecdss import HecDss
   
   with HecDss.open("file") as dss:
        ts=dss.get("path")
3.**DSS file**
Attach DSS file.

Note: GitHub strips large binaries, so always ZIP before attaching.

Additional Context
Add any other context about the problem here (logs, screenshots, etc.).
