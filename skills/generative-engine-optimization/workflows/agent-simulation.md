---
name: agent-simulation
description: >
  Simulates how an AI agent behaves given a system prompt and a task.
  Runs a step-by-step agent loop and provides a debrief with prompt improvement suggestions.

  Trigger when users say: "simulate agent", "run agent loop", "test agent", or "test this prompt".
---

# Agent Simulation

## Overview

Simulate an agent loop step-by-step and debrief what worked, what failed, and how to improve the prompt.

## Prerequisites

- A product name, URL, or description to understand what is being simulated
- A system prompt (paste or describe)
- A user message or task to simulate against

## Required Workflow

**Follow all steps in order.**

---

### Step 1 — Check for existing simulations

Before creating anything, use the CLI to list existing simulation tasks and avoid overlap:

```bash
claude task list --type simulation
```

- If a simulation already exists for the same product or prompt, show it to the user and ask whether to extend it or create a new one.
- If none exist, proceed to Step 2.

---

### Step 2 — Understand the product

Collect context on what the product is solving for. Ask the user:

- **What does the product do?** — core problem it solves and who it's for
- **What is the agent's role?** — what job is the agent being asked to do inside this product?
- **What does success look like?** — what should the agent reliably produce or decide?
- **Who are the end users?** — their technical level and expectations

If a URL is provided, use web search to fill in gaps before proceeding.

Document a one-paragraph **Product Context** summary before moving to Step 3.

---

### Step 3 — Gather simulation inputs

Ask the user for:

- **System prompt** — the agent's instructions (paste or describe)
- **User message / task** — what the user would send to the agent
- **Tools available** (optional) — list any tools the agent can call (web search, code execution, etc.)
- **Stop condition** (optional) — when should the simulation end? Default: first terminal response

---

### Step 4 — Run the simulation loop

For each iteration, show:

```
--- Turn N ---
[Reasoning] What the agent is thinking
[Action]    Tool call or response decision
[Output]    The agent's message or tool result
```

Continue until:
- The agent produces a final answer
- A tool returns an error that cannot be recovered
- The user says to stop
- 10 turns have elapsed (safety cap — ask to continue if reached)

---

### Step 5 — Debrief

After the loop ends, provide:

1. **What worked** — steps the agent handled well
2. **Failure points** — where the agent got confused or went off-track
3. **Prompt suggestions** — specific edits to the system prompt that would improve behavior
4. **Edge cases to test** — 2-3 follow-up scenarios worth simulating next

---

### Step 6 — Confirm and create the simulation task

Summarise what will be saved:

```
Product:        [product name]
Agent role:     [one line]
System prompt:  [first 100 chars…]
Scenario:       [user message / task]
Result:         [pass / fail / partial]
Suggested fix:  [top prompt suggestion]
```

Ask the user:
> "Shall I save this simulation to the platform?"

If confirmed, create the task via the CLI:

```bash
claude task create \
  --type simulation \
  --product "[product name]" \
  --title "[scenario title]" \
  --result "[pass|fail|partial]" \
  --notes "[top debrief finding]"
```

Confirm back with: "Simulation saved: `[title]`"

---

## Tips

- If the system prompt is vague, flag it before starting — a bad prompt makes the simulation less useful
- Simulate tool results realistically; don't always return success
- If the agent loops or hallucinates, call it out explicitly rather than papering over it
