# Mode: evaluate — Full A-F Evaluation

When the candidate pastes a job offer (text or URL), deliver Blocks A and B to the terminal, then write the full report (A–F) silently to `reports/`.

---

## Step 0 — Archetype Detection

Classify the offer using `_shared.md` archetype signals. If hybrid, indicate the 2 closest. This determines which proof points to prioritise in Block B, which CV changes to suggest in Block E, and which STAR stories to prepare in Block F.

After detecting, read `modes/_profile.md` for Elam's specific framing and proof points for that archetype.

---

## TERMINAL OUTPUT (shown to user)

### Block A — Role Summary

Table with:
- Detected archetype
- Domain
- Function (build / consult / manage / deploy)
- Seniority
- Remote policy (full / hybrid / onsite)
- Team size (if mentioned)
- **CV language** → `EN` or `DE`
- TL;DR in 1 sentence

**CV language rule:**
- JD written in German → `DE`
- JD in English + German mandatory (C1/C2, "fließend", "required") → `DE`
- JD in English + German optional or not mentioned → `EN`

---

### Block B — CV Match

Read `cv.md`. Create a table mapping each JD requirement to exact lines from the CV.

**Adapted framing by archetype:**
- AI Platform / LLMOps → prioritise evals, observability, pipelines
- Agentic / Automation → prioritise multi-agent, HITL, orchestration
- Technical AI PM → prioritise product discovery, roadmap, metrics
- AI Solutions Architect → prioritise AI system design, ML platform, integrations
- AI Forward Deployed → prioritise fast delivery and client-facing proof points
- AI Transformation → prioritise change management, adoption, scaling
- Program Manager → prioritise PMO, SteerCo, RAID, cross-functional delivery, release trains
- Technical Program Manager → prioritise multi-team engineering coordination, dependency management, release management
- Product Manager → prioritise backlog ownership, go-to-market, product lifecycle, customer engagement
- Project Manager → prioritise project delivery, risk management, budget tracking, milestone ownership
- Solution Architect → prioritise enterprise architecture decisions, cloud design, integration patterns, technical governance
- Systems Architect → prioritise safety-critical design, ASPICE/ISO 26262, MBSE, real-time systems, embedded/cloud co-design

**Gaps section** — for each gap:
1. Hard blocker or nice-to-have?
2. Adjacent experience that covers it?
3. Portfolio project that addresses it?
4. Mitigation plan (cover letter phrase, quick project, etc.)

---

### Terminal summary prompt

After Block B, print:

```
---
Evaluation complete.

Company:   {Company}
Role:      {Role}
Score:     {X/5} — {recommendation}
CV to use: {English / German} (detected from JD)
Report:    reports/{###}-{company-slug}-{YYYY-MM-DD}.md

(Full report with level strategy, comp research, personalisation plan, and interview prep saved to reports/)

What would you like to generate?
  → pdf          — Tailored CV PDF (LaTeX → .pdf)
  → coverletter  — Cover letter (.docx)
  → both         — CV PDF + cover letter
  → skip         — Nothing for now
```

If score is below 3.5, add: "Score is below 3.5 — recommend skipping this application."

Only proceed based on the user's reply:
- `pdf`         → run `modes/pdf.md`, then ask if they also want a cover letter
- `coverletter` → PDF must exist first; if not found, run pdf first then coverletter
- `both`        → run `modes/pdf.md` first, then `modes/coverletter.md`
- `skip`        → do nothing

---

## REPORT ONLY (written silently to `reports/`, NOT printed to terminal)

### Block C — Level & Strategy

1. **Detected level** in the JD vs candidate's natural level for that archetype
2. **"Sell senior without lying" plan**: archetype-specific phrases, key achievements to highlight
3. **"If they down-level me" plan**: accept if comp is fair, negotiate 6-month review, clear promotion criteria

**Adapted by archetype:**
- Program Manager / TPM → emphasise governance scope, team size, budget accountability
- Product Manager → emphasise customer impact, adoption metrics, roadmap outcomes
- Project Manager → emphasise on-time delivery rate, risk mitigation, budget adherence
- Solution Architect / Systems Architect → emphasise patents, technical decisions with business impact, cross-domain depth
- AI archetypes → emphasise production deployments, eval frameworks, model performance metrics

---

### Block D — Compensation Research (not scored)

> Informational only — not included in the score. Purpose: negotiate from a position of knowledge.

Use WebSearch to research:
- Market salaries for this role (Glassdoor, Levels.fyi, LinkedIn Salary, Blind)
- Company compensation reputation
- Demand trend for this role type

| Source | Role | Level | Location | Range | Notes |
|--------|------|-------|----------|-------|-------|

**Suggested ask:** Specific range based on data + profile.

If no reliable data exists, say so — never invent figures.

---

### Block E — Personalisation Plan

Top 5 CV changes + Top 5 LinkedIn changes to maximise match.

| # | Section | Current state | Proposed change | Why |
|---|---------|---------------|-----------------|-----|

**Adapted by archetype:**
- Program Manager / TPM → surface SteerCo, RAID, release train, forecast accuracy
- Product Manager → surface backlog metrics, customer discovery, go-to-market outcomes
- Project Manager → surface delivery rate, risk registers, budget performance
- Solution Architect → surface Azure architecture, integration patterns, technical governance, patents
- Systems Architect → surface ASPICE, ISO 26262, MBSE, autonomy stack, safety-critical decisions
- AI archetypes → surface model metrics, eval frameworks, pipeline design, production deployments

---

### Block F — Interview Prep

6–10 STAR+R stories mapped to JD requirements:

| # | JD Requirement | Story summary | S | T | A | R | Reflection |
|---|----------------|---------------|---|---|---|---|------------|

**Reflection** = what was learned / what would be done differently (signals seniority).

**Story Bank:** If `interview-prep/story-bank.md` exists, check for existing stories. Append new ones. Build toward a reusable bank of 5–10 master stories.

**Adapted by archetype:**
- Program Manager / TPM → emphasise governance under pressure, cross-team alignment, dependency resolution
- Product Manager → emphasise discovery trade-offs, customer validation, roadmap pivots
- Project Manager → emphasise risk mitigation, stakeholder management, scope control
- Solution Architect → emphasise architecture decisions with long-term impact, build-vs-buy trade-offs
- Systems Architect → emphasise safety-critical constraints, embedded/cloud co-design decisions, ASPICE compliance
- AI archetypes → emphasise production hardening, eval design, multi-agent orchestration

Include:
- 1 recommended case study (which project to present and how)
- Red-flag questions and how to answer them

---

## Post-Evaluation Actions (always run silently)

### 1. Save report

Save full evaluation to `reports/{###}-{company-slug}-{YYYY-MM-DD}.md`:

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

---

## Extracted Keywords
(15–20 ATS keywords from the JD)
```

### 2. Register in tracker

Append to `data/applications.jsonl`:

```json
{
  "id": "###",
  "date": "YYYY-MM-DD",
  "company": "Company",
  "role": "Role",
  "url": "https://...",
  "score": 4.2,
  "status": "Evaluated",
  "archetype": "Solution Architect",
  "cv_lang": "EN",
  "country": "DE",
  "pdf": false,
  "report": "reports/###-company-YYYY-MM-DD.md",
  "notes": "One-line summary",
  "comp_suggestion": "€120k–140k",
  "added_at": "YYYY-MM-DDTHH:MM:SS"
}
```

**Before writing:** check for duplicates:
- Exact URL match → update existing entry
- Company + role fuzzy match (>85% + >75%) → update existing entry
