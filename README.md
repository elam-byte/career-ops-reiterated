# Career-Ops Reiterated

> A personalized fork of [career-ops](https://github.com/santifer/career-ops) — rebuilt with Python-first workflows, LaTeX-based CV generation, Streamlit and terminal dashboards, location-aware job scanning, and extended consistency checks.

![Claude Code](https://img.shields.io/badge/Claude_Code-000?style=flat&logo=anthropic&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LaTeX](https://img.shields.io/badge/LaTeX-008080?style=flat&logo=latex&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

---

**What this fork changes:**

| Area | Original | This Fork |
|------|----------|-----------|
| CV / PDF generation | HTML template → Playwright → PDF | LaTeX (`.tex`) → xelatex → PDF |
| Dashboard | Go + Bubble Tea TUI | Streamlit web UI + Rich terminal |
| Data storage | Markdown tables + TSV | JSONL (append-friendly, no SQL) |
| Compensation | Scored dimension (Block C) | Non-scored research block (Block D) |
| Job scanning | Germany only | Multi-country: DE, CH, AT, IT, IN, GB, US, FR, REMOTE |
| Modes language | Spanish | English |
| Duplicate detection | Basic | URL exact + company+role fuzzy match + company-exists warning |
| Consistency checks | Manual | Automated status normalization, ID integrity, dedup enforcement |

---

## What Is This

Career-ops-reiterated turns Claude Code into a full job search command center:

- **Evaluates offers** with a structured A-F scoring system (9 weighted dimensions)
- **Generates tailored PDFs** — ATS-optimized LaTeX CVs customized per job description
- **Scans portals** automatically (Greenhouse, Ashby, Lever, company pages)
- **Processes in batch** — evaluate 10+ offers in parallel with sub-agents
- **Tracks everything** in JSONL with duplicate detection and integrity checks
- **Location-aware scanning** — filter companies and queries by active country set

> **This is NOT a spray-and-pray tool.** It's a filter — it helps you find the few offers worth your time out of hundreds. The system strongly recommends against applying to anything scoring below 4.0/5. Always review before submitting.

---

## What's New in This Fork

### Python-First Stack

All tooling is Python — no Node.js, no Go. The dashboard runs with Streamlit (`cd dashboard && streamlit run app.py`) or as a Rich terminal UI (`python dashboard/terminal.py`).

### LaTeX CV Pipeline

CVs are generated from your own `.tex` source via xelatex:

```bash
python cv/generate_pdf.py --company "Anthropic" --role "AI Architect" --keywords RAG LLMOps
```

The generator auto-detects available LaTeX engines (xelatex → pdflatex → lualatex → tectonic), injects a `\TargetCompany` command for tailored builds, and outputs to `output/`.

### Location-Based Job Scanning

Configure which countries to scan in `config/profile.yml`:

```yaml
search:
  countries:
    - DE        # Germany (default — always on)
    # - CH      # Switzerland
    # - AT      # Austria
    # - IT      # Italy
    # - IN      # India
    # - GB      # United Kingdom
    # - US      # United States
    # - FR      # France
    # - REMOTE  # Fully-remote anywhere
  include_remote: true
```

Every company and search query in `portals.yml` is tagged with country codes. The scanner filters by active countries before running — so a DE-only session never touches IT or IN portals. You can also override per session: "Scan for jobs in India today."

### Consistency Checks & Duplicate Detection

Before adding any application:
1. **Exact URL match** — blocks exact duplicates
2. **Company + role fuzzy match** — blocks near-duplicates (>85% company + >75% role similarity)
3. **Company-exists warning** — informs you of existing applications at the same company

Status values are enforced against a canonical set: `Evaluated`, `Applied`, `Responded`, `Interview`, `Offer`, `Rejected`, `Discarded`, `SKIP`.

### JSONL Data Storage

All application data lives in `data/applications.jsonl` — one JSON record per line. Append-friendly, human-readable, no dependencies, handles 2000 records in under 200KB.

```json
{
  "id": "005",
  "date": "2026-04-09",
  "company": "Anthropic",
  "role": "Senior AI Architect",
  "url": "https://boards.greenhouse.io/anthropic/jobs/123",
  "score": 4.5,
  "status": "Evaluated",
  "archetype": "AI Architect",
  "cv_lang": "EN",
  "country": "US",
  "pdf": false,
  "report": "reports/005-anthropic-2026-04-09.md",
  "notes": "Strong RAG + distributed systems match",
  "comp_suggestion": "€130k–150k",
  "added_at": "2026-04-09T10:30:00"
}
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-username/career-ops-reiterated.git
cd career-ops-reiterated

# 2. Install Python dependencies
pip install -r dashboard/requirements.txt
npx playwright install chromium   # Required for portal scanning

# 3. Configure
cp config/profile.example.yml config/profile.yml  # Fill in your details
cp templates/portals.example.yml portals.yml       # Customize companies

# 4. Add your CV
cp your-cv.tex cv/cv.tex   # Or use cv/template.tex as a starting point

# 5. Open Claude Code
claude   # Ask Claude to adapt the system to your profile

# 6. Launch dashboard
cd dashboard && streamlit run app.py     # Web UI
python dashboard/terminal.py            # Terminal UI
```

See [docs/SETUP.md](docs/SETUP.md) for the full setup guide.

---

## Commands

```
/career-ops-reiterated                → Show all available commands
/career-ops-reiterated {paste a JD}   → Full auto-pipeline (evaluate + PDF + tracker)
/career-ops-reiterated scan           → Scan portals for new offers
/career-ops-reiterated pdf            → Generate ATS-optimized CV
/career-ops-reiterated batch          → Batch evaluate multiple offers
/career-ops-reiterated tracker        → View application status
/career-ops-reiterated apply          → Fill application forms with AI
/career-ops-reiterated pipeline       → Process pending URLs
/career-ops-reiterated contact       → LinkedIn outreach message
/career-ops-reiterated deep           → Deep company research
/career-ops-reiterated training       → Evaluate a course/cert
/career-ops-reiterated project        → Evaluate a portfolio project
```

---

## Project Structure

```
career-ops-reiterated/
├── CLAUDE.md                    # Agent instructions
├── cv.md                        # Your CV in markdown (optional)
├── cv/
│   ├── cv.tex                   # Your LaTeX CV (create this)
│   ├── template.tex             # Starter LaTeX template
│   └── generate_pdf.py          # LaTeX → PDF compiler
├── config/
│   └── profile.yml              # Your profile (name, targets, countries)
├── portals.yml                  # 60+ companies + search queries, country-tagged
├── modes/                       # 14 skill modes (all in English)
│   ├── _shared.md               # Shared scoring context
│   ├── _profile.md              # Your personal context layer
│   ├── evaluate.md              # Single offer evaluation
│   ├── scan.md                  # Portal scanner (country-aware)
│   ├── pdf.md                   # LaTeX PDF generation
│   ├── pipeline.md              # Batch URL processor
│   └── ...
├── dashboard/
│   ├── app.py                   # Streamlit web dashboard
│   ├── terminal.py              # Rich terminal dashboard
│   ├── utils.py                 # Shared data utilities
│   └── requirements.txt
├── data/                        # Tracking data (gitignored)
│   ├── applications.jsonl       # Application tracker
│   ├── pipeline.md              # Pending URLs inbox
│   └── scan-history.jsonl       # Scanner dedup history
├── reports/                     # Evaluation reports (gitignored)
├── output/                      # Generated PDFs (gitignored)
├── scripts/
│   └── migrate_to_jsonl.py      # One-time MD/TSV → JSONL migration
└── templates/
    ├── portals.example.yml      # Scanner config template
    └── states.yml               # Canonical status values
```

---

## Tech Stack

![Claude Code](https://img.shields.io/badge/Claude_Code-000?style=flat&logo=anthropic&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LaTeX](https://img.shields.io/badge/LaTeX-008080?style=flat&logo=latex&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)

- **Agent**: Claude Code with custom skills and modes
- **PDF**: LaTeX (xelatex) from `.tex` source
- **Scanner**: Playwright + Greenhouse API + WebSearch, filtered by country
- **Dashboard**: Streamlit (web) + Rich (terminal)
- **Data**: JSONL tracker + YAML config + Markdown pipeline inbox

---

## Credits

Original system by [santifer](https://santifer.io) — [github.com/santifer/career-ops](https://github.com/santifer/career-ops). This fork personalizes and extends it for Python/LaTeX workflows and multi-country job search.

---

## Disclaimer

**career-ops-reiterated is a local, open-source tool — NOT a hosted service.** Your CV, contact info, and personal data stay on your machine. Never auto-submits applications — you always have the final call. Use in accordance with the Terms of Service of the career portals you interact with.

See [LEGAL_DISCLAIMER.md](LEGAL_DISCLAIMER.md) for full details. Provided under the [MIT License](LICENSE).
