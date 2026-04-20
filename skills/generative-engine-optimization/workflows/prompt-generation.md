# Prompt Generation Workflow

Use this workflow when the user wants to create or improve a prompt for an AI model.

## Step 1 — Clarify the goal

Ask the user:
- What task should the prompt accomplish?
- Who or what will use the prompt — an agent, a one-shot API call, a chat UI?
- Is there an existing prompt to improve, or are we starting fresh?
- Any constraints (max length, tone, audience, output format)?

## Step 2 — Choose a prompt type

| Type | When to use |
|---|---|
| System prompt | Persistent agent persona or role instructions |
| User message template | Parameterized input for repeated tasks |
| Few-shot template | Task needs examples to ground the model |
| Chain-of-thought scaffold | Task benefits from explicit reasoning steps |

## Step 3 — Draft the prompt

Follow this structure for system prompts:

```
# Role
You are a [role] that [core function].

# Context
[Background the model needs to do its job well]

# Instructions
1. [Step or rule]
2. [Step or rule]
...

# Output format
[Describe the expected format: JSON, prose, bullet list, etc.]

# Constraints
- [Hard limits or things to avoid]
```

For few-shot templates, add an `# Examples` section with 2-3 input/output pairs.

## Step 4 — Review checklist

Before presenting the draft, verify:
- [ ] Role is specific, not generic ("expert data analyst" not "helpful assistant")
- [ ] Instructions are imperative ("Return JSON" not "You should return JSON")
- [ ] Output format is explicit
- [ ] No contradictions between instructions
- [ ] No unnecessary padding or filler phrases

## Step 5 — Present and iterate

Show the prompt, explain 2-3 key decisions, and ask:
> "Want me to adjust the tone, add examples, or tighten any section?"
