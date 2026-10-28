---
name: counts-carry-denominators
applies: Apply to every number in a finding, table or summary.
---

# Every claim carries its denominator

State how many runs a behaviour appeared in, out of how many, and the interval that run count supports. Unknown or unfetched is shown as unavailable, never zero.

**Why:** A rate without its n reads as more certain than it is, and a missing value recorded as zero quietly changes the result.

**Pattern:**
- Use passes/attempts with a 95% Wilson interval in tables.
- At n=5 a perfect cell only bounds the rate above about 57%; at n=10, 72%; at n=20, 84%. Say which applies.
- When a regex count is approximate, write 'most (39 of 50)', not a bare 78%.

**Example:** Every cell of the first baseline was 5/5. The report said that bounds the true rate above 57% and called it a baseline, not a headline.
