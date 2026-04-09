#!/usr/bin/env python3
"""
Cover letter → .docx generator for Career Ops Reiterated.

Reads candidate details from config/profile.yml and formats the
cover letter text into a professional Word document (.docx) that
opens in both LibreOffice and Microsoft Word.

Output folder mirrors the CV generator:
    output/{company-slug}-{role-slug}/
    └── coverletter-{slug}.docx

Usage:
  # Pass text directly
  python cv/generate_coverletter.py \\
      --company "Siemens" \\
      --role "Solutions Architect" \\
      --lang en \\
      --text "Dear Hiring Manager, ..."

  # Read text from stdin
  echo "Dear Hiring Manager, ..." | python cv/generate_coverletter.py \\
      --company "Siemens" \\
      --role "Solutions Architect" \\
      --lang en

Requirements:
  pip install python-docx pyyaml
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT    = Path(__file__).resolve().parent.parent
CV_DIR  = ROOT / "cv"
OUT_DIR = ROOT / "output"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_profile() -> dict:
    profile_file = ROOT / "config" / "profile.yml"
    if profile_file.exists():
        with open(profile_file) as f:
            return yaml.safe_load(f) or {}
    return {}


# ---------------------------------------------------------------------------
# Slug
# ---------------------------------------------------------------------------

def _make_slug(company: str, role: str) -> str:
    raw = f"{company}-{role[:40]}"
    raw = raw.lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9-]", "", raw)


# ---------------------------------------------------------------------------
# .docx generation
# ---------------------------------------------------------------------------

def generate_docx(
    text: str,
    company: str,
    role: str,
    lang: str,
    profile: dict,
) -> Path:
    try:
        from docx import Document
        from docx.shared import Pt, Cm, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        print("ERROR: python-docx not installed.")
        print("Install with:  pip install python-docx")
        sys.exit(1)

    candidate = profile.get("candidate", {})
    name      = candidate.get("full_name", "")
    email     = candidate.get("email", "")
    phone     = candidate.get("phone", "")
    location  = candidate.get("location", "")
    linkedin  = candidate.get("linkedin", "")

    doc = Document()

    # ── Page margins ──────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

    # ── Styles ────────────────────────────────────────────────────────────
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)

    BLUE = RGBColor(0, 87, 183)   # matches CV accent colour

    # ── Header: candidate info ─────────────────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(name.upper())
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = BLUE

    contact_line = "  |  ".join(filter(None, [location, phone, email, linkedin]))
    p2 = doc.add_paragraph(contact_line)
    p2.runs[0].font.size = Pt(9)
    p2.runs[0].font.color.rgb = RGBColor(100, 100, 100)

    # Divider
    p3 = doc.add_paragraph()
    p3.paragraph_format.space_after = Pt(4)
    run3 = p3.add_run("─" * 80)
    run3.font.size = Pt(9)
    run3.font.color.rgb = BLUE

    # ── Date + recipient block ─────────────────────────────────────────────
    today = date.today().strftime("%d %B %Y") if lang == "en" else date.today().strftime("%d. %B %Y")
    doc.add_paragraph(today)

    if lang == "de":
        subj = doc.add_paragraph()
        subj_run = subj.add_run(f"Bewerbung als {role}")
        subj_run.bold = True
        subj_run.font.size = Pt(11)
        subj.paragraph_format.space_before = Pt(8)

    doc.add_paragraph()  # spacer

    # ── Body: split text into paragraphs on blank lines ───────────────────
    paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    for i, para_text in enumerate(paragraphs):
        p = doc.add_paragraph(para_text)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.first_line_indent = Cm(0)
        # Justify all body paragraphs except the last (signature)
        if i < len(paragraphs) - 1:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # ── Save ──────────────────────────────────────────────────────────────
    slug      = _make_slug(company, role)
    build_dir = OUT_DIR / slug
    build_dir.mkdir(parents=True, exist_ok=True)

    out_path = build_dir / f"coverletter-{slug}.docx"
    doc.save(str(out_path))
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate cover letter .docx")
    parser.add_argument("--company", required=True, help="Target company name")
    parser.add_argument("--role",    required=True, help="Target role title")
    parser.add_argument("--lang",    choices=["en", "de"], default="en",
                        help="Letter language: en (default) or de")
    parser.add_argument("--text",    help="Cover letter text (or pipe via stdin)")
    args = parser.parse_args()

    # Get text from --text arg or stdin
    if args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("ERROR: Provide cover letter text via --text or stdin.")
        sys.exit(1)

    if not text.strip():
        print("ERROR: Cover letter text is empty.")
        sys.exit(1)

    profile  = load_profile()
    out_path = generate_docx(text, args.company, args.role, args.lang, profile)

    print(f"\n✅  Cover letter ready: {out_path.resolve()}")
    print(f"📁  Folder:             {out_path.parent.resolve()}/")
    print(f"📄  Open with:          libreoffice \"{out_path}\"")


if __name__ == "__main__":
    main()
