# Setup Guide

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and configured
- Python 3.10+
- XeLaTeX (for PDF generation): `sudo apt install texlive-xetex texlive-fonts-extra`
- Playwright (for scraping and offer verification): `pip install playwright && playwright install chromium`

## Quick Start (5 steps)

### 1. Clone the repo

```bash
git clone https://github.com/santifer/career-ops-reiterated.git
cd career-ops-reiterated
```

### 2. Install Python dependencies

```bash
pip install -r dashboard/requirements.txt
```

### 3. Configure your profile

```bash
cp config/profile.example.yml config/profile.yml
```

Edit `config/profile.yml` with your personal details: name, email, target roles, narrative, proof points.

### 4. Add your CV

Place your LaTeX CV files in the `cv/` folder:
- `cv/EnglishCVtemplate.tex` — English version
- `cv/GermanCVtemplate.tex` — German version (optional)

Also create `cv.md` in the project root — a markdown version of your CV used for evaluation context.

(Optional) Create `article-digest.md` with proof points from your portfolio projects/articles.

### 5. Configure portals

```bash
cp templates/portals.example.yml portals.yml
```

Edit `portals.yml`:
- Update `title_filter.positive` with keywords matching your target roles
- Add companies you want to track in `tracked_companies`
- Customize `search_queries` for your preferred job boards

### 6. Start using

Open Claude Code in this directory:

```bash
claude
```

Then paste a job offer URL or description. Career-ops will automatically evaluate it, generate a report, create a tailored PDF, and track it.

## Available Commands

| Action | How |
|--------|-----|
| Evaluate an offer | Paste a URL or JD text |
| Search for offers | `/career-ops-reiterated scan` |
| Process pending URLs | `/career-ops-reiterated pipeline` |
| Generate a PDF | `/career-ops-reiterated pdf` |
| Batch evaluate | `/career-ops-reiterated batch` |
| Check tracker status | `/career-ops-reiterated tracker` |
| Fill application form | `/career-ops-reiterated apply` |

## Verify Setup

```bash
# Check LaTeX is available
xelatex --version

# Check Python deps
python -c "import streamlit, playwright; print('OK')"

# Check Playwright browser
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## Dashboard (Optional)

```bash
# Web dashboard
cd dashboard && streamlit run app.py

# Terminal dashboard
python dashboard/terminal.py
```
