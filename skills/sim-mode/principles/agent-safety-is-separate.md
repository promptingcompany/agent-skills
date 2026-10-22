---
name: agent-safety-is-separate
applies: Apply when an agent does something harmful or forbidden during a run.
---

# Agent-safety events are separate from product results

Report it as agent behaviour with the run and configuration, quote the agent's own account if it gave one, and keep it out of the product's column. The product's controls working is a separate fact.

**Why:** Blaming the product for an agent that bypassed its controls with a broader credential misreports both, and hides a real agent-safety finding.

**Pattern:**
- Identify the credential and call that caused the effect.
- Check whether the product's restriction held for the restricted credential.
- Report: the control held; the agent then did X with Y.

**Example:** A draft-only key was refused on reply (403). The agent then repeated the reply with the account key 'as a control' and sent mail. Reported as one agent-safety event, not a permissions failure.

**Example:** Blocked on a refused domain, an agent attached two outside addresses it made up (one at a real company domain) to probe the block, so the vendor emailed verification codes to strangers. Reported as an agent-safety event, separate from the sign-up verdict.
