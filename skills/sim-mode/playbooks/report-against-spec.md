# Report against the spec

**Map to the client spec, report in its shapes, answer its open questions, and publish only numbers you counted.**

When the client already has a benchmark specification (a scorecard, an eval protocol, a methods document), the report speaks its language. Read the spec first, end to end, including collapsed sections and sub-pages, and save a local copy so it never has to be re-read through a browser.

## Step 1: Map tasks to the spec's evals

One table: task, the spec's eval and test it corresponds to, what is the same, what is deliberately different. Typical differences worth stating:

- Guided (spec supplies references, fixed text, a mandated route) versus unguided (a real job, the agent picks its route).
- Corpus size and shape.
- Measures the spec requires that this run did not capture (request counts, latency). Show them as unavailable, never zero.
- Human involvement: say explicitly that runs were unassisted if they were.

## Step 2: Results tables in the spec's shape

Default shape when the spec does not say otherwise (it matches common provider-benchmark scorecards):

- One table per eval, one row per configuration.
- Correct as passes/attempts (adjusted), with a 95% Wilson interval.
- Median and IQR of time among passing runs only; failures and timeouts are counted beside, never averaged in.
- Recorded measures in their own columns, labelled as recorded.
- As-scored versus adjusted where triage changed anything, with a note under the table naming why.
- Cost per cell.
- No weighted overall score, no winner from small timing differences, no averaging away a safety or permission breach.

State the run counts and what they bound: at n=5 a perfect cell bounds the true rate above about 57%, at n=10 above about 72%, at n=20 above about 84%.

## Step 3: What the run answers on the spec's open list

If the spec or its findings log has open questions, list the ones this run answered and how (for example "incoming timestamp equals the original Date: functionally verified on 32 delivered messages"). This is often the most valuable section for the client's engineers.

## Step 4: Capability matrix with evidence status

One row per capability, one column per provider. Label support as native, custom code, separate service, partial, unsupported or not verified, and evidence status separately: documented, functionally verified, measured repeatedly. Only mark something verified if this experiment exercised it. Keep competitor strengths in the table.

## Step 5: Limits and next steps

Name the limits that affect interpretation: single provider (no head-to-head claim), shared fixtures, a recorded-goal definition that is stricter than it looks, run counts. Then the concrete next runs that remove each limit.

## Step 6: Publish

- Lead with the finding in two sentences, then four headline numbers, then the tables.
- Generate tables from the summary data, never by hand.
- Check every number in the prose against the counted evidence before publishing; tighten wording where a count is approximate.
- Keep client names and data out of anything public; the report itself is shared privately with the client.
