# Mode: pdf — LaTeX CV Generation (ATS-Optimised)

## Full Pipeline

1. Read `cv/EnglishCVtemplate.tex` and `cv/GermanCVtemplate.tex` as CV sources
2. Ask the user for the JD if not in context (text or URL)
3. Extract 15–20 keywords from the JD
4. **Detect CV language** (see rules below) → set `--lang en` or `--lang de`
5. Detect company location → paper format:
   - US / Canada → `letter`
   - Rest of world → `a4` (default)
6. Detect role archetype → adapt framing
7. Apply **CV Tailoring Rules** (see section below) — section by section
8. Compile to PDF:
   ```bash
   python cv/generate_pdf.py --company "{company}" --role "{role}" --lang {en|de} --keywords {kw1} {kw2} ...
   ```
9. Output folder: `output/{company-slug}-{role-slug}/` containing the tailored `.tex`, `.pdf`, and all LaTeX build artefacts
10. Report: PDF path, CV language used, keyword coverage %

---

## CV Language Detection (MANDATORY — run before generating PDF)

Scan the JD for these signals and apply the **first matching rule**:

### Rule 1 → Use German CV (`--lang de`)
Any of the following is true:
- The JD is **written in German** (majority of text is German)
- German is listed as **required / mandatory / must-have** in the language or skills section
  - Signal phrases: "Deutsch (fließend)", "Deutschkenntnisse erforderlich", "German required", "German C1/C2", "business-level German", "fluent German required", "Verhandlungssicheres Deutsch"

### Rule 2 → Use English CV (`--lang en`)
Any of the following is true:
- The JD is written in English and German is **not mentioned** at all
- German is listed as **optional / nice-to-have / preferred but not required**
  - Signal phrases: "German is a plus", "German preferred", "German nice to have", "German advantageous", "von Vorteil", "wünschenswert", "German B1/B2 beneficial"

### Rule 3 → Default
If unclear (no language requirement mentioned), use `--lang en`.

### Decision summary

| JD language | German requirement | CV template |
|-------------|-------------------|-------------|
| German | Any | `--lang de` |
| English | Mandatory (C1/C2, required, fließend) | `--lang de` |
| English | Optional / nice-to-have | `--lang en` |
| English | Not mentioned | `--lang en` |

**Always state which template was selected and why** before compiling.

---

## CV Tailoring Rules (MANDATORY — apply to every build)

These rules are based on the actual structure of both CV templates. Read the selected template carefully before applying changes. **NEVER invent new projects, companies, or metrics. Only reframe real experience using JD vocabulary.**

---

### Section 1 — Professional Summary / Profil

**Structure in both templates:**
- English (`PROFESSIONAL SUMMARY`): currently 1 paragraph
- German (`PROFIL`): currently 2 paragraphs

**Rule — rewrite as exactly 2 focused points/sentences:**

Each point must:
- Directly mirror a key theme from the JD (use the JD's exact noun phrases)
- Contain **2–4 bolded words or short phrases** that match JD terminology exactly — use `\textbf{}` in LaTeX
- Stay grounded in the candidate's real experience (10+ years, ZF, portfolio/architecture/AI)
- Be concise — 2–3 lines maximum per point

**Example approach:**
- Point 1 → maps to the primary technical dimension of the JD (e.g. "Enterprise Architecture", "AI Platform", "Program Governance")
- Point 2 → maps to the delivery/leadership dimension of the JD (e.g. "cross-functional teams", "stakeholder management", "transformation")

**What NOT to do:** Do not keep the generic summary from the template. Every word should earn its place by mirroring the JD.

---

### Section 2 — Key Achievements (EN: `KEY ACHIEVEMENTS` / DE: `HERAUSRAGENDE ERFOLGE`)

**Structure in both templates:**
- Exactly **4 bullet points**
- German template already uses `\textbf{Heading:}` pattern on each bullet
- English template currently has no bold headings on bullets — **add them for every tailored build**

**Rule — 100% match to the JD:**

Each bullet must:
1. Start with a **bold heading** (`\textbf{JD Term or Theme:}`) that is taken directly from the JD's requirements, responsibilities, or key skills section — use the JD's exact vocabulary, not the candidate's own words
2. The body of the bullet must contain a **quantified proof point** from the real CV (percentages, €, timelines, team sizes — read these from the template, never invent)
3. Across the 4 bullets, cover the **4 most important dimensions** of the JD — no two bullets should cover the same JD requirement

**Selection logic:**
- Read all JD requirements → rank by prominence (mentioned first, mentioned multiple times, or in "must have" section)
- Map each of the top 4 to an existing achievement in the template
- Rewrite the heading using JD language, keep the metric from the template

**Example (if JD emphasises "Enterprise Architecture", "Stakeholder Management", "Cloud Delivery", "Agile Governance"):**
- `\textbf{Enterprise Architecture:}` → map to the ASPICE/model-based architecture bullet
- `\textbf{Stakeholder Management:}` → map to the cross-functional team / SteerCo bullet
- `\textbf{Cloud Delivery:}` → map to the Azure/Power Platform 99.95% uptime bullet
- `\textbf{Agile Governance:}` → map to the PMO / release train bullet

---

### Section 3 — Core Competencies (EN: `CORE COMPETENCIES` / DE: `KERNDISZIPLINEN`)

**Structure in both templates:**
- Lines of the format `\textbf{Category:}` followed by comma-separated skills
- Both templates already use bold headings

**Rule — 100% match to the JD:**

1. **Rename category headings** to use the JD's exact grouping language where possible
   - e.g. if JD says "Technical Leadership" instead of "Technical Architecture" → rename the heading
2. **Reorder categories** — the most JD-relevant category must appear first
3. **Within each category**, move JD-matching terms to the front of the comma list
4. **Add JD-specific terms** that the candidate genuinely has but that aren't in the template — insert at the front of the relevant category
5. **Do not remove** any category entirely — only reorder and relabel
6. Keep the Languages line exactly as-is (B2 German, Fluent English, Native Tamil)

---

### Section 4 — Professional Experience (EN: `PROFESSIONAL EXPERIENCE` / DE: `BERUFSERFAHRUNG`)

**Structure in both templates:**
- ZF Friedrichshafen AG (main employer, 4 sub-roles with bullets)
- Zenuity GmbH, TAMA Systemtechnik GmbH, Larsen & Toubro Limited (1 bullet each)
- German template: every bullet already starts with `\textbf{Heading:}` pattern
- English template: bullets currently have no bold headings

**Rules:**

**A. Maximum 4 bullets per role (already the case — do not add more).**

**B. Bold heading on every bullet (MANDATORY for both EN and DE templates):**
- Each bullet must start with `\textbf{JD-aligned heading:}`
- The heading must be a term, skill, or responsibility taken directly from the JD
- Different roles can reuse the same heading if that theme appears across your career — that signals depth

**C. Make bullets more relevant to the JD:**
- Read the JD requirements → for each role, pick the 4 existing bullets that best match
- If a role has bullets that are irrelevant to this JD, replace the **heading only** with a more relevant JD term and reframe the sentence opening — but the underlying achievement/metric stays unchanged
- Do not rewrite the metric numbers — they come from the template exactly
- For older roles (Zenuity, TAMA, L&T): 1 bullet each, reframe the heading to the most relevant JD dimension

**D. Do NOT invent projects or roles:**
- All companies, role titles, dates, and locations must match the template exactly
- You may only change: bullet headings, sentence framing, and vocabulary — not the facts

**E. ZF sub-role ordering:** Keep roles in reverse chronological order (Portfolio Manager → TPM → Lead Architect → Algorithm Engineer). Do not reorder.

---

### Section 5 — Education, Patents, Certifications

**Do not change these sections.** Copy from the template verbatim. These are factual and must not be tailored.

---

### Tailoring checklist (verify before compiling)

- [ ] Summary has exactly 2 points with bolded JD-matching terms
- [ ] Key Achievements has 4 bullets, each with a bold heading from JD vocabulary
- [ ] The 4 achievement headings cover 4 distinct JD requirements
- [ ] Core Competencies reordered, most JD-relevant category first
- [ ] Every experience bullet has a bold heading using JD terminology
- [ ] No bullet exceeds the 4-bullet limit per role
- [ ] No invented metrics, companies, or projects
- [ ] Education, Patents, Certifications unchanged

---

## ATS Rules (clean parsing)

- Single-column layout (no sidebars, no parallel columns)
- No text in images/SVGs
- No critical info in PDF headers/footers (ATS ignores these)
- UTF-8, selectable text (not rasterised)
- No nested tables
- JD keywords distributed: Summary (top 5), first bullet of each role, Competencies section

---

## Keyword Injection Strategy (ethical, truth-based)

Reformulate real experience using the JD's exact vocabulary:
- JD says "RAG pipelines" and CV says "LLM workflows with retrieval" → "RAG pipeline design and LLM orchestration workflows"
- JD says "MLOps" and CV says "observability, evals, error handling" → "MLOps and observability: evals, error handling, cost monitoring"
- JD says "Enterprise Architecture" and CV says "system architecture" → "Enterprise Architecture across perception, planning, and platform subsystems"

**NEVER add skills the candidate doesn't have. Only reformulate real experience using the JD's exact vocabulary.**

---

## LaTeX Variables (tailored builds)

The `cv/generate_pdf.py` script injects these into the compiled LaTeX:

```latex
\renewcommand{\TargetCompany}{Anthropic}
\renewcommand{\TargetRole}{Senior AI Architect}
\renewcommand{\JobKeywords}{RAG, LLMOps, multi-agent, evals}
```

---

## Post-generation

Update tracker: change `pdf` from `false` to `true` in `data/applications.jsonl` for this entry.
