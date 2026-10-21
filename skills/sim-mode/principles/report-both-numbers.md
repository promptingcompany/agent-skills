---
name: report-both-numbers
applies: Apply whenever triage changes any verdict.
---

# Report the platform number and the adjusted number side by side

Show as-scored (what the platform recorded) next to adjusted (after triage), and name the reason for every difference under the table.

**Why:** Silently replacing the platform's number makes the report unauditable: anyone who opens the platform sees different figures and loses trust in both. Showing both makes the triage itself the evidence.

**Pattern:**
- Keep an adjusted-runs list: run ID, class, one-line evidence.
- Put an 'as scored' column in the results table wherever it differs.
- Say that the platform still shows the original verdict.

**Example:** Draft task: 40/50 as scored, 46/50 adjusted, with the six contaminated runs named under the table.
