---
name: fixtures-must-not-leak
applies: Apply when generating seeded data and writing graders.
---

# Fixtures must not leak the answer

Nothing the agent can read encodes which object is the target: no role words in IDs, filenames, headers or boundaries. The answer key stays out of the sandbox; graders carry only the minimum needed to grade.

**Why:** A leaked role turns a retrieval test into string matching, and it inflates every configuration equally, so the comparison still looks plausible.

**Pattern:**
- Hash readable identifiers from the role, never use the role.
- Grep the generated fixtures for role words before seeding.
- Embed hashes and totals in graders, never the mapping of which object is which.

**Example:** First-draft fixtures used `<target@...>` as a Message-ID and `b-decoy-near-number` as a MIME boundary. Both visible to the agent; both replaced with hashes.
