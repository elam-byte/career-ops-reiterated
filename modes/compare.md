# Mode: compare — Multi-Offer Comparison

Scoring matrix across 9 weighted dimensions (compensation removed as a scored metric — researched separately in Block D):

| Dimension | Weight | Criteria 1–5 |
|-----------|--------|--------------|
| North Star alignment | 28% | 5=exact target role, 1=unrelated |
| CV match | 18% | 5=90%+ match, 1=<40% match |
| Level (senior+) | 16% | 5=staff+, 4=senior, 3=mid-senior, 2=mid, 1=junior |
| Growth trajectory | 12% | 5=clear path to next level, 1=dead end |
| Remote quality | 6% | 5=full async remote, 1=onsite only |
| Company reputation | 6% | 5=top employer, 1=red flags |
| Tech stack modernity | 5% | 5=cutting-edge AI/ML, 1=legacy |
| Time-to-offer speed | 4% | 5=fast process, 1=6+ months |
| Cultural signals | 5% | 5=builder culture, 1=bureaucratic |

For each offer: score per dimension, weighted total.
Final ranking + recommendation with time-to-offer considerations.

**Compensation column (separate, not scored):**
Research market comp for each role independently (Block D logic from `modes/evaluate.md`).
Add a "Comp suggestion" column to the comparison table.

Ask the user for the offers if not already in context. They can be text, URLs, or references to already-evaluated offers in the tracker.
