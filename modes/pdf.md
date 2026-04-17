# Mode: pdf — LaTeX CV Generation (ATS-Optimised)

## Full Pipeline

1. Ask the user for the JD if not in context (text or URL)
2. Extract 15–20 keywords from the JD
3. **Detect CV language** (see rules below) → set `--lang en` or `--lang de`
4. **Read the selected template only** — `cv/EnglishCVtemplate.tex` for `--lang en`, `cv/GermanCVtemplate.tex` for `--lang de`. Do NOT read both.
5. Detect company location → paper format:
   - US / Canada → `letter`
   - Rest of world → `a4` (default)
6. Detect role archetype → adapt framing (see Archetype Detection below)
7. Apply **CV Tailoring Rules** (see section below) — section by section
8. Compile to PDF:
   ```bash
   python cv/generate_pdf.py --company "{company}" --role "{role}" --lang {en|de} --keywords {kw1} {kw2} ...
   ```
9. Output folder: `output/{company-slug}-{role-slug}/` containing the tailored `.tex`, `.pdf`, and all LaTeX build artefacts
10. Report: PDF path, CV language used, keyword coverage %

> **NEVER print the generated LaTeX source to the terminal/chat.** Write it directly to the `.tex` file. Only show the compile command, output path, and report summary.

> **NEVER use `--` (en-dash) in bullet text or headings.** Use a comma `,` instead. This applies everywhere inside `\item` bodies and `\textbf{}` headings. The only permitted use of `--` is in date ranges (e.g. `03/2024 -- Present`) and patent entries, which are copied verbatim from the template.

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

## Archetype Detection (MANDATORY — determines Header lines 2 & 3)

Detect the **primary archetype** of the JD before generating the header. Apply the **first matching rule**:

| Archetype | JD signals |
|-----------|-----------|
| **Architect** | "Solution Architect", "Enterprise Architect", "Principal Architect", "Systems Architect", "Technical Architect", "Architecture Lead", "Chief Architect" |
| **Manager / EM** | "Engineering Manager", "Head of Engineering", "VP Engineering", "Director of Engineering", "Software Manager" |
| **Project / Portfolio** | "Project Manager", "Portfolio Manager", "Program Manager", "PMO", "SW Portfolio", "Delivery Manager", "TPM" |

---

## CV Tailoring Rules (MANDATORY — apply to every build)

These rules are based on the actual structure of both CV templates. Read the selected template carefully before applying changes. **NEVER invent new projects, companies, or metrics. Only reframe real experience using JD vocabulary.**

---

### Section 0 — Header (Name + Title + Certifications)

**Line 1:** Name — copy verbatim from template: `ELAM PARITHI BALASUBRAMANIAN`

**Line 2 — Target Position Title:** Adapt based on archetype:

| Archetype | EN Header Line 2 | DE Header Line 2 |
|-----------|-----------------|-----------------|
| **Architect** | `Lead Architect \textbar{} Software Manager (EM)` | `Lead Architekt \textbar{} Software Manager (EM)` |
| **Manager / EM** | `Software Manager (EM) \textbar{} Lead Architect` | `Software Manager (EM) \textbar{} Lead Architekt` |
| **Project / Portfolio** | `SW Portfolio Manager \textbar{} Lead Architect` | `SW Portfolio Manager \textbar{} Lead Architekt` |

**Line 3 — Certifications:** Adapt based on archetype:

| Archetype | Line 3 (both EN and DE) |
|-----------|------------------------|
| **Architect** | `Azure Architect Certified Expert \textbar{} M.B.A. \textbar{} PMP` |
| **Manager / EM** | `M.B.A. \textbar{} PMP \textbar{} Azure Architect Certified Expert` |
| **Project / Portfolio** | `M.B.A. \textbar{} PMP \textbar{} Azure Architect Certified Expert` |

**Spacing (copy exactly from template):**
```latex
\textcolor{zfblue}{\large\bfseries{ELAM PARITHI BALASUBRAMANIAN}}\\[3pt]
{\textbf{<Line 2>}}\\[3pt]
{\textbf{<Line 3>}}\\[3pt]
```
Contact lines and `\vspace{-22pt}` after the header block: copy verbatim from template, no changes.

---

### Section 1 — Professional Summary

**Section heading:**
- EN template: `PROFESSIONAL SUMMARY`
- DE template: `PROFIL`

**Structure — exactly 2 focused paragraphs (not bullet points):**

Each paragraph must:
- Be **2–3 lines** long (not shorter, not longer)
- Directly mirror a key theme from the JD (use the JD's exact noun phrases)
- Contain **2–4 bolded words or short phrases** matching JD terminology — use `\textbf{}` in LaTeX
- Stay grounded in the candidate's real experience (10+ years, ZF, portfolio/architecture/AI/Distributed System Architecture)

**Paragraph mapping:**
- **Paragraph 1** → the primary technical/architectural dimension of the JD (e.g. Enterprise Architecture, AI Platform, Program Governance, Cloud Strategy)
- **Paragraph 2** → the delivery/leadership/people dimension of the JD (e.g. cross-functional teams, stakeholder management, transformation, organisational scale)

**Separator between paragraphs:** `\\` (line break in LaTeX), no blank line.

**What NOT to do:** Do not keep the generic summary from the template. Every word must earn its place by mirroring the JD.

**Spacing:** No `\vspace` before or after — the `\titlespacing*{\section}` handles it (8pt above, 4pt below rule line).

---

### Section 2 — Key Achievements

**Section heading:**
- EN template: `KEY ACHIEVEMENTS`
- DE template: `HERAUSRAGENDE ERFOLGE`

**Structure — exactly 4 bullet points:**

Each bullet must:
1. Start with a **bold heading** (`\textbf{JD Term:}`) taken directly from the JD's requirements, responsibilities, or key skills section
2. Be **strictly under 2 lines — HARD LIMIT** (target 1.5 lines; range 1.5–1.9; if it runs to 2+ lines, compress the sentence — drop adjectives, merge KPIs, cut sub-clauses)
3. Contain a **quantified proof point** from the real CV — read metrics from `cv.md`, never invent
4. **NOT duplicate a bullet from the Professional Experience section** — Key Achievements must synthesise across the candidate's full career arc and personality: combine a management dimension + a technical dimension + a KPI into a single compressed statement that could NOT be lifted from a single role bullet
5. Cover **4 distinct JD requirements** — no two bullets may address the same JD theme

**Selection logic:**
- Read all JD requirements → rank by prominence (mentioned first, mentioned multiple times, in "must have" section)
- For each of the top 4 JD themes → synthesise a cross-role achievement that demonstrates breadth (e.g. combines ZF Portfolio + ZF TPM + ZF Lead Architect evidence into one condensed statement)
- Rewrite the heading using JD vocabulary, keep the metrics from `cv.md`

**LaTeX pattern (same for both templates):**
```latex
\begin{itemize}
    \item \textbf{Heading:} Body text body text body text body text body text body
    text continues on second line with KPI.
    \item \textbf{Heading:} ...
\end{itemize}
```

**Spacing after section:** controlled by `\titlespacing*`, no manual `\vspace` needed.

---

### Section 3 — Core Competencies

**Section heading:**
- EN template: `CORE COMPETENCIES`
- DE template: `KERNDISZIPLINEN`

**Structure — bold-headed category lines, `\\[2pt]` between each:**
```latex
\textbf{Category:} term1, term2, term3, ...\\[2pt]
```

**Rules:**

1. **Keep less than 8 lines total** — consolidate categories aggressively if needed; never exceed 8 lines
2. **Rename category headings** to use JD's exact grouping language where possible
3. **Reorder categories** — most JD-relevant category must appear first
4. **Within each category**, move JD-matching terms to the front of the comma list
5. **Optionally add JD-relevant terms** the candidate genuinely has but that are not in the template — only do this if there are spare lines within the 8-line cap; 2–3 extras is a good target but not required; insert at the front of the relevant category
6. **Do not add terms the candidate does not have**
7. **Always keep the Languages line last**, exactly as in the template:
   - EN: `\textbf{Languages:} German - B2 (berufspraktisch) \textbar{} English - fluent \textbar{} Tamil - native speaker`
   - DE: `\textbf{Sprachen:} Deutsch - B2 (berufspraktisch) \textbar{} Englisch - fließend \textbar{} Tamil - Muttersprache`
8. If a category is entirely irrelevant to the JD, merge it into the most relevant remaining category rather than remove it

**Spacing:** `\\[2pt]` between lines (already in template) — do not change this.

---

### Section 4 — Professional Experience

**Section heading:**
- EN template: `PROFESSIONAL EXPERIENCE`
- DE template: `BERUFSERFAHRUNG`

**Overall structure (copy exactly from template):**
```latex
\textbf{ZF Friedrichshafen AG} \hfill \textbf{05/2018 -- Present}\\   % EN
\textbf{ZF Friedrichshafen AG} \hfill \textbf{05/2018 -- Heute}\\     % DE
\textit{Friedrichshafen, Germany}
\vspace{3pt}
```

**ZF sub-role header format (copy exactly from template):**
```latex
\textbf{\textit{<Role Title>}} \hfill \textit{<dates>}
\vspace{1pt}
```
**Role titles: use the archetype-specific title from the F2 table below** (NOT the dual-title form from `cv.md`). Dates and locations are always verbatim from the template.

#### ZF Sub-Roles — Bullet Rules

**A. Select exactly 4 bullets per sub-role from the 6 available in `cv.md`** (do NOT use fewer than 4, do NOT use more than 4):

**Selection logic — score each of the 6 bullets against the JD, then keep the top 4:**
1. **Primary filter — archetype alignment:** Bullets that directly address the JD's core archetype (architecture decisions, delivery governance, product ownership, etc.) score highest
2. **Secondary filter — JD keyword density:** Prefer bullets whose underlying facts use vocabulary closest to the JD's requirements and responsibilities sections
3. **Tertiary filter — metric strength:** When two bullets are otherwise equal, prefer the one with the stronger or more specific quantified outcome
4. **Diversity rule:** The 4 selected bullets must cover at least 3 distinct JD themes — do not pick 4 bullets that all address the same dimension (e.g. 4 architecture bullets when the JD also asks for delivery and stakeholder skills)
5. **Drop rule:** Drop the 2 bullets whose themes are least represented in the JD, or that duplicate a stronger bullet already selected

**B. Each bullet must be strictly under 2 lines — HARD LIMIT (prevents 3-page CV):**
- Target: 1.5 lines. Acceptable range: 1.5–1.9 lines. Never 2 full lines or more.
- If a bullet runs to 2+ lines, shorten it — cut adjectives, compress the KPI list, drop redundant clauses.
- Sentence structure: `\textbf{Heading:} [Action verb] [what was done]; [KPI].` — one tight sentence, no sub-clauses.

**C. Bold heading on every bullet (MANDATORY for both templates):**
- `\textbf{<JD-aligned term>:}` — taken directly from the JD's requirements or responsibilities
- Different sub-roles can reuse the same heading if the theme spans the career — this signals depth

**D. Align bullets to target role:**
- Reframe sentence openings using JD vocabulary — do NOT change underlying facts, metrics, or project scope
- For bullets loosely connected to the JD: replace only the **heading** with a more relevant JD term and rephrase the sentence opening

**E. Do NOT invent projects or roles:**
- All companies, role titles, dates, locations must match the template exactly
- You may only change: bullet headings, sentence framing, and vocabulary — not the facts

**F. ZF sub-role ordering:** Keep reverse chronological. Never reorder.

**F2. ZF Role titles — adapt ALL 4 roles based on archetype:**

| Archetype | Role 1 title | Role 2 title | Role 3 title | Role 4 title |
|-----------|-------------|-------------|-------------|-------------|
| **Architect** | `Lead Architect -- Data Analytics / AI, Portfolio Management, and Strategy` | `Staff Engineer -- Product and Program Management` | `Lead Architect -- Software \& System, Autonomous Mobility Systems` | `Algorithm Engineer -- Machine Learning \& Autonomous Driving` |
| **Manager / EM** | `SW Portfolio Manager \& Lead Architect -- Data Analytics / AI, Portfolio Management, and Strategy` | `Technical Program Manager -- Product and Program Management` | `Product Manager \& Lead Architect -- Software \& System, Autonomous Mobility Systems` | `Algorithm Engineer (Product Owner) -- Machine Learning \& Autonomous Driving` |
| **Project / Portfolio** | `SW Portfolio Manager \& Lead Architect -- Data Analytics / AI, Portfolio Management, and Strategy` | `Technical Program Manager -- Product and Program Management` | `Product Manager \& Lead Architect -- Software \& System, Autonomous Mobility Systems` | `Algorithm Engineer (Product Owner) -- Machine Learning \& Autonomous Driving` |

Dates for all ZF roles are always verbatim: Role 1: `03/2024 -- Present`, Role 2: `03/2023 -- 02/2024`, Role 3: `05/2020 -- 02/2023`, Role 4: `05/2018 -- 04/2020`. Locations are always verbatim from the template.

**G. Spacing between sub-roles (copy exactly from template):**
```latex
\end{itemize}
\vspace{6pt}
```

#### Older Companies — Bullet Rules

**Zenuity, TAMA, Larsen & Toubro: exactly 1 bullet each.**

Use `\jobentry{}{}{}{}` macro (copy verbatim from template):
```latex
% EN
\jobentry{Zenuity GmbH}{03/2017 -- 04/2018}{Acquired by Qualcomm, Machine Learning \& Sensor Fusion Engineer (Work Study)}{Munich, Germany}
% DE
\jobentry{Zenuity GmbH}{03/2017 -- 04/2018}{Übernommen durch Qualcomm; Machine‑Learning‑ \& Sensorfusionsingenieur (Werkstudent)}{Munich, Germany}
```

The single bullet must:
- Start with `\textbf{<most relevant JD dimension>:}` — pick the single most relevant heading for the role
- Be strictly under 2 lines (target 1.5 lines) — same hard limit as ZF bullets
- Use real facts from `cv.md` — no invented metrics

**Spacing after each older company (copy exactly from template):**
```latex
\end{itemize}
\vspace{6pt}
```
**No `\vspace{6pt}` after the last company (Larsen & Toubro)** — the section spacing handles it.

---

### Section 5 — Education

**Section heading:**
- EN template: `EDUCATION`
- DE template: `AUSBILDUNG`

**Copy verbatim from template — no changes:**
```latex
\section{EDUCATION}   % or AUSBILDUNG

\eduentry{Kempten Business School}{03/2023 -- 08/2024}{Master of Business Administration (MBA), CGPA: 1,4}{Kempten, Germany}\\
{Incl. Executive Study -- \textbf{Graduate School of Business, University of Cape Town}, South Africa}\\ [6pt]
\eduentry{Technische Hochschule Ingolstadt}{03/2016 -- 03/2018}{Master of Engineering (M.E.), International Automotive Engineering, CGPA: 1,5}{Ingolstadt, Germany}\\ [6pt]
\eduentry{Coimbatore Institute of Technology}{06/2010 -- 04/2014}{Bachelor of Engineering (B.E.), Mechanical Engineering, CGPA: 9,1/10}{Chennai, India}\\
\vspace{-10pt}
```

---

### Section 6 — Patents

**Section heading:**
- EN template: `PATENTS`
- DE template: `PATENTE`

**Copy verbatim from template — no changes.** (EN and DE have different patent description text — use the matching template's text.)

---

### Section 7 — Certifications & Research

**Section heading:**
- EN template: `CERTIFICATIONS \& RESEARCH`
- DE template: `ZERTIFIKATE \& FORSCHUNG`

**Copy verbatim from template — no changes.** (Column labels differ between EN and DE — use the matching template's labels.)

**Closing line (copy verbatim from template, no changes):**
```latex
\vspace{6pt}
\noindent Ravensburg, \today \hfill Elam Parithi Balasubramanian
```

---

### Tailoring checklist (verify before compiling)

- [ ] Header line 2 matches archetype (Architect / Manager / Project-Portfolio)
- [ ] Header line 3 certifications match archetype
- [ ] Summary has exactly 2 paragraphs, each 2–3 lines, with bolded JD-matching terms
- [ ] Key Achievements has exactly 4 bullets, each strictly under 2 lines (target 1.5), bold heading from JD vocabulary
- [ ] Key Achievements bullets do NOT duplicate Professional Experience bullets
- [ ] The 4 achievement headings cover 4 distinct JD requirements
- [ ] Core Competencies is under 8 lines total; most JD-relevant category first
- [ ] Core Competencies includes extra JD-relevant terms only if space allows (optional, not required)
- [ ] Every experience bullet has a bold heading using JD terminology
- [ ] All 4 ZF roles have exactly 4 bullets each (selected from 6 in `cv.md`); every bullet is strictly under 2 lines
- [ ] All 4 ZF role titles match the archetype from the F2 table (Architect vs Manager/Portfolio)
- [ ] Zenuity, TAMA, L&T each have exactly 1 bullet
- [ ] All `\vspace{6pt}` between sub-roles are present
- [ ] `\vspace{-10pt}` after Education is present
- [ ] No invented metrics, companies, or projects
- [ ] Education, Patents, Certifications unchanged from template

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

Reformulate real experience using the JD's exact vocabulary. Examples by archetype:

**AI / LLMOps / Agentic:**
- JD says "RAG pipelines" and CV says "LLM workflows with retrieval" → "RAG pipeline design and LLM orchestration workflows"
- JD says "MLOps" and CV says "observability, evals, error handling" → "MLOps and observability: evals, error handling, cost monitoring"

**Solution / Systems Architect:**
- JD says "Enterprise Architecture" and CV says "system architecture" → "Enterprise Architecture across perception, planning, and platform subsystems"
- JD says "MBSE" and CV says "model-based development" → "Model-Based Systems Engineering (MBSE) for autonomy stack architecture"

**Program Manager / TPM:**
- JD says "release train" and CV says "coordinated releases across teams" → "Agile Release Train coordination across 3 distributed sites"
- JD says "RAID management" and CV says "risk and issue tracking" → "RAID management and SteerCo reporting for SAE L4 program"

**Product Manager:**
- JD says "product discovery" and CV says "requirements gathering" → "Product discovery: user interviews, backlog synthesis, and hypothesis-driven prioritisation"
- JD says "go-to-market" and CV says "product launch" → "Go-to-market coordination across engineering, sales, and customer success"

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
