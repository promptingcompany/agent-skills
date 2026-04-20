# Generative Engine Optimization (GEO)

A Claude Code skill covering core GEO workflows: **agent simulation**, **prompt generation**, and **content generation**.

## What this skill does

| Workflow | Trigger phrases | Description |
|---|---|---|
| Agent simulation | "simulate agent", "run agent loop", "test agent" | Simulates a multi-step agent conversation against a prompt |
| GEO simulation prompts | "generate prompts for [product]", "create GEO audit prompts", "build a prompt bank", "test if AI recommends [product]" | Generates 15-25 pain-focused, unbranded simulation prompts to audit AI visibility for a product |

## Installation

See [`INSTALL.md`](INSTALL.md) for full instructions covering Claude Code CLI, claude.ai, and MCP server setup.

Quick start:

```bash
cp -r skills/generative-engine-optimization ~/.claude/skills/
```

## File layout

```
generative-engine-optimization/
├── SKILL.md              ← load this into Claude
├── INSTALL.md            ← CLI, claude.ai, and MCP server setup
├── README.md             ← you are here
├── metadata.json         ← version + abstract
└── workflows/
    ├── agent-simulation.md
    └── geo-simulation-prompts.md
```
