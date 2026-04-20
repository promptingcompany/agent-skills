# Generative Engine Optimization (GEO)

A Claude Code skill covering core GEO workflows: **agent simulation**, **prompt generation**, and **content generation**.

## What this skill does

| Workflow | Trigger phrases | Description |
|---|---|---|
| Agent simulation | "simulate agent", "run agent loop", "test agent" | Simulates a multi-step agent conversation against a prompt |
| Prompt generation | "generate a prompt", "write a system prompt", "draft prompt" | Creates structured system or user prompts for a given task |
| Content generation | "generate content", "write copy", "draft content" | Produces on-brand content using configurable tone and format |
| GEO simulation prompts | "generate prompts for [product]", "create GEO audit prompts", "build a prompt bank", "test if AI recommends [product]" | Generates 15-25 pain-focused, unbranded simulation prompts to audit AI visibility for a product |

## Installation

```bash
cp -r skills/generative-engine-optimization ~/.claude/skills/
```

Or paste `SKILL.md` into your claude.ai project knowledge.

## File layout

```
generative-engine-optimization/
├── SKILL.md              ← load this into Claude
├── README.md             ← you are here
├── metadata.json         ← version + abstract
└── workflows/
    ├── agent-simulation.md
    ├── prompt-generation.md
    ├── content-generation.md
    └── geo-simulation-prompts.md
```
