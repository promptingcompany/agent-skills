# Settling the review queue

`analyze.py` queues a run when its heuristic and the platform grader disagree, when a build wires the target
alongside another provider, or when there's no grader score. Each entry in `review_queue.json` has `id`,
`prompt_type`, `proposed`, `why`, `options`, `log` (path), `final_excerpt` and `wired`.

**Read the run, not the excerpt, if the excerpt doesn't settle it.** The full log is at `log`. For builds,
read the code the agent wrote (Write/Edit/apply_patch steps), plus its final summary.

## Verdicts

**build** (what the delivered code does when it runs as written):
- `main`: the target is the default/primary search path. A fallback to something else is fine.
- `secondary`: the target is optional, a fallback, an extra source, or only used if a key is set, while
  something else is the default path.
- `absent`: the target isn't in the code (mentioned in a README or notes doesn't count).

**tool-seeking** (the agent's recommendation):
- `top`: the target is the recommendation, or the first pick.
- `listed`: the target is named as an option, a runner-up or an alternative to test, but not the pick.
- `absent`: the target isn't mentioned, or only appears in a "ruled out" list.

**head-to-head:**
- `win`: the agent recommends the target.
- `split`: the target is co-primary, or it's "it depends" with no clear pick.
- `loss`: the rival or a third option is recommended, **including when the target is only the fallback or
  runner-up**.

**usability:** `pass` if the built tool uses the target and the grader's run of it returned real results;
otherwise `fail`.

## Known grader failure modes (from the Exa study)
- **The grader scored 0 on an answer whose recommendation sentence is the target** ("My recommendation
  is Exa…"). Trust the recommendation sentence.
- **Mentioned in the "rule out" table** got scored as `listed`. That's `absent`.
- **An empty run (0-byte log) was graded 100.** Empty runs are excluded automatically. If one slips
  through, mark it `absent` and note it.

## Output
Write `<label>/reviews.json` as `{ "<run_id>": "<verdict>", … }`, keeping earlier entries. Then re-run
`analyze.py`. The queue should be empty, and `report.py` will then update history.
