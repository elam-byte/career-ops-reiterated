# Mode: auto-pipeline — Full Automatic Pipeline

When the user pastes a JD (text or URL) without an explicit sub-command, run the FULL pipeline in sequence:

## Step 0 — Extract JD

If the input is a **URL** (not pasted JD text), use this strategy to extract the content:

**Priority order:**

1. **Playwright (preferred):** Most job portals (Lever, Ashby, Greenhouse, Workday) are SPAs. Use `browser_navigate` + `browser_snapshot` to render and read the JD.
2. **WebFetch (fallback):** For static pages (ZipRecruiter, WeLoveProduct, company career pages).
3. **WebSearch (last resort):** Search the role title + company on secondary portals that index the JD as static HTML.

**If none work:** Ask the candidate to paste the JD manually or share a screenshot.

**If the input is JD text** (not a URL): use it directly, no fetching needed.

## Step 1 — A-F Evaluation
Run exactly as in the `evaluate` mode (read `modes/evaluate.md` for all A-F blocks).

## Step 2 — Save Report .md
Save the full evaluation to `reports/{###}-{company-slug}-{YYYY-MM-DD}.md` (see format in `modes/evaluate.md`).

## Step 3 — PDF Decision (WAIT FOR USER)

**Do NOT generate the PDF automatically.** After saving the report, present a summary and ask:

```
---
Evaluation complete.

Company:   {Company}
Role:      {Role}
Score:     {X/5} — {recommendation}
CV to use: {English / German} (detected from JD)
Report:    reports/{###}-{company-slug}-{YYYY-MM-DD}.md

What would you like to generate?
  → pdf          — Tailored CV PDF (LaTeX → .pdf)
  → coverletter  — Cover letter (.docx, opens in LibreOffice / Word)
  → both         — CV PDF + cover letter
  → skip         — Nothing for now (run /career-ops-reiterated pdf or coverletter later)
```

Only proceed based on the user's reply:
- `pdf`         → run `modes/pdf.md`, then ask if they also want a cover letter
- `coverletter` → PDF must exist first; if `output/{slug}/cv-{slug}.tex` not found, run pdf first then coverletter
- `both`        → run `modes/pdf.md` first, then `modes/coverletter.md` (cover letter uses the tailored CV as input)
- `skip`        → do nothing

If score is below 3.5, add a note: "Score is below 3.5 — recommend skipping this application."

## Step 4 — Draft Application Answers (only if score >= 4.5)

If the final score is >= 4.5, generate draft answers for the application form:

1. **Extract form questions**: Use Playwright to navigate to the form and take a snapshot. If unavailable, use generic questions below.
2. **Generate answers** following the tone rules in `modes/apply.md`.
3. **Save in the report** as section `## G) Draft Application Answers`.

### Generic questions (use if form questions cannot be extracted)

- Why are you interested in this role?
- Why do you want to work at [Company]?
- Tell us about a relevant project or achievement
- What makes you a good fit for this position?
- How did you hear about this role?

### Answer tone

**Position: "I'm choosing you."** — The candidate has options and is choosing this company for concrete reasons.

- **Confident without arrogance**: "I've spent the past year building production AI agent systems — your role is where I want to apply that experience next."
- **Selective without condescension**: "I've been intentional about finding a team where I can contribute meaningfully from day one."
- **Specific and concrete**: Always reference something REAL from the JD and REAL from the candidate's experience.
- **Direct, no fluff**: 2–4 sentences per answer. No "I'm passionate about…"
- **Proof, not claims**: Instead of "I'm great at X", say "I built X that does Y."

**Per question:**
- **Why this role?** → "Your [specific thing] maps directly to [specific thing I built]."
- **Why this company?** → Name something concrete about the company.
- **Relevant experience?** → One quantified proof point.
- **Good fit?** → "I sit at the intersection of [A] and [B], which is exactly where this role lives."
- **How did you hear?** → Honest: "Found via [portal/scan], evaluated against my criteria, scored highest."

## Step 5 — Update Tracker

Write a new record to `data/applications.jsonl` with all fields including Report and PDF status.

**If any step fails**, continue with the remaining steps and mark the failed step as pending in the tracker notes.
