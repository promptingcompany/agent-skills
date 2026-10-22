---
name: platform-verdict-is-intent
applies: Apply before accepting, reporting or overturning any goal verdict, count or status.
---

# The platform verdict is an intent; provider state is the fact

Check the real state the task touched (sent folder, created objects, keys, files, the response the agent got) before you trust a verdict. A grader message, a run status, or a command's own success line is a claim about the world, not the world.

**Why:** Graders misparse, run statuses lag, and success responses are not proof the object exists. Acting on the claim when the fact is one API call away is the most common way a wrong table ships.

**Pattern:**
- For any verdict you will report, name the provider read that would confirm it, and run it for every failure and a sample of passes.
- When a verdict and the agent's own final message disagree, read the provider. Either can be wrong.
- When verification fails, suspect the observation method (the grader, the parser, the list call) before suspecting the agent.

**Example:** A draft task scored 0 of 2 drafts found. The provider showed both drafts, in thread: the agent had written `{"draft_ids": [...]}` and the grader only read a bare list.
