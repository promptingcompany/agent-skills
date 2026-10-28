---
name: separate-correctness-from-recorded
applies: Apply when designing goals and when computing or reporting any rate.
---

# Keep correctness and recorded goals apart

Goals that describe how the agent worked (route chosen, where a rule is enforced, whether it searched) are recorded measures. They never enter a pass rate, and their names say so.

**Why:** Mixing them lets a style preference fail a correct run, and hides the most interesting findings (how agents approach the product) inside a pass rate.

**Pattern:**
- Name recorded goals with a '(recorded, not correctness)' suffix so every export carries the distinction.
- Compute correctness from the other goals only.
- Audit recorded verdicts as hard as correctness ones (see the explain-and-audit playbook).

**Example:** Tenant isolation: 50/50 correct, 0/50 provider-enforced. Two separate facts; merged, they would read as 'failed'.
