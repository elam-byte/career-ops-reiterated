#!/usr/bin/env python3
"""
Migrate data/applications.md (markdown table) → data/applications.jsonl
and data/scan-history.tsv → data/scan-history.jsonl

Safe to run multiple times — will not duplicate records.

Usage:
  python scripts/migrate_to_jsonl.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


# ---------------------------------------------------------------------------
# Applications: MD table → JSONL
# ---------------------------------------------------------------------------

def migrate_applications():
    md_file   = DATA_DIR / "applications.md"
    jsonl_file = DATA_DIR / "applications.jsonl"

    if not md_file.exists():
        print(f"  [skip] {md_file} not found")
        return

    # Load existing JSONL ids to avoid duplicates
    existing_ids: set[str] = set()
    if jsonl_file.exists():
        with open(jsonl_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        existing_ids.add(str(json.loads(line).get("id", "")))
                    except json.JSONDecodeError:
                        pass

    new_records = []
    with open(md_file) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|") or line.startswith("| #") or line.startswith("|---"):
                continue
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) < 8:
                continue
            try:
                num      = cols[0]
                date     = cols[1]
                company  = cols[2]
                role     = cols[3]
                score_r  = cols[4]
                status   = cols[5]
                pdf_r    = cols[6]
                report_r = cols[7]
                notes    = cols[8] if len(cols) > 8 else ""

                app_id = num.zfill(3) if re.match(r"^\d+$", num) else num

                if app_id in existing_ids:
                    continue

                score_m = re.search(r"([\d.]+)", score_r)
                score   = float(score_m.group(1)) if score_m else None

                report_m = re.search(r"\[.*?\]\((.*?)\)", report_r)
                report   = report_m.group(1) if report_m else report_r.strip()

                record = {
                    "id":             app_id,
                    "date":           date,
                    "company":        company,
                    "role":           role,
                    "url":            "",
                    "score":          score,
                    "status":         _normalize_status(status),
                    "archetype":      "",
                    "pdf":            "✅" in pdf_r,
                    "report":         report,
                    "notes":          notes,
                    "comp_suggestion": "",
                    "added_at":       f"{date}T00:00:00",
                }
                new_records.append(record)
                existing_ids.add(app_id)

            except (ValueError, IndexError) as e:
                print(f"  [warn] skipping row: {e}")
                continue

    if new_records:
        with open(jsonl_file, "a") as f:
            for rec in new_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"  ✅ applications.md → {len(new_records)} record(s) added to applications.jsonl")
    else:
        print("  ✅ applications.jsonl already up to date (no new records)")


# ---------------------------------------------------------------------------
# Scan history: TSV → JSONL
# ---------------------------------------------------------------------------

def migrate_scan_history():
    tsv_file   = DATA_DIR / "scan-history.tsv"
    jsonl_file = DATA_DIR / "scan-history.jsonl"

    if not tsv_file.exists():
        print(f"  [skip] {tsv_file} not found")
        return

    existing_urls: set[str] = set()
    if jsonl_file.exists():
        with open(jsonl_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        existing_urls.add(json.loads(line).get("url", ""))
                    except json.JSONDecodeError:
                        pass

    import csv
    new_records = []
    with open(tsv_file) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            url = row.get("url", "").strip()
            if not url or url in existing_urls:
                continue
            new_records.append(dict(row))
            existing_urls.add(url)

    if new_records:
        with open(jsonl_file, "a") as f:
            for rec in new_records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"  ✅ scan-history.tsv → {len(new_records)} record(s) added to scan-history.jsonl")
    else:
        print("  ✅ scan-history.jsonl already up to date")


# ---------------------------------------------------------------------------
# Status normalisation
# ---------------------------------------------------------------------------

def _normalize_status(raw: str) -> str:
    m = {
        "evaluada": "Evaluated", "evaluated": "Evaluated",
        "aplicado": "Applied",   "applied": "Applied",
        "respondido": "Responded", "responded": "Responded",
        "entrevista": "Interview", "interview": "Interview",
        "oferta": "Offer",       "offer": "Offer",
        "rechazada": "Rejected", "rejected": "Rejected",
        "descartada": "Discarded", "discarded": "Discarded",
        "no aplicar": "SKIP",    "skip": "SKIP",
    }
    return m.get(raw.lower().strip(), raw)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Career Ops — Data Migration")
    print(f"Root: {ROOT}")
    print()
    print("Migrating applications.md …")
    migrate_applications()
    print()
    print("Migrating scan-history.tsv …")
    migrate_scan_history()
    print()
    print("Done. Run the dashboard: cd dashboard && streamlit run app.py")
