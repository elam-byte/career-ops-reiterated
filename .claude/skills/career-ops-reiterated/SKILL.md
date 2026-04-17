---
name: career-ops-reiterated
description: AI job search command center -- evaluate offers, generate CVs, scan portals, track applications
user_invocable: true
args: mode
---

# career-ops-reiterated -- Router

## Mode Routing

Determine the mode from `{{mode}}`:

| Input | Mode |
|-------|------|
| (empty / no args) | `discovery` -- Show command menu |
| JD text or URL (no sub-command) | **`auto-pipeline`** |
| `evaluate` | `evaluate` |
| `compare` | `compare` |
| `contact` | `contact` |
| `deep` | `deep` |
| `pdf` | `pdf` |
| `training` | `training` |
| `project` | `project` |
| `tracker` | `tracker` |
| `pipeline` | `pipeline` |
| `apply` | `apply` |
| `scan` | `scan` |
| `batch` | `batch` |
| `coverletter` | `coverletter` |

**Auto-pipeline detection:** If `{{mode}}` is not a known sub-command AND contains JD text (keywords: "responsibilities", "requirements", "qualifications", "about the role", "we're looking for", company name + role) or a URL to a JD, execute `auto-pipeline`.

If `{{mode}}` is not a sub-command AND doesn't look like a JD, show discovery.

---

## Discovery Mode (no arguments)

Show this menu:

```
career-ops-reiterated -- Command Center

Available commands:
  /career-ops-reiterated {JD}        → AUTO-PIPELINE: evaluate + report + PDF + tracker (paste text or URL)
  /career-ops-reiterated pipeline    → Process pending URLs from inbox (data/pipeline.md)
  /career-ops-reiterated evaluate    → Evaluation only A-F (no auto PDF)
  /career-ops-reiterated compare     → Compare and rank multiple offers
  /career-ops-reiterated contact     → LinkedIn outreach: find contacts + draft message
  /career-ops-reiterated deep        → Deep research on a company
  /career-ops-reiterated pdf         → Generate ATS-optimized LaTeX CV PDF
  /career-ops-reiterated training    → Evaluate course/cert against North Star
  /career-ops-reiterated project     → Evaluate portfolio project idea
  /career-ops-reiterated tracker     → Application status overview
  /career-ops-reiterated apply       → Live application assistant (reads form + generates answers)
  /career-ops-reiterated scan        → Scan portals and discover new offers
  /career-ops-reiterated batch        → Batch processing with parallel workers
  /career-ops-reiterated coverletter → Generate cover letter (.docx, EN or DE)

Inbox: add URLs to data/pipeline.md → /career-ops-reiterated pipeline
Or paste a JD directly to run the full pipeline.
```

---

## Context Loading by Mode

After determining the mode, load the necessary files before executing:

### Modes that require `_shared.md` + their mode file:
Read `modes/_shared.md` + `modes/{mode}.md`

Applies to: `auto-pipeline`, `evaluate`, `compare`, `pdf`, `contact`, `apply`, `pipeline`, `scan`, `batch`, `coverletter`

### Standalone modes (only their mode file):
Read `modes/{mode}.md`

Applies to: `tracker`, `deep`, `training`, `project`

### Modes delegated to subagent:
Only `pipeline` (3+ URLs): launch as Agent with the content of `_shared.md` + `modes/{mode}.md` injected into the subagent prompt.

```
Agent(
  subagent_type="general-purpose",
  prompt="[content of modes/_shared.md]\n\n[content of modes/{mode}.md]\n\n[invocation-specific data]",
  description="career-ops-reiterated {mode}"
)
```

**`scan` and `apply` must run directly in the main session — NOT as subagents.** Subagents do not have access to MCP tools (Playwright). Load `_shared.md` + the mode file and execute inline.

Execute the instructions from the loaded mode file.
