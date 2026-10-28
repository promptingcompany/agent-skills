---
name: widen-before-deepen
applies: Apply when deciding what to run after a first baseline.
---

# Widen across configurations before deepening runs

Add harness and model configurations chosen for a stated reason before adding repetitions to the same two. Include the same model in a different harness.

**Why:** Two configurations cannot tell a product property from a model quirk. A finding that holds across vendors, tiers and harnesses is a finding about the product.

**Pattern:**
- Use harness/model pairs already running cleanly elsewhere on the platform.
- Pick for coverage: newest flagship, cheaper tier, another vendor's harness, an open-weight model, same-model-different-harness.
- Then raise n on the cells that will carry a published comparison.

**Example:** Eight configurations showed the discovery gap in every one; with two it could have been a model habit.
