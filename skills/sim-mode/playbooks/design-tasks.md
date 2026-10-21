# Design tasks

**Write jobs a developer would hand an agent, seed fixtures that cannot leak, and split goals into correctness and recorded before anything is created.**

## Steps

1. **Map the spec.** If the client has a benchmark spec, list its evals and pick the ones an unguided agent run can test. Note which need infrastructure you do not have yet (a receiving service, a public webhook URL) and defer them to a later wave rather than weakening them. Principle: **speak-the-spec**.
2. **Check what exists.** List the product's existing experiments and tasks (`tpc sim experiment list`, `tpc sim task list`) and grep them for other vendors' names before building, so you neither duplicate nor collide with someone else's benchmark.
3. **Write each prompt as a real job.** Product named, outcome stated, connection details in a workspace file, no route, no endpoint, no mention of keys. Principle: **real-jobs-not-setup**.
4. **Plan a stated/implied pair** for any capability you expect agents to miss. Principle: **stated-versus-implied**.
5. **Design fixtures.** Target plus realistic decoys (near-identical identifiers, the right sender in the wrong period, the wrong sender in the right period, a related message with no payload) and routine noise. Hash every readable identifier. Principle: **fixtures-must-not-leak**.
6. **Decide fixture isolation.** For each task, list side effects. Anything with side effects that will run concurrently gets its own fixture per run, or an attribution scheme. Check provider plan limits now; they decide which is possible. Principle: **isolate-shared-fixtures**.
7. **Split goals.** Correctness goals as `script_judge` against state wherever possible; recorded goals named "(recorded, not correctness)"; LLM-judge rubrics that state the pass boundary explicitly. Principle: **separate-correctness-from-recorded**.
8. **Generate specs from one builder.** One script emits every task spec, init-command file and task-only update file per arm, so a grader fix reaches every arm at once.
9. **Hand off to Prove the graders.** Nothing is scored until that playbook passes.

**Reply:** the task list with spec mapping, the stated/implied pairs, fixture isolation decision per task, goals table, and what is deferred to a later wave and why.
