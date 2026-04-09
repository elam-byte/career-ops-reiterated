# Mode: pipeline — URL Inbox (Second Brain)

Processes job URLs accumulated in `data/pipeline.md`. The user adds URLs whenever they want and then runs `/career-ops-reiterated pipeline` to process them all.

## Workflow

1. **Read** `data/pipeline.md` → find `- [ ]` items in the "Pending" section
2. **For each pending URL**:
   a. Calculate the next sequential `REPORT_NUM` (read `reports/`, take highest number + 1)
   b. **Extract JD** using Playwright (`browser_navigate` + `browser_snapshot`) → WebFetch → WebSearch
   c. If URL is inaccessible → mark as `- [!]` with a note and continue
   d. **Run full auto-pipeline**: A-F evaluation → Report .md → LaTeX PDF (if score >= 3.0) → Tracker
   e. **Move from "Pending" to "Processed"**: `- [x] #NNN | URL | Company | Role | Score/5 | PDF ✅/❌`
3. **If 3+ pending URLs**, launch parallel agents (Agent tool with `run_in_background`) for maximum speed.
4. **When done**, show summary table:

```
| # | Company | Role | Score | PDF | Recommended action |
```

## pipeline.md format

```markdown
## Pending
- [ ] https://jobs.example.com/posting/123
- [ ] https://boards.greenhouse.io/company/jobs/456 | Company Inc | Senior PM
- [!] https://private.url/job — Error: login required

## Processed
- [x] #143 | https://jobs.example.com/posting/789 | Acme Corp | AI PM | 4.2/5 | PDF ✅
- [x] #144 | https://boards.greenhouse.io/xyz/jobs/012 | BigCo | SA | 2.1/5 | PDF ❌
```

## Intelligent JD extraction from URL

1. **Playwright (preferred):** `browser_navigate` + `browser_snapshot`. Works with all SPAs.
2. **WebFetch (fallback):** For static pages or when Playwright is unavailable.
3. **WebSearch (last resort):** Search portals that index the JD as static HTML.

**Special cases:**
- **LinkedIn**: May require login → mark `[!]` and ask user to paste the text
- **PDF**: If the URL points to a PDF, read it directly with the Read tool
- **`local:` prefix**: Read the local file. Example: `local:jds/linkedin-pm-ai.md` → read `jds/linkedin-pm-ai.md`

## Automatic numbering

1. List all files in `reports/`
2. Extract the number prefix (e.g., `142-company-...` → 142)
3. New number = highest found + 1

## Sync check

Before processing any URL, verify sync:
```bash
python scripts/check_sync.py
```
If out of sync, warn the user before continuing.

## Duplicate check

Before processing any URL, call `check_duplicate` (from `dashboard/utils.py` or replicate the logic):
- If the URL already exists in `data/applications.jsonl` → skip and log as duplicate
- If company + role fuzzy match → ask user before creating a new entry
