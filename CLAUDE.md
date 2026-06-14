# PDF Converter — Project Guide

## What this is
A Flask webapp wrapping 5 PDF utility scripts. Users upload PDFs via the browser, configure options, and download processed outputs.

## Stack
- Backend: Flask (Python)
- Frontend: Bootstrap 5 (CDN), vanilla JS
- PDF scripts: pdf_extractor.py, pdf_inventory.py, pdf_marker.py, pdf_merge_split.py, pdf_redactor.py

## Running locally
```powershell
.venv\Scripts\Activate.ps1
python app.py
```
App runs on http://localhost:5000

## Project structure
```
pdf_converter/
├── app.py                  # Flask routes + subprocess wrappers
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── extractor.html
│   ├── inventory.html
│   ├── marker.html
│   ├── merge_split.html
│   └── redactor.html
├── static/app.js           # Spinner + conditional field logic
├── uploads/                # Temp uploaded files (not committed)
├── outputs/                # Script output files (not committed)
└── (pdf_*.py scripts)
```

## Key conventions
- Scripts are invoked via `subprocess.run` — keeps them CLI-independent
- Uploads go to `./uploads/<uuid>/`, outputs to `./outputs/<uuid>/`
- Routes follow `/extractor`, `/inventory`, `/marker`, `/merge-split`, `/redactor`
- GET renders the form; POST runs the script and shows download links on the same page
- `pip install` requires `--trusted-host pypi.org --trusted-host files.pythonhosted.org` on this network (SSL cert issue)
