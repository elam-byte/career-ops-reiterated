# Mode: evaluate — Full A-F Evaluation

When the candidate pastes a job offer (text or URL), ALWAYS deliver all 6 blocks:

## Step 0 — Archetype Detection

Classify the offer into one of the 6 archetypes (see `_shared.md`). If hybrid, indicate the 2 closest. This determines:
- Which proof points to prioritise in Block B
- How to rewrite the summary in Block E
- Which STAR stories to prepare in Block F

## Block A — Role Summary

Table with:
- Detected archetype
- Domain (platform / agentic / LLMOps / ML / enterprise)
- Function (build / consult / manage / deploy)
- Seniority
- Remote policy (full / hybrid / onsite)
- Team size (if mentioned)
- **CV language** → `EN` or `DE` (see rule below)
- TL;DR in 1 sentence

**CV language rule** (detect here, used later when generating PDF):
- JD written in German → `DE`
- JD in English + German mandatory/required (C1/C2, "fließend", "required") → `DE`
- JD in English + German optional/nice-to-have or not mentioned → `EN`

## Block B — CV Match

Read `cv.md`. Create a table mapping each JD requirement to exact lines from the CV.

**Adapted to archetype:**
- FDE → prioritise fast delivery and client-facing proof points
- SA → prioritise system design and integrations
- PM → prioritise product discovery and metrics
- LLMOps → prioritise evals, observability, pipelines
- Agentic → prioritise multi-agent, HITL, orchestration
- Transformation → prioritise change management, adoption, scaling

**Gaps section** with mitigation strategy for each gap:
1. Is it a hard blocker or a nice-to-have?
2. Can the candidate demonstrate adjacent experience?
3. Is there a portfolio project that covers this gap?
4. Concrete mitigation plan (cover letter phrase, quick project, etc.)

## Block C — Level & Strategy

1. **Detected level** in the JD vs **candidate's natural level for that archetype**
2. **"Sell senior without lying" plan**: specific phrases adapted to archetype, key achievements to highlight, how to position founder experience as an advantage
3. **"If they down-level me" plan**: accept if comp is fair, negotiate a 6-month review, clear promotion criteria

## Block D — Compensation Research (not scored)

> This block is **informational only** — compensation is not included in the score.
> Its purpose is to help you negotiate from a position of knowledge.

Use WebSearch to research:
- Current market salaries for this role (Glassdoor, Levels.fyi, LinkedIn Salary, Blind)
- This company's compensation reputation
- Demand trend for this role type

| Source | Role | Level | Location | Range | Notes |
|--------|------|-------|----------|-------|-------|

**Suggested ask:** Based on the above data and your profile, suggest a specific range the candidate should target.

If no reliable data exists, say so — never invent figures.

## Block E — Personalisation Plan

| # | Section | Current state | Proposed change | Why |
|---|---------|---------------|-----------------|-----|
| 1 | Summary | … | … | … |
| … | … | … | … | … |

Top 5 CV changes + Top 5 LinkedIn changes to maximise match.

## Block F — Interview Prep

6–10 STAR+R stories mapped to JD requirements (STAR + **Reflection**):

| # | JD Requirement | STAR+R Story | S | T | A | R | Reflection |
|---|----------------|--------------|---|---|---|---|------------|

The **Reflection** column captures what was learned or what would be done differently. This signals seniority — junior candidates describe what happened, senior candidates extract lessons.

**Story Bank:** If `interview-prep/story-bank.md` exists, check whether any of these stories are already there. If not, append new ones. Over time this builds a reusable bank of 5–10 master stories.

**Selected and framed by archetype:**
- FDE → emphasise delivery speed and client-facing outcomes
- SA → emphasise architecture decisions
- PM → emphasise discovery and trade-offs
- LLMOps → emphasise metrics, evals, production hardening
- Agentic → emphasise orchestration, error handling, HITL
- Transformation → emphasise adoption, organisational change

Include also:
- 1 recommended case study (which project to present and how)
- Red-flag questions and how to answer them (e.g. "Why did you sell your company?", "Do you have direct reports?")

---

## Post-Evaluation

**ALWAYS** after generating blocks A–F:

### 1. Save report .md

Save the full evaluation to `reports/{###}-{company-slug}-{YYYY-MM-DD}.md`.

- `{###}` = next sequential number (3 digits, zero-padded)
- `{company-slug}` = company name lowercase with hyphens
- `{YYYY-MM-DD}` = today's date

**Report format:**

```markdown
# Evaluation: {Company} — {Role}

**Date:** {YYYY-MM-DD}
**Archetype:** {detected}
**Score:** {X/5}
**URL:** {job url}
**PDF:** {path or pending}

---

## A) Role Summary
## B) CV Match
## C) Level & Strategy
## D) Compensation Research
## E) Personalisation Plan
## F) Interview Prep
## G) Draft Application Answers
(only if score >= 4.5)

---

## Extracted Keywords
(15–20 ATS keywords from the JD)
```

### 2. Ask about PDF (WAIT FOR USER)

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

### 3. Register in tracker

**ALWAYS** write a new entry to `data/applications.jsonl`:

```json
{
  "id": "###",
  "date": "YYYY-MM-DD",
  "company": "Company",
  "role": "Role",
  "url": "https://...",
  "score": 4.2,
  "status": "Evaluated",
  "archetype": "AI Architect",
  "cv_lang": "EN",
  "country": "DE",
  "pdf": false,
  "report": "reports/###-company-YYYY-MM-DD.md",
  "notes": "One-line summary",
  "comp_suggestion": "€120k–140k",
  "added_at": "YYYY-MM-DDTHH:MM:SS"
}
```

**Before writing**, call `check_duplicate` from `dashboard/utils.py` — or replicate the logic:
- If exact URL match → update the existing entry instead of creating a new one
- If company + role fuzzy match (>85% + >75% similarity) → update existing entry
