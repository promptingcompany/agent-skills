---
name: isolate-shared-fixtures
applies: Apply when a task has side effects (send, delete, create credentials) and runs in parallel with others.
---

# Concurrent runs must not share mutable fixtures

Give each run its own fixture, or make every side effect attributable to exactly one run. Reset fixtures between iterations with a script that only touches objects created after the experiment started.

**Why:** One agent's side effect lands in every concurrent run's window and fails them all. Agents also clean up: they delete objects they think are stray, including other runs' work.

**Pattern:**
- List each task's side effects before running. Any that a grader checks by time window is a contamination risk.
- Prefer one fixture per run. If plan limits forbid it, attribute side effects by run (own sender, own object prefix) and document the residual risk.
- The reset script logs every deletion by name and creation time and never deletes pre-existing objects.
- Select what to delete by content, never by a time cutoff alone: keep an explicit list of fixture objects (subjects,
  IDs) and delete only what is provably agent-made (sent by the agent, created by the run). A cutoff set before the
  fixture was seeded wipes the fixture. Then run the reset once on the clean fixture and confirm nothing was deleted.
- Check that the listing you clean from returns everything: some APIs omit items from a list view (sent-only threads,
  for example), so the reset silently misses them.

**Example:** One agent sent a reply as a 'control' test; six other runs open in the same minutes failed 'nothing went out'. 14 of 50 draft runs deleted drafts in the shared inbox.
