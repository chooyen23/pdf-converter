# PDF Tools

A Flask web app wrapping 5 PDF utility scripts — extract text & tables, generate metadata inventory, add watermarks/stamps, merge or split files, and redact sensitive data. Upload PDFs via browser and download results. All scripts are also fully usable as standalone CLI tools.

---

## Quick Start (Web App)

```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate        # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open `http://localhost:5000` in your browser.

---

## Sharing with Others (ngrok)

To share your local instance publicly without deploying:

```powershell
ngrok http 5000
```

ngrok will give you a public URL (e.g. `https://abc123.ngrok-free.app`) that anyone can access while your server is running.

---

## Scripts

| Script | What it does |
|---|---|
| `pdf_extractor.py` | Extract text and tables from PDFs into TXT, Markdown, CSV, or Excel |
| `pdf_inventory.py` | Scan a folder of PDFs and export a metadata inventory to Excel |
| `pdf_marker.py` | Add watermarks, stamps, or page numbers to PDFs in batch |
| `pdf_merge_split.py` | Merge multiple PDFs into one, or split a PDF by page range or chunk size |
| `pdf_redactor.py` | Permanently redact text matching patterns or built-in categories |

---

## CLI Usage

All scripts can be run directly without the web app.

### pdf_extractor.py

```bash
python pdf_extractor.py --input report.pdf
python pdf_extractor.py --input report.pdf --mode tables --table-format csv
python pdf_extractor.py --input ./pdfs --mode both --text-format md --output-dir ./extracted
```

`--mode`: `text` | `tables` | `both`  
`--text-format`: `txt` | `md`  
`--table-format`: `csv` | `xlsx`

---

### pdf_inventory.py

```bash
python pdf_inventory.py --input ./documents
python pdf_inventory.py --input ./documents --output my_inventory.xlsx --sample-pages 5
python pdf_inventory.py --input ./archive --recursive
```

Output: Excel file with two sheets — per-file metadata and a summary. Scanned PDFs highlighted yellow, encrypted PDFs in red.

---

### pdf_marker.py

```bash
python pdf_marker.py --input report.pdf --text "CONFIDENTIAL"
python pdf_marker.py --input report.pdf --mode stamp --text "APPROVED" --position top-center --angle 0
python pdf_marker.py --input report.pdf --mode page-numbers --position bottom-center
```

`--mode`: `watermark` | `stamp` | `page-numbers`  
`--position`: `center`, `top-left`, `top-center`, `top-right`, `bottom-left`, `bottom-center`, `bottom-right`

---

### pdf_merge_split.py

```bash
# Merge
python pdf_merge_split.py merge --input ./reports --output merged.pdf

# Split every N pages
python pdf_merge_split.py split --input large.pdf --output-dir ./splits --every 10

# Split by page ranges
python pdf_merge_split.py split --input report.pdf --output-dir ./splits --ranges "1-5,6-20,21-"

# Split before specific pages
python pdf_merge_split.py split --input report.pdf --output-dir ./splits --on-pages 10 25 40
```

---

### pdf_redactor.py

```bash
python pdf_redactor.py --input document.pdf --categories email phone
python pdf_redactor.py --input document.pdf --patterns "John Smith" "ACC-\d{6}"
python pdf_redactor.py --input ./pdfs --categories email ssn --patterns "Project X"
```

`--categories`: `email`, `phone`, `ssn`, `credit`, `postcode`, `date`

Output: `{filename}_redacted.pdf` per file and a `_redaction_log.csv` listing every match removed.

⚠️ Always verify output before distributing. Test on a copy first.

---

## Dependencies

```
flask, pypdf, pdfplumber, pymupdf, reportlab, pandas, openpyxl
```

Install all:
```bash
pip install -r requirements.txt
```

---

## Project Structure

```
pdf_converter/
├── app.py                  # Flask routes
├── templates/              # HTML templates (Bootstrap 5)
├── static/app.js           # Spinner + conditional field logic
├── uploads/                # Temp uploads (not committed)
├── outputs/                # Script outputs (not committed)
├── pdf_extractor.py
├── pdf_inventory.py
├── pdf_marker.py
├── pdf_merge_split.py
├── pdf_redactor.py
└── requirements.txt
```
