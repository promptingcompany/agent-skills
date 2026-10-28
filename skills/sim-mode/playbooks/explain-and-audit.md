# Explain and audit

**Audit recorded verdicts, count behaviour across transcripts, and write findings that carry their denominators.**

Correctness rates say whether agents succeeded. The useful findings usually come from how they worked, which lives in recorded goals and transcripts. Both need the same scrutiny as correctness.

## Step 1: Audit recorded verdicts

For every recorded goal, read the runs where its verdict is surprising, in either direction:

- A run that claims to have done the thing the goal checks for ("fetched with an inbox-scoped key") but scored FAIL.
- A cell at 0% or 100% on a recorded goal across many runs: confirm with at least two transcripts that the grader is measuring the behaviour and not an artifact of how it observes it.

Common observation artifacts:

- A grader that intercepts network calls sees every credential the code uses, including one used only for setup (for example minting a scoped key with an account key). Decide which call the goal is about (the read, not the mint) and say in the report which definition the numbers use.
- An LLM judge that applies a stricter boundary than the rubric intended. Quote the judge's reasoning for one PASS and one FAIL and check they follow the rubric.

When the strict verdict is defensible but hides something real, report both: "0/50 enforced purely at the provider; 1/50 used scoped keys (minted at runtime with the account key)".

## Step 2: Count behaviour across transcripts

Turn impressions into denominators. For each task, count across all completed runs:

- Calls to the endpoints that matter (the feature under study, search versus list, delete calls on shared objects).
- Documentation fetched (provider docs domains) per run and per configuration.
- Mentions of the concept without using it ("scoped key", "per-tenant key"), which separates "never heard of it" from "knew and chose not to".
- Probes the agent ran to test its own work (for example a send attempt with a restricted key), and their outcomes.

Use regex over the event stream, then spot-check matches by reading them; regex counts are approximate and the report should say "most (39 of 50)" rather than imply precision it does not have.

## Step 3: Write findings that survive scrutiny

Each finding:

1. States the claim with run counts and the configurations it holds for.
2. Cites the mechanism: what in the transcripts or provider state produces the number.
3. Contrasts with a control where possible (the same capability found 50/50 when the prompt named the outcome, 1/50 when it was implied).
4. Says what it means for the client in one sentence, and how to test a fix (rerun the same task after the change).

Cut anything with no observed impact. A provable defect that never affected a run goes in a separate, labelled static-audit note or nowhere.

## Step 4: Separate agent-safety events from provider results

If an agent does something harmful (sends mail it was told not to, deletes shared work), report it as an agent behaviour with the run and configuration, quote the agent's own account if it flagged the mistake, and keep it out of the provider's column. The provider's permissions working is a separate fact from an agent choosing to bypass them with a broader credential.
