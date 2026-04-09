# Mode: tracker — Application Tracker

Read and display `data/applications.jsonl`.

**Primary data source:** `data/applications.jsonl` (JSONL format — one JSON record per line)

**Canonical statuses:**
`Evaluated` → `Applied` → `Responded` → `Interview` → `Offer` / `Rejected` / `Discarded` / `SKIP`

- `Applied` = candidate submitted the application
- `Responded` = a recruiter/company reached out and the candidate replied (inbound)
- `Interview` = active interview process
- `Offer` = offer received
- `Rejected` = rejected by the company
- `Discarded` = candidate or role closed (candidate's choice)
- `SKIP` = does not fit, do not apply

## Display

Show a formatted summary table:

| # | Date | Company | Role | Score | Status | PDF | Comp Suggestion | Notes |
|---|------|---------|------|-------|--------|-----|-----------------|-------|

Also show statistics:
- Total applications
- Breakdown by status
- Average score
- % with PDF generated
- % with report generated
- Top companies by application count

## Updating status

If the user asks to update a status, edit the matching record in `applications.jsonl`:
- Find by id, company, or role
- Update the `status` field
- Add/update `notes` if the user provides context
- Never create a duplicate entry — always update the existing one

## Dashboard

For a visual view, run:
```bash
# Web dashboard
cd dashboard && streamlit run app.py

# Terminal dashboard
python dashboard/terminal.py overview
python dashboard/terminal.py apps
```
