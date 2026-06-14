"""
app.py — Flask webapp wrapping the 5 PDF utility scripts.
"""

import os
import sys
import uuid
import subprocess
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect,
    url_for, send_file, flash
)

app = Flask(__name__)
app.secret_key = "pdf-converter-secret"

BASE_DIR  = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_dirs():
    job_id  = uuid.uuid4().hex
    up_dir  = UPLOAD_DIR / job_id
    out_dir = OUTPUT_DIR / job_id
    up_dir.mkdir(parents=True)
    out_dir.mkdir(parents=True)
    return job_id, up_dir, out_dir


def save_uploads(files, dest: Path) -> list[Path]:
    saved = []
    for f in files:
        if f and f.filename:
            p = dest / f.filename
            f.save(p)
            saved.append(p)
    return saved


def run_script(script: str, args: list) -> tuple[str, str]:
    cmd = [sys.executable, str(BASE_DIR / script)] + [str(a) for a in args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr


def collect_outputs(out_dir: Path) -> list[Path]:
    return sorted(out_dir.rglob("*") if out_dir.exists() else [])


def output_links(out_dir: Path, job_id: str) -> list[dict]:
    links = []
    for p in collect_outputs(out_dir):
        if p.is_file():
            rel = p.relative_to(OUTPUT_DIR)
            links.append({"name": p.name, "path": str(rel).replace("\\", "/")})
    return links


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# -- Extractor -----------------------------------------------------------------

@app.route("/extractor", methods=["GET", "POST"])
def extractor():
    if request.method == "GET":
        return render_template("extractor.html")

    files = request.files.getlist("pdfs")
    if not files or not files[0].filename:
        flash("Please upload at least one PDF.")
        return redirect(url_for("extractor"))

    job_id, up_dir, out_dir = make_dirs()
    saved = save_uploads(files, up_dir)

    mode         = request.form.get("mode", "both")
    text_format  = request.form.get("text_format", "txt")
    table_format = request.form.get("table_format", "xlsx")

    input_arg = str(saved[0]) if len(saved) == 1 else str(up_dir)
    stdout, stderr = run_script("pdf_extractor.py", [
        "--input", input_arg,
        "--output-dir", str(out_dir),
        "--mode", mode,
        "--text-format", text_format,
        "--table-format", table_format,
    ])

    return render_template("extractor.html",
                           stdout=stdout, stderr=stderr,
                           links=output_links(out_dir, job_id))


# -- Inventory -----------------------------------------------------------------

@app.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.method == "GET":
        return render_template("inventory.html")

    files = request.files.getlist("pdfs")
    if not files or not files[0].filename:
        flash("Please upload at least one PDF.")
        return redirect(url_for("inventory"))

    job_id, up_dir, out_dir = make_dirs()
    save_uploads(files, up_dir)

    sample_pages = request.form.get("sample_pages", "3")
    recursive    = "--recursive" if request.form.get("recursive") else ""
    out_file     = out_dir / "pdf_inventory.xlsx"

    args = [
        "--input", str(up_dir),
        "--output", str(out_file),
        "--sample-pages", sample_pages,
    ]
    if recursive:
        args.append("--recursive")

    stdout, stderr = run_script("pdf_inventory.py", args)

    return render_template("inventory.html",
                           stdout=stdout, stderr=stderr,
                           links=output_links(out_dir, job_id))


# -- Marker --------------------------------------------------------------------

@app.route("/marker", methods=["GET", "POST"])
def marker():
    if request.method == "GET":
        return render_template("marker.html")

    files = request.files.getlist("pdfs")
    if not files or not files[0].filename:
        flash("Please upload at least one PDF.")
        return redirect(url_for("marker"))

    job_id, up_dir, out_dir = make_dirs()
    saved = save_uploads(files, up_dir)

    mode        = request.form.get("mode", "watermark")
    text        = request.form.get("text", "CONFIDENTIAL")
    position    = request.form.get("position", "center")
    angle       = request.form.get("angle", "45")
    opacity     = request.form.get("opacity", "0.12")
    font_size   = request.form.get("font_size", "48")
    color       = request.form.get("color", "#CCCCCC")
    page_num_fmt  = request.form.get("page_num_fmt", "Page {n} of {total}")
    page_num_size = request.form.get("page_num_size", "10")

    input_arg = str(saved[0]) if len(saved) == 1 else str(up_dir)
    args = [
        "--input", input_arg,
        "--output-dir", str(out_dir),
        "--mode", mode,
        "--text", text,
        "--position", position,
        "--angle", angle,
        "--opacity", opacity,
        "--font-size", font_size,
        "--color", color,
        "--page-num-fmt", page_num_fmt,
        "--page-num-size", page_num_size,
    ]

    stdout, stderr = run_script("pdf_marker.py", args)

    return render_template("marker.html",
                           stdout=stdout, stderr=stderr,
                           links=output_links(out_dir, job_id))


# -- Merge / Split -------------------------------------------------------------

@app.route("/merge-split", methods=["GET", "POST"])
def merge_split():
    if request.method == "GET":
        return render_template("merge_split.html")

    action = request.form.get("action", "merge")
    files  = request.files.getlist("pdfs")
    if not files or not files[0].filename:
        flash("Please upload at least one PDF.")
        return redirect(url_for("merge_split"))

    job_id, up_dir, out_dir = make_dirs()
    save_uploads(files, up_dir)

    if action == "merge":
        out_file = out_dir / "merged.pdf"
        args = ["merge", "--input", str(up_dir), "--output", str(out_file)]
    else:
        saved = list(up_dir.glob("*.pdf"))
        if not saved:
            flash("No PDF found.")
            return redirect(url_for("merge_split"))

        args = ["split", "--input", str(saved[0]), "--output-dir", str(out_dir)]
        every    = request.form.get("every", "").strip()
        ranges   = request.form.get("ranges", "").strip()
        on_pages = request.form.get("on_pages", "").strip()

        if every:
            args += ["--every", every]
        elif ranges:
            args += ["--ranges", ranges]
        elif on_pages:
            args += ["--on-pages"] + on_pages.split()

    stdout, stderr = run_script("pdf_merge_split.py", args)

    return render_template("merge_split.html",
                           stdout=stdout, stderr=stderr,
                           links=output_links(out_dir, job_id))


# -- Redactor ------------------------------------------------------------------

@app.route("/redactor", methods=["GET", "POST"])
def redactor():
    if request.method == "GET":
        return render_template("redactor.html")

    files = request.files.getlist("pdfs")
    if not files or not files[0].filename:
        flash("Please upload at least one PDF.")
        return redirect(url_for("redactor"))

    job_id, up_dir, out_dir = make_dirs()
    saved = save_uploads(files, up_dir)

    patterns   = request.form.get("patterns", "").strip().split()
    categories = request.form.getlist("categories")
    whole_word = request.form.get("whole_word")

    input_arg = str(saved[0]) if len(saved) == 1 else str(up_dir)
    args = ["--input", input_arg, "--output-dir", str(out_dir)]

    if patterns:
        args += ["--patterns"] + patterns
    if categories:
        args += ["--categories"] + categories
    if whole_word:
        args.append("--whole-word")

    stdout, stderr = run_script("pdf_redactor.py", args)

    return render_template("redactor.html",
                           stdout=stdout, stderr=stderr,
                           links=output_links(out_dir, job_id))


# -- Download ------------------------------------------------------------------

@app.route("/download/<path:filepath>")
def download(filepath):
    full_path = OUTPUT_DIR / filepath
    if not full_path.exists():
        flash("File not found.")
        return redirect(url_for("index"))
    return send_file(full_path, as_attachment=True)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
