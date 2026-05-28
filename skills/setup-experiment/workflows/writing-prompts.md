---
name: writing-prompts
description: Guidelines and examples for writing task prompts and goal prompts when drafting `task.json` files in the Setup Experiment flow.
---

# Writing Task Prompts and Goal Prompts

Reference this file when drafting the `prompt` field on a task and the `description` field on each goal in `task.json` (see Step B2 in [`setup-experiment.md`](setup-experiment.md)).

---

## Task prompts

The `prompt` field is the instruction the agent receives at the start of the run. It defines the scenario in one self-contained block.

### Rules

1. **State intent, not implementation.** Write what the user wants accomplished, not which SDKs, functions, or endpoints to call. Let the agent discover the right path from the docs.
2. **Self-contained — no shared context across tasks.** Each task runs in a fresh agent session. Don't reference "the API from Task 1" or "what you built earlier." If a multi-step flow matters, fold it into one task with a richer single prompt.
3. **Don't pin implementation details.** Avoid specific package names, function names, versions, or endpoints unless a real user would naturally include them. "I'm on Node 18" is fine; "use v3.2.1 of the SDK" is not.
4. **One ask per task.** Single, focused goal. Compound prompts ("build X, deploy Y, and configure Z") read like specs and pollute the signal.
5. **Write like a junior dev asking for help.** 1–3 conversational sentences, optionally with a small snippet showing where they're stuck. If it reads like internal documentation, rewrite.

### Examples

#### Good

**Example 1 —**

```
I'm building a signup flow in my Node app. When someone signs up, I want
to send them a welcome email. I have my API key set in RESEND_API_KEY.
Wire it up.
```

Why it works: states the user's intent (welcome email on signup), gives realistic context (Node, API key in env), doesn't name a specific function or package. A junior dev would plausibly write this.

---

**Example 2 —**

```
I want Claude to be able to look up customer info from our Postgres
database when I ask. Set it up so I can ask "what's customer 123's last
order?" and get a real answer.
```

Why it works: real user framing, concrete observable check built into the prompt, doesn't prescribe MCP primitives or schema details.

---

#### Bad

**Example 1 —**

```
Install resend-node@4.0 via npm. Initialize a Resend client using
process.env.RESEND_API_KEY. Call resend.emails.send() with from, to,
subject, and html parameters. Log the response.
```

What's wrong: prescribes package name, version, function, and every parameter. Tests instruction-following, not whether the agent can use Resend. An agent that picks a valid alternative path would unfairly fail.

---

**Example 2 —**

```
Using the email setup from the previous task, add a follow-up email that
sends 24 hours after signup.
```

What's wrong: depends on state from another task. Breaks parallel execution, makes failures cascade, can't be run independently or shuffled. Rewrite as a standalone "build a delayed follow-up email flow" task.

---

## Goal prompts

Each goal's `description` field tells the LLM judge what a passing run looks like. It must be observable from the run artifacts — not internal agent state.

### Rules

1. **Describe an observable outcome.** The judge sees only run artifacts (code produced, command outputs, files written, API responses). Goals must be checkable from those — never from what the agent "understood" or "intended."
2. **Tie to user intent, not implementation path.** "An email is delivered" beats "the agent called the right SDK function." Multiple valid implementations should all pass.
3. **Be specific enough to be falsifiable.** "Works correctly" or "follows best practices" can't be judged. Concrete commands, expected outputs, or testable assertions can.
4. **One condition per goal.** Compound goals ("does X AND Y AND Z") collapse into a single pass/fail and hide which part actually failed. Split them.
5. **Stand alone alongside the task.** No references to "the system from earlier" or "the API key we discussed." Same independence rule as task prompts.

### Examples

#### Good

**Example 1 —**

```
The agent's run produces an HTTP 200 response from the email-send call,
and the response body contains a non-empty message ID.
```

Why it works: observable from run artifacts (the HTTP response is in the logs), outcome-based, falsifiable, doesn't care which SDK or HTTP client was used.

---

**Example 2 —**

```
Running `wrangler dev` and curling the resulting localhost URL returns
200 with body "hello world" (case-insensitive, trimmed).
```

Why it works: concrete commands and expected output, allows whitespace/case flex, doesn't constrain file structure or framework choice.

---

#### Bad

**Example 1 —**

```
The agent correctly understands that it should use the Resend SDK rather
than raw fetch calls.
```

What's wrong: "correctly understands" isn't observable. Two equivalent implementations should both pass — what the agent "understood" is irrelevant if the email gets sent.

---

**Example 2 —**

```
The code installs the SDK, initializes the client with the right key,
sends an email with all required fields, handles errors, and logs the
result to the console.
```

What's wrong: five conditions in one goal. If any fails, the whole goal fails — and you can't tell which. Split into separate goals, or collapse into one outcome-based goal: "an email is delivered."

---

## Quick checklist

Before calling `tpc sim task create`, confirm:

- [ ] Task prompt states user intent, not implementation steps
- [ ] Task prompt is self-contained — no reference to other tasks or prior runs
- [ ] Each goal description is observable from run artifacts (not internal agent state)
- [ ] Each goal describes one outcome-based, falsifiable condition
