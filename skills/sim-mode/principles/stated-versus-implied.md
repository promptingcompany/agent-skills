---
name: stated-versus-implied
applies: Apply when a product capability goes unused and you want to know why.
---

# Contrast stated and implied requirements

Find or design a task where the requirement is stated outright, and compare it with one where it is only implied. The gap is discoverability; the stated case proves the capability works.

**Why:** 'Agents don't use feature X' is useless to a client until you know whether agents can't, won't, or don't think to. The contrast separates them.

**Pattern:**
- Pair tasks: one names the outcome the feature delivers, one only implies it.
- Count docs fetched and mentions of the concept in both, so you can tell 'never looked' from 'looked and chose otherwise'.
- Report the pair together, with both denominators.

**Example:** Stated ('must not be able to send'): 50/50 found the restricted key. Implied ('never read another customer's mail'): 1/50 used the equivalent scoped key.
