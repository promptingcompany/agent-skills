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

In the client report, name only limits of scope that affect interpretation: single provider (no head-to-head claim), run counts, what was not tested. Instrument and fixture problems go in the internal dev-feedback note (Step 6).

## Step 6: Order findings by who acts

Sort every finding into blocks by owner, and by insight within each block. Score each candidate finding 1 to 5 on
insight (does it tell the reader something they could not guess) and actionability (a concrete change, an owner, a
test) before writing.

1. What the client should change. Insightful findings with a clear owner and a test.
2. What the client can now claim. Verified capabilities, each with its bounds.
3. Notes. One line each for findings that are neither insightful nor actionable. Cut the rest.

Keep your own side out of the client report entirely: platform failures and limits (sandbox provisioning, metrics the
platform does not capture), grader and fixture bugs, verdict adjustments, and benchmark-design fixes. Write those to a
separate internal dev-feedback note, one item each with what happened, how often, impact and proposed fix, split into
platform work and benchmark-design work. Platform items also go onto the team's single living tracker issue for agent-simulation
platform feedback, one checklist item each, rather than one ticket per gap. The client report then states only verified results. If a platform verdict
differs from the triaged one, that difference lives in the dev note and the results file, not the client page.

Each finding in blocks 1 and 2 opens with the one sentence a reader should remember, then **Evidence.** (counts),
**Change.** (owner) and **Test.** (what would show the change worked). When two causes are not yet separated, name
both and the test that separates them; never call a fix obvious. Correctness totals that are at ceiling go in a small
stat row, not the lead. Every tile says what it counts ("runs correct"), and a behaviour count never sits beside pass
rates in the same style: mark it as a behaviour so "1/50" cannot read as a failure rate. Per-configuration tables go to the evidence section at the end, as one compact matrix.

Before publishing, hand the findings and evidence to a second strong model for an independent insight and
actionability ranking and a list of overstated claims, then reconcile.

## Step 7: Publish

- Lead with the finding in two to four sentences. Then the blocks from Step 6. Tables last.
- Generate tables from the summary data, never by hand.
- End with an appendix generated from the specs actually created on the platform, never retyped: each task's prompt
  verbatim, its starting state in plain words, its goals with type and pass rule; the agent configurations (harness,
  model, runs per task); and the run settings (iterations, resets between them, judge model, how time is counted).
  Describe setup in plain words rather than copying internal init labels.
  For any stated/implied pair, highlight the sentence in each prompt that sets the requirement and add one line under
  it saying whether the requirement is stated or implied, with that task's result. Link the finding to it. Open the
  appendix with a clear visual break and a label so readers know the report has ended.
- Check every number in the prose against the counted evidence before publishing; tighten wording where a count is approximate.
- Never cite the spec's internal codes alone (scope or scorecard versions, eval numbers, open-item IDs). Name the
  benchmark by its title and pair each code with what it means, every time. A reader outside the client's team cannot
  look them up.
- Keep client names and data out of anything public; the report itself is shared privately with the client.
- For a shareable copy, wrap the page into a full HTML document (doctype, charset, viewport, `noindex`), upload it to your
  static asset host under an unguessable path, then fetch it and compare bytes before sending the link.
