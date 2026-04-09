# Mode: deep — Company Research

Generates a structured research brief for the evaluated company and role. Adapts axes based on the detected archetype (from `_shared.md`). Personalise each section with the specific context of the role.

---

## Common axes (all archetypes)

### 1. Company overview
- What does the company actually do? (product, customers, revenue model)
- Size, stage (startup / scale-up / enterprise / public)
- Funding, ownership, recent M&A
- Key leadership — CEO, CTO, hiring manager if known

### 2. Recent moves (last 6 months)
- Relevant hires or departures
- Acquisitions or partnerships
- Product launches, pivots, or restructuring
- Funding rounds or financial signals

### 3. Culture & ways of working
- Remote-first or office-first?
- How do they ship? (cadence, process)
- Glassdoor / Blind reviews — what do employees say?
- Known for: bureaucracy / builder culture / process-heavy / fast-moving?

### 4. Competitors and market position
- Who are their main competitors?
- What is their moat / differentiator?
- Market trends affecting this role?

### 5. Candidate angle
Read `cv.md` and `config/profile.yml` for Elam's specific experience, then answer:
- What unique value does Elam bring to this team?
- Which projects or achievements are most relevant?
- What story should he tell in the interview?
- Any potential concerns to pre-empt?

---

## Archetype-specific axes

Read the detected archetype from `_shared.md` and add the relevant section below.

### If archetype is AI Platform / LLMOps / Agentic / AI Solutions Architect / AI Forward Deployed / AI Transformation / Technical AI PM:

**AI & Technology**
- Which products / features use AI/ML?
- What is their AI stack? (models, infra, tooling)
- Engineering blog, papers, or talks on AI?
- Are they building in-house or wrapping third-party models?
- Known reliability, cost, or latency challenges?

### If archetype is Program Manager / Technical Program Manager / Project Manager:

**Delivery & Governance**
- How do they structure program delivery? (SAFe, Scrum, waterfall, hybrid?)
- Do they have a PMO? How formal is it?
- What does a typical program look like in scope and duration?
- Known delivery challenges — late programs, scope creep, org friction?
- How do they handle cross-functional dependencies?

### If archetype is Product Manager / Technical Product Manager:

**Product & Roadmap**
- What does their product development lifecycle look like?
- How do they do discovery — user research, data-driven, exec-driven?
- Do PMs own the roadmap or does engineering / leadership drive it?
- Known product challenges — retention, monetisation, technical debt?
- How close are PMs to customers?

### If archetype is Solution Architect / Systems Architect:

**Architecture & Technical Governance**
- What is their current architecture? (monolith, microservices, event-driven?)
- Cloud strategy — Azure, AWS, GCP, hybrid, on-prem?
- Known architectural debt or migration programs underway?
- How are architecture decisions made — central CoE, embedded, ad-hoc?
- Compliance and safety requirements (ASPICE, ISO 26262, SOC2, GDPR)?
- Standards and tooling — MBSE, ArchiMate, EA tools?
