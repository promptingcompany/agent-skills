---
name: prove-the-instrument
applies: Apply before the first scored run of any task, and again after any grader change.
---

# Prove the instrument before you measure with it

Every grader passes a correct reference solution, fails a realistic broken one, classifies a plausible alternative correctly, and fails an empty run, all against the live fixtures the agents will see.

**Why:** A grader that has only ever graded agent output is unproven: you cannot tell its bugs from the agents' mistakes, and every number it produces inherits that doubt.

**Pattern:**
- Write the four references (correct, broken, alternative, empty) per task before creating it on the platform.
- Run each goal locally against each reference; every mismatch is a grader fix.
- Then run one unscored validation run per task per environment and read every verdict against its transcript before the first scored iteration.

**Example:** A negative check ("no decoy cited") passed on an empty output. The empty reference caught it before any agent run did.

**Example:** A discovery grader looked for a product's package name in the agent's code. Three versions in a row were wrong: the bare word matched files the agent named after the product; a quote-tolerant pattern matched a script called `create-<package>`; a pattern with literal quotes broke the shell line the grader was injected with. Prove a code-marker check against the agent's own naming (a file and a script named after the product, with no import) as well as against a real import and dependency, before any run counts.
