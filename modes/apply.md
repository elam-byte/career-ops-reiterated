# Mode: apply — Live Application Assistant

Interactive mode for when the candidate is filling out an application form in their browser. Reads what's on screen, loads prior evaluation context, and generates personalised answers for each form field.

## Requirements

- **Best with Playwright visible**: In visible mode, the candidate sees the browser and Claude can interact with the page.
- **Without Playwright**: The candidate shares a screenshot or pastes the questions manually.

## Workflow

```
1. DETECT    → Read active Chrome tab (screenshot / URL / title)
2. IDENTIFY  → Extract company + role from the page
3. SEARCH    → Match against existing reports in reports/
4. LOAD      → Read full report + Section G (if it exists)
5. COMPARE   → Does the on-screen role match the evaluated one? If changed → warn
6. ANALYSE   → Identify ALL visible form questions
7. GENERATE  → For each question, generate a personalised answer
8. PRESENT   → Display formatted answers ready for copy-paste
```

## Step 1 — Detect the offer

**With Playwright:** Take a snapshot of the active page. Read title, URL, and visible content.

**Without Playwright:** Ask the candidate to:
- Share a screenshot of the form (Read tool can process images)
- Or paste the form questions as text
- Or provide company + role so we can search for it

## Step 2 — Identify and find context

1. Extract company name and role title from the page
2. Search `reports/` for the company name (case-insensitive grep)
3. If match found → load the full report
4. If Section G exists → use those draft answers as a starting point
5. If NO match → alert the candidate and offer to run auto-pipeline first

## Step 3 — Detect role changes

If the on-screen role differs from the evaluated one:
- **Alert the candidate**: "The role has changed from [X] to [Y]. Should I re-evaluate or adapt the answers to the new title?"
- **Adapt**: Adjust answers to the new role without re-evaluating
- **Re-evaluate**: Run a full A-F evaluation, update the report, regenerate Section G
- **Update tracker**: Change the role title in applications.jsonl if appropriate

## Step 4 — Analyse form questions

Identify ALL visible questions:
- Free text fields (cover letter, why this role, etc.)
- Dropdowns (how did you hear, work authorisation, etc.)
- Yes/No (relocation, visa, etc.)
- Salary fields (range, expectation)
- Upload fields (résumé, cover letter PDF)

Classify each question:
- **Already answered in Section G** → adapt the existing draft
- **New question** → generate answer from report + cv.md

## Step 5 — Generate answers

For each question, generate the answer following these rules:

1. **Report context**: Use proof points from Block B, STAR stories from Block F
2. **Prior Section G**: If a draft exists, use it as a base and refine
3. **"I'm choosing you" tone**: See tone rules below
4. **Specificity**: Reference something concrete from the JD visible on screen
5. **Proof point hook**: Include a metric or achievement, not a claim

**Output format:**

```
## Application Answers: [Company] — [Role]

Based on: Report #NNN | Score: X.X/5 | Archetype: [type]

---

### 1. [Exact form question]
> [Answer ready for copy-paste]

### 2. [Next question]
> [Answer]

...

---

Notes:
- [Any observations about the role, changes, etc.]
- [Personalisation suggestions the candidate should review]
```

### Answer tone rules

**Position: "I'm choosing you."** — the candidate has options and is choosing this company for concrete reasons.

- **Confident, not arrogant**: "I've spent the past year building production AI agent systems — your role is where I want to apply that next."
- **Selective, not superior**: "I've been intentional about finding a team where I can contribute meaningfully from day one."
- **Specific and concrete**: Always reference something REAL from the JD and something REAL from the candidate's experience.
- **Direct, no fluff**: 2–4 sentences per answer. No "I'm passionate about…" or "I would love the opportunity to…"
- **Proof over claim**: Instead of "I'm great at X", say "I built X that achieves Y."

**Per question framework:**
- **Why this role?** → "Your [specific thing] maps directly to [specific thing I built]."
- **Why this company?** → Name something concrete about the company.
- **Relevant experience?** → One quantified proof point.
- **Good fit?** → "I sit at the intersection of [A] and [B], which is exactly where this role lives."
- **How did you hear?** → Honest: "Found via [portal/scan], evaluated against my criteria, scored highly."

## Step 6 — Post-apply (optional)

If the candidate confirms they submitted:
1. Update status in `data/applications.jsonl` from "Evaluated" to "Applied"
2. Update Section G of the report with the final submitted answers
3. Suggest next step: `/career-ops-reiterated contact` for LinkedIn outreach

## Scroll handling

If the form has more questions than visible:
- Ask the candidate to scroll and share another screenshot
- Or paste the remaining questions
- Process in iterations until the full form is covered
