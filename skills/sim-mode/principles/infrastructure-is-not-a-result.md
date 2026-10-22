---
name: infrastructure-is-not-a-result
applies: Apply when a run failed before the agent's first action, or the sandbox never became usable.
---

# Infrastructure failures are not results

Rerun it inside its original iteration and exclude the failed attempt from every rate. List it in the report footer.

**Why:** A sandbox that never started says nothing about the agent or the product. Counting it as a failure penalizes whichever configuration was unlucky with capacity or a cold image.

**Pattern:**
- Check `failureDetails.kind` on every non-completed run (`sandbox_provisioning_failed`, snapshot building, provider capacity).
- Rerun in place with the experiment rerun endpoint so the iteration total stays the same; a standalone `tpc sim run` lands outside the iteration.
- Expect a burst of these the first time a new harness is used: its sandbox image builds on demand.

**Example:** Five of 24 runs failed in the first iteration after adding three new harnesses, all with 'snapshot is building'. All five reruns completed.
