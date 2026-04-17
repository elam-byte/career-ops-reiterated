# Mode: scan — Portal Scanner (Job Discovery)

Scans configured job portals, filters by title relevance, and adds new offers to the pipeline for later evaluation.

## Recommended execution

Run as a subagent to avoid consuming main context:

```
Agent(
    subagent_type="general-purpose",
    prompt="[content of this file + specific data]",
    run_in_background=True
)
```

## Configuration

Read `portals.yml` which contains:
- `search_queries`: WebSearch queries with `site:` filters per portal (broad discovery)
- `tracked_companies`: Specific companies with `careers_url` for direct navigation
- `title_filter`: Positive / negative / seniority_boost keywords for title filtering

Also read `config/profile.yml` → `search.countries` list and `search.include_remote`.

## Country filtering (APPLY BEFORE SCANNING)

1. Read `search.countries` from `config/profile.yml` (e.g. `[DE]`)
2. Add `REMOTE` to the active set if `search.include_remote: true`
3. **Filter `tracked_companies`**: only scan entries whose `country` list overlaps the active set.
   - If a company has no `country` field → include it (assume global / remote)
4. **Filter `search_queries`**: only run queries whose `country` list overlaps the active set.
   - If a query has no `country` field → include it (assumed global)

**Example:** active = `[DE, REMOTE]` → scans Aleph Alpha (DE), n8n (DE, REMOTE), Anthropic (US, REMOTE) ✅ but skips Bending Spoons (IT only) ❌

**To scan a different country in one session**, the user can say:
> "Scan for jobs in India" or "Add GB to my scan countries"

If the user says this, temporarily add that country to the active set for this run only (do not save to profile.yml unless they ask to make it permanent).

## Discovery strategy (3 levels)

### Level 1 — Direct Playwright (PRIMARY)

**For each company in `tracked_companies`:** Navigate to its `careers_url` with Playwright (`browser_navigate` + `browser_snapshot`), read ALL visible job listings, and extract title + URL from each. This is the most reliable method because:
- Sees the page in real time (not cached Google results)
- Works with SPAs (Ashby, Lever, Workday)
- Detects new offers instantly
- Does not depend on Google indexing

**Every company MUST have `careers_url` in portals.yml.** If missing, find it once, save it, and use it in future scans.

### Level 2 — Greenhouse API (COMPLEMENTARY)

For companies on Greenhouse, the JSON API (`boards-api.greenhouse.io/v1/boards/{slug}/jobs`) returns clean structured data. Use as a fast complement to Level 1 — faster than Playwright but only works with Greenhouse.

### Level 3 — WebSearch queries (BROAD DISCOVERY)

The `search_queries` with `site:` filters cover portals transversally (all Ashby, all Greenhouse, etc.). Useful for discovering NEW companies not yet in `tracked_companies`, but results may be stale.

**Execution priority:**

1. Level 1: Playwright → all `tracked_companies` with `careers_url`
2. Level 2: API → all `tracked_companies` with `api:`
3. Level 3: WebSearch → all `search_queries` with `enabled: true`

Levels are additive — all run, results are merged and deduplicated.

## Workflow

1. **Read config**: `portals.yml`
2. **Read history**: `data/scan-history.jsonl` → URLs already seen
3. **Read dedup sources**: `data/applications.jsonl` + `data/pipeline.md`

4. **Level 1 — Playwright scan** (parallel in batches of 3-5):
   - For each company in `tracked_companies` with `enabled: true` and `careers_url` defined:
   - a. `browser_navigate` to the `careers_url`
   - b. `browser_snapshot` to read all job listings
   - c. If the page has filters/departments, navigate relevant sections
   - d. For each job listing extract: `{title, url, company}`
   - e. If the page paginates, navigate additional pages
   - f. If `careers_url` fails (404, redirect, timeout), skip and note for URL update

5. **Level 2 — Greenhouse APIs** (parallel):
   - For each company in `tracked_companies` with `api:` defined and `enabled: true`:
   - a. WebFetch the API URL → JSON with job list
   - b. For each job extract: `{title, url, company}`
   - c. Accumulate (dedup with Level 1)

6. **Level 3 — WebSearch queries** (parallel where possible):
   - For each query in `search_queries` with `enabled: true`:
   - a. Run WebSearch with the defined `query`
   - b. From each result extract: `{title, url, company}`
   - c. Accumulate (dedup with Level 1+2)

7. **Filter by title** using `title_filter` from `portals.yml`:
   - At least 1 keyword from `positive` must appear in the title (case-insensitive)
   - 0 keywords from `negative` may appear
   - `seniority_boost` keywords give priority but are not mandatory

8. **Deduplicate** against 3 sources:
   - `scan-history.jsonl` → exact URL already seen
   - `applications.jsonl` → company + normalised role already evaluated
   - `pipeline.md` → exact URL already in pending or processed

### 7.5 — Verify liveness of WebSearch results (Level 3) — BEFORE adding to pipeline

WebSearch results may be stale (Google caches results for weeks or months). To avoid evaluating expired offers, verify with Playwright each new URL from Level 3. Levels 1 and 2 are inherently real-time and do not require this check.

For each new URL from Level 3 (run sequentially in the main context — liveness checks are lightweight and don't need parallel subagents):
- a. `browser_navigate` to the URL
- b. `browser_snapshot` to read content
- c. Classify:
  - **Active**: job title visible + role description + Apply/Submit button
  - **Expired** (any of these signals):
    - Final URL contains `?error=true` (Greenhouse redirects this way for closed offers)
    - Page contains: "job no longer available" / "no longer open" / "position has been filled" / "this job has expired" / "page not found"
    - Only navbar and footer visible, no JD content (content < ~300 chars)
- d. If expired: record in `scan-history.jsonl` with status `skipped_expired` and discard
- e. If active: continue to step 8

**Do not abort the entire scan if one URL fails.** If `browser_navigate` errors (timeout, 403, etc.), mark as `skipped_expired` and continue.

9. **For each new verified offer that passes filters**:
   - a. Add to `pipeline.md` "Pending" section: `- [ ] {url} | {company} | {title}`
   - b. Record in `scan-history.jsonl`:
     ```json
     {"url": "...", "first_seen": "YYYY-MM-DD", "portal": "...", "title": "...", "company": "...", "status": "added"}
     ```

10. **Filtered by title**: record in `scan-history.jsonl` with status `skipped_title`
11. **Duplicates**: record with status `skipped_dup`
12. **Expired (Level 3)**: record with status `skipped_expired`

## Title and company extraction from WebSearch results

Results come in formats like: `"Job Title @ Company"` or `"Job Title | Company"` or `"Job Title — Company"`.

Extraction patterns by portal:
- **Ashby**: `"Senior AI PM (Remote) @ EverAI"` → title: `Senior AI PM`, company: `EverAI`
- **Greenhouse**: `"AI Engineer at Anthropic"` → title: `AI Engineer`, company: `Anthropic`
- **Lever**: `"Product Manager - AI @ Temporal"` → title: `Product Manager - AI`, company: `Temporal`

Generic regex: `(.+?)(?:\s*[@|—–-]\s*|\s+at\s+)(.+?)$`

## Private / login-gated URLs

If a URL is not publicly accessible:
1. Save the JD to `jds/{company}-{role-slug}.md`
2. Add to pipeline.md as: `- [ ] local:jds/{company}-{role-slug}.md | {company} | {title}`

## Scan History (JSONL)

`data/scan-history.jsonl` tracks ALL URLs seen — one JSON record per line:

```json
{"url": "https://...", "first_seen": "2026-04-09", "portal": "Ashby", "title": "Senior AI PM", "company": "EverAI", "status": "added"}
{"url": "https://...", "first_seen": "2026-04-09", "portal": "Greenhouse", "title": "Junior Dev", "company": "BigCo", "status": "skipped_title"}
```

## Scan summary output

```
Portal Scan — {YYYY-MM-DD}
━━━━━━━━━━━━━━━━━━━━━━━━━━
Queries run: N
Offers found: N total
Filtered by title: N relevant
Duplicates: N (already evaluated or in pipeline)
Expired discarded: N (dead links, Level 3)
New added to pipeline.md: N

  + {company} | {title} | {portal}
  ...

→ Run /career-ops-reiterated pipeline to evaluate new offers.
```

## careers_url management

Every company in `tracked_companies` must have `careers_url` — the direct URL to their jobs page.

**Known patterns by platform:**
- **Ashby:** `https://jobs.ashbyhq.com/{slug}`
- **Greenhouse:** `https://job-boards.greenhouse.io/{slug}` or `https://job-boards.eu.greenhouse.io/{slug}`
- **Lever:** `https://jobs.lever.co/{slug}`
- **Custom:** The company's own careers URL (e.g. `https://openai.com/careers`)

**If `careers_url` is missing** for a company:
1. Try the pattern for its known platform
2. If that fails, WebSearch: `"{company}" careers jobs`
3. Navigate with Playwright to confirm it works
4. **Save the found URL to portals.yml** for future scans
