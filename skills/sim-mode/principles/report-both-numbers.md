---
name: report-both-numbers
applies: Apply whenever triage changes any verdict.
---

# Keep the platform number and the adjusted number side by side, internally

Record as-scored (what the platform recorded) next to adjusted (after triage) in the results file and the internal dev-feedback note, with the reason for every difference. The client report shows only the verified, adjusted result.

**Why:** Silently replacing the platform's number makes the work unauditable for your own team: anyone who opens the platform sees different figures. Putting the instrument's mistakes in the client report makes it about you instead of their product. Keep the audit trail internal and the client page clean.

**Pattern:**
- Keep an adjusted-runs list: run ID, class, one-line evidence.
- Put as-scored and adjusted columns in the internal results table wherever they differ.
- Note in the dev-feedback file that the platform still shows the original verdict, and why.

**Example:** Draft task: 40/50 as scored, 46/50 adjusted. The internal results file names the six contaminated runs; the client report says 46/50.
