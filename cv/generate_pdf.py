#!/usr/bin/env python3
"""
LaTeX CV → PDF generator for Career Ops Reiterated.

Selects the correct CV template based on job language:
  - German JD  OR  German mandatory in skills  →  cv/GermanCVtemplate.tex
  - English JD with German optional/nice-to-have  →  cv/EnglishCVtemplate.tex

Each tailored build gets its own folder under output/:

    output/{company-slug}-{role-slug}/
    ├── cv-{slug}.tex          tailored LaTeX source
    ├── cv-{slug}.pdf          final PDF
    ├── cv-{slug}.aux          │
    ├── cv-{slug}.log          │  LaTeX build artefacts
    ├── cv-{slug}.out          │  (all isolated here)
    └── ...

Usage:
  # Auto-detect language from JD (most common — let the mode decide)
  python cv/generate_pdf.py --company Anthropic --role "AI Architect" --lang en
  python cv/generate_pdf.py --company Siemens   --role "Architect"    --lang de

  # With ATS keywords
  python cv/generate_pdf.py --company OpenAI --role "Staff Engineer" --lang en --keywords RAG LLMOps evals

  # Base build (no tailoring)
  python cv/generate_pdf.py --lang en

  # Compile a specific .tex file (bypasses template selection)
  python cv/generate_pdf.py --tex path/to/custom.tex

Requirements:
  - xelatex (recommended) or pdflatex / lualatex / tectonic
  - cv/EnglishCVtemplate.tex   (your English CV)
  - cv/GermanCVtemplate.tex    (your German CV)
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
CV_DIR  = ROOT / "cv"
OUT_DIR = ROOT / "output"

# Template files — gitignored (personal), must be created by the user
TEMPLATES = {
    "en": CV_DIR / "EnglishCVtemplate.tex",
    "de": CV_DIR / "GermanCVtemplate.tex",
}


# ---------------------------------------------------------------------------
# Engine detection
# ---------------------------------------------------------------------------

def detect_engine() -> str:
    for engine in ("xelatex", "pdflatex", "lualatex", "tectonic"):
        if shutil.which(engine):
            return engine
    return ""


# ---------------------------------------------------------------------------
# Template selection
# ---------------------------------------------------------------------------

def resolve_template(lang: str, explicit_tex: str | None) -> Path:
    """
    Return the base .tex file to use.
    - If --tex is given explicitly, use that directly.
    - Otherwise pick the template for the given lang (en/de).
    """
    if explicit_tex:
        p = Path(explicit_tex)
        if not p.exists():
            print(f"ERROR: Specified --tex not found: {p}")
            sys.exit(1)
        return p

    lang = lang.lower().strip()
    if lang not in TEMPLATES:
        print(f"ERROR: Unknown --lang '{lang}'. Use 'en' or 'de'.")
        sys.exit(1)

    template = TEMPLATES[lang]
    if not template.exists():
        other = "de" if lang == "en" else "en"
        print(f"ERROR: Template not found: {template}")
        print(f"  Expected your {lang.upper()} CV at: {template}")
        print(f"  Copy cv/template.tex to {template.name} and fill in your content.")
        # Fallback: try the other language template rather than crashing
        fallback = TEMPLATES[other]
        if fallback.exists():
            print(f"  Falling back to {fallback.name} — consider creating the {lang.upper()} template.")
            return fallback
        sys.exit(1)

    return template


# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------

def compile_latex(tex_file: Path, build_dir: Path, engine: str) -> Path:
    """
    Compile *tex_file* into *build_dir*.
    All auxiliary files (.aux, .log, .out, …) land in *build_dir* alongside
    the PDF — nothing bleeds into the repo root or cv/ directory.
    Returns the path to the generated PDF.
    """
    build_dir.mkdir(parents=True, exist_ok=True)

    if engine == "tectonic":
        cmd  = ["tectonic", "-o", str(build_dir), str(tex_file)]
        runs = 1
    else:
        cmd = [
            engine,
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={build_dir}",
            str(tex_file),
        ]
        runs = 2  # second run resolves cross-references

    for i in range(runs):
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=tex_file.parent)
        if result.returncode != 0:
            print(f"\n[LaTeX ERROR — run {i+1}/{runs}]")
            for line in result.stdout.splitlines()[-40:]:
                print(line)
            if result.stderr:
                print(result.stderr[-500:])
            sys.exit(1)

    pdf_name = tex_file.stem + ".pdf"
    pdf_path = build_dir / pdf_name
    if not pdf_path.exists():
        local_pdf = tex_file.parent / pdf_name
        if local_pdf.exists():
            shutil.move(str(local_pdf), str(pdf_path))
        else:
            print(f"PDF not found at expected path: {pdf_path}")
            sys.exit(1)

    return pdf_path


# ---------------------------------------------------------------------------
# Tailored build: copy template into the application folder, inject metadata
# ---------------------------------------------------------------------------

def make_tailored_copy(
    base_tex: Path,
    build_dir: Path,
    slug: str,
    company: str,
    role: str,
    keywords: list[str] | None = None,
) -> Path:
    """
    Create a tailored copy of the LaTeX CV inside *build_dir* with
    job-specific \\renewcommand overrides injected after \\begin{document}.

    The base template should contain:
        \\providecommand{\\TargetCompany}{General Application}
        \\providecommand{\\TargetRole}{Your Target Role}
        \\providecommand{\\JobKeywords}{}

    These are safely overridden without modifying the original template.
    """
    src = base_tex.read_text(encoding="utf-8")

    overrides = (
        f"\\renewcommand{{\\TargetCompany}}{{{_tex_escape(company)}}}\n"
        f"\\renewcommand{{\\TargetRole}}{{{_tex_escape(role)}}}\n"
    )
    if keywords:
        overrides += (
            f"\\renewcommand{{\\JobKeywords}}"
            f"{{{_tex_escape(', '.join(keywords))}}}\n"
        )

    if "\\begin{document}" in src:
        src = src.replace("\\begin{document}", "\\begin{document}\n" + overrides, 1)
    else:
        src = overrides + src

    tailored = build_dir / f"cv-{slug}.tex"
    tailored.write_text(src, encoding="utf-8")
    return tailored


def _tex_escape(text: str) -> str:
    chars = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(chars.get(c, c) for c in text)


def _make_slug(company: str, role: str) -> str:
    raw = f"{company}-{role[:40]}"
    raw = raw.lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9-]", "", raw)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Compile LaTeX CV to PDF")
    parser.add_argument("--tex",      help="Path to a specific .tex file (bypasses template selection)")
    parser.add_argument("--lang",     choices=["en", "de"], default="en",
                        help="CV language: 'en' = EnglishCVtemplate.tex, 'de' = GermanCVtemplate.tex (default: en)")
    parser.add_argument("--company",  help="Target company name (for tailored build)")
    parser.add_argument("--role",     help="Target role title (for tailored build)")
    parser.add_argument("--keywords", nargs="*", help="ATS keywords to inject")
    args = parser.parse_args()

    engine = detect_engine()
    if not engine:
        print("ERROR: No LaTeX engine found.")
        print("Install with:  sudo apt install texlive-xetex")
        print("Or tectonic:   https://tectonic-typesetting.github.io")
        sys.exit(1)
    print(f"Engine:   {engine}")
    print(f"Language: {args.lang.upper()} → {TEMPLATES.get(args.lang, 'custom').name if not args.tex else args.tex}")

    base_tex = resolve_template(args.lang, args.tex)

    # ── Tailored build ──────────────────────────────────────────────────────
    if args.company or args.role:
        company   = args.company or "Company"
        role      = args.role    or "Role"
        slug      = _make_slug(company, role)
        build_dir = OUT_DIR / slug

        print(f"Building:  {company} — {role}")
        print(f"Folder:    output/{slug}/")

        tex_file = make_tailored_copy(
            base_tex, build_dir, slug, company, role, args.keywords
        )
        pdf_path = compile_latex(tex_file, build_dir, engine)

    # ── Base build ──────────────────────────────────────────────────────────
    else:
        build_dir = OUT_DIR / f"base-{args.lang}"
        print(f"Building base CV ({args.lang.upper()}, no tailoring)")
        print(f"Folder:    output/base-{args.lang}/")
        pdf_path = compile_latex(base_tex, build_dir, engine)

    print(f"\n✅  PDF ready:  {pdf_path.resolve()}")
    print(f"📁  Folder:     {build_dir.resolve()}/")


if __name__ == "__main__":
    main()
