---
name: every-failure-has-a-cause
applies: Apply to every run with a failing correctness goal, before computing any rate for a report.
---

# Every failure has a named cause and evidence

Classify each failure as exactly one of: infrastructure, grader defect, fixture contamination, genuine agent failure. Attach the transcript line or provider record that proves the class.

**Why:** Unclassified failures make every rate ambiguous. Readers assume all failures are the agent's, which overstates agent weakness when the instrument broke, and understates it when a fix is applied without evidence.

**Pattern:**
- Open the transcript of every failing run. Find the moment it went wrong.
- Match the signature to a class (see the run-and-triage playbook's table).
- Write one line per failure: run, class, evidence. Never adjust a number without one.

**Example:** Ten draft failures split into 4 genuine (wrong vendor twice, an ignored field, one real send), and 6 contaminated by that one send landing in a shared inbox.
