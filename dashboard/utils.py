"""Shared data utilities for Career Ops dashboard."""

import json
import re
import yaml
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
APPLICATIONS_FILE = DATA_DIR / "applications.jsonl"
SCAN_HISTORY_FILE = DATA_DIR / "scan-history.jsonl"
PIPELINE_FILE = DATA_DIR / "pipeline.md"
REPORTS_DIR = ROOT / "reports"

STATUSES = [
    "Evaluated", "Applied", "Responded", "Interview",
    "Offer", "Rejected", "Discarded", "SKIP"
]

STATUS_COLORS = {
    "Evaluated": "#74c7ec",
    "Applied":   "#89dceb",
    "Responded": "#cba6f7",
    "Interview": "#fab387",
    "Offer":     "#a6e3a1",
    "Rejected":  "#f38ba8",
    "Discarded": "#9399b2",
    "SKIP":      "#6c7086",
}

ARCHETYPES = [
    "AI Architect",
    "AI Platform / LLMOps",
    "Agentic / Automation",
    "Technical AI PM",
    "AI Solutions Architect",
    "AI Forward Deployed",
    "AI Transformation",
    "Engineering Manager",
    "Program Manager",
    "Other",
]


COUNTRY_LABELS = {
    "DE": "🇩🇪 Germany",
    "CH": "🇨🇭 Switzerland",
    "AT": "🇦🇹 Austria",
    "IT": "🇮🇹 Italy",
    "IN": "🇮🇳 India",
    "GB": "🇬🇧 United Kingdom",
    "US": "🇺🇸 United States",
    "FR": "🇫🇷 France",
    "REMOTE": "🌐 Remote",
}


# ---------------------------------------------------------------------------
# Profile / config
# ---------------------------------------------------------------------------

def load_profile() -> dict:
    profile_file = ROOT / "config" / "profile.yml"
    if profile_file.exists():
        with open(profile_file) as f:
            return yaml.safe_load(f) or {}
    return {}


def get_active_countries() -> list[str]:
    """Return the list of active country codes from profile.yml."""
    profile = load_profile()
    search = profile.get("search", {})
    countries = list(search.get("countries", ["DE"]))
    if search.get("include_remote", True) and "REMOTE" not in countries:
        countries.append("REMOTE")
    return countries


# ---------------------------------------------------------------------------
# JSONL read / write
# ---------------------------------------------------------------------------

def load_applications() -> list[dict]:
    """Load all applications from JSONL. Falls back to parsing applications.md."""
    if APPLICATIONS_FILE.exists():
        apps = []
        with open(APPLICATIONS_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        apps.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return apps
    # Fallback: parse markdown table
    return _parse_applications_md()


def save_applications(apps: list[dict]) -> None:
    """Rewrite the full JSONL file."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(APPLICATIONS_FILE, "w") as f:
        for app in apps:
            f.write(json.dumps(app, ensure_ascii=False) + "\n")


def add_application(app: dict) -> None:
    """Append a single application."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(APPLICATIONS_FILE, "a") as f:
        f.write(json.dumps(app, ensure_ascii=False) + "\n")


def update_application(app_id: str, updates: dict) -> None:
    """Update fields of an existing application by id."""
    apps = load_applications()
    for app in apps:
        if str(app.get("id")) == str(app_id):
            app.update(updates)
            break
    save_applications(apps)


def get_next_id(apps: list[dict]) -> str:
    """Return next zero-padded 3-digit sequential id."""
    if not apps:
        return "001"
    ids = [int(a.get("id", 0)) for a in apps if str(a.get("id", "")).isdigit()]
    return f"{(max(ids) + 1):03d}" if ids else "001"


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def check_duplicate(
    url: str | None = None,
    company: str | None = None,
    role: str | None = None,
) -> dict:
    """
    Returns:
      { is_duplicate: bool, match_type: str, existing: dict | list | None,
        warning: str | None }
    """
    apps = load_applications()

    # 1. Exact URL match
    if url:
        for app in apps:
            if app.get("url") and app["url"].rstrip("/") == url.rstrip("/"):
                return {"is_duplicate": True, "match_type": "url", "existing": app}

    # 2. Company + role fuzzy match
    if company and role:
        for app in apps:
            c_sim = _similarity(company, app.get("company", ""))
            r_sim = _similarity(role, app.get("role", ""))
            if c_sim >= 0.85 and r_sim >= 0.75:
                return {"is_duplicate": True, "match_type": "company+role", "existing": app}

    # 3. Company-only warning (not a blocker, just informational)
    if company:
        matches = [
            app for app in apps
            if _similarity(company, app.get("company", "")) >= 0.88
        ]
        if matches:
            return {
                "is_duplicate": False,
                "match_type": "company_exists",
                "warning": f"You have {len(matches)} existing application(s) at {company}",
                "existing": matches,
            }

    return {"is_duplicate": False, "match_type": None, "existing": None}


# ---------------------------------------------------------------------------
# Pipeline (pending URLs)
# ---------------------------------------------------------------------------

def load_pipeline() -> list[dict]:
    jobs = []
    if not PIPELINE_FILE.exists():
        return jobs
    with open(PIPELINE_FILE) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("- [ ]"):
                jobs.append(_parse_pipeline_line(line[5:].strip(), "pending"))
            elif line.startswith("- [x]") or line.startswith("- [X]"):
                jobs.append(_parse_pipeline_line(line[5:].strip(), "done"))
            elif line.startswith("- [!]"):
                jobs.append(_parse_pipeline_line(line[5:].strip(), "error"))
    return jobs


def _parse_pipeline_line(content: str, status: str) -> dict:
    parts = [p.strip() for p in content.split("|")]
    job = {"status": status, "url": "", "company": "", "title": ""}
    if parts:
        job["url"] = parts[0]
    if len(parts) >= 2:
        job["company"] = parts[1]
    if len(parts) >= 3:
        job["title"] = parts[2]
    return job


# ---------------------------------------------------------------------------
# Scan history
# ---------------------------------------------------------------------------

def load_scan_history() -> list[dict]:
    # Try JSONL first
    if SCAN_HISTORY_FILE.exists():
        history = []
        with open(SCAN_HISTORY_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        history.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return history

    # Fallback: read TSV
    tsv = DATA_DIR / "scan-history.tsv"
    if tsv.exists():
        import csv
        rows = []
        with open(tsv) as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                rows.append(dict(row))
        return rows

    return []


# ---------------------------------------------------------------------------
# Markdown → JSONL migration helper
# ---------------------------------------------------------------------------

def _parse_applications_md() -> list[dict]:
    """Parse the markdown table in data/applications.md into dicts."""
    md_file = DATA_DIR / "applications.md"
    if not md_file.exists():
        return []

    apps = []
    with open(md_file) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|") or line.startswith("| #") or line.startswith("|---"):
                continue
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) < 8:
                continue
            try:
                # Columns: # | Date | Company | Role | Score | Status | PDF | Report | Notes
                num, date, company, role, score_raw, status, pdf_raw, report_raw = cols[:8]
                notes = cols[8] if len(cols) > 8 else ""

                score_match = re.search(r"([\d.]+)", score_raw)
                score = float(score_match.group(1)) if score_match else None

                report_match = re.search(r"\[.*?\]\((.*?)\)", report_raw)
                report = report_match.group(1) if report_match else report_raw

                apps.append({
                    "id": num.zfill(3) if num.isdigit() else num,
                    "date": date,
                    "company": company,
                    "role": role,
                    "url": "",
                    "score": score,
                    "status": _normalize_status(status),
                    "archetype": "",
                    "pdf": "✅" in pdf_raw,
                    "report": report,
                    "notes": notes,
                    "comp_suggestion": "",
                    "added_at": f"{date}T00:00:00",
                })
            except (ValueError, IndexError):
                continue
    return apps


def _normalize_status(raw: str) -> str:
    mapping = {
        "evaluada": "Evaluated",
        "evaluated": "Evaluated",
        "aplicado": "Applied",
        "applied": "Applied",
        "respondido": "Responded",
        "responded": "Responded",
        "entrevista": "Interview",
        "interview": "Interview",
        "oferta": "Offer",
        "offer": "Offer",
        "rechazada": "Rejected",
        "rejected": "Rejected",
        "descartada": "Discarded",
        "discarded": "Discarded",
        "no aplicar": "SKIP",
        "skip": "SKIP",
    }
    return mapping.get(raw.lower().strip(), raw)
