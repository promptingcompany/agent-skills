# Agent Simulation Workflow

Use this workflow when the user wants to simulate how an AI agent would behave given a system prompt and a task.

## Step 1 — Gather inputs

Ask the user for:
- **System prompt** — the agent's instructions (paste or describe)
- **User message / task** — what the user would send to the agent
- **Tools available** (optional) — list any tools the agent can call (web search, code execution, etc.)
- **Stop condition** (optional) — when should the simulation end? Default: first terminal response

## Step 2 — Run the simulation loop

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

## Step 3 — Debrief

After the loop ends, provide:

1. **What worked** — steps the agent handled well
2. **Failure points** — where the agent got confused or went off-track
3. **Prompt suggestions** — specific edits to the system prompt that would improve behavior
4. **Edge cases to test** — 2-3 follow-up scenarios worth simulating next

## Tips

- If the system prompt is vague, flag it before starting — a bad prompt makes the simulation less useful
- Simulate tool results realistically; don't always return success
- If the agent loops or hallucinates, call it out explicitly rather than papering over it
