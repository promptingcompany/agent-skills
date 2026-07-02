# Setup Experiment

Interactive workflow to set up agent simulation experiments end-to-end — tasks, environments, signals, and first run.

## Workflows

| Workflow | Triggers |
|---|---|
| Setup Experiment | "set up an experiment", "create an experiment", "I want to run an experiment", "new experiment" |
| Usability Benchmark Design | "usability benchmark", "friction delta", "skill-off vs skill-on", "does the skill help", "rigorous benchmark" |
| Cross-Product Benchmark | "compare products", "benchmark products", "compare providers", "same tasks across products", "PlanetScale vs Neon vs Supabase" |

## Reference

Concepts and platform limits live in the [Coding Agent Optimization docs](https://docs.promptingcompany.com/guides/coding-agent-optimization/overview):

| Doc | Covers |
|---|---|
| [Tasks](https://docs.promptingcompany.com/guides/coding-agent-optimization/tasks) | Instructions, goals/criteria, init files & commands, secrets |
| [Environments](https://docs.promptingcompany.com/guides/coding-agent-optimization/environments) | Harness/model, sandbox resources, GPU, secrets |
| [Runs & iterations](https://docs.promptingcompany.com/guides/coding-agent-optimization/runs) | Run lifecycle and what each run records |
| [Signals](https://docs.promptingcompany.com/guides/coding-agent-optimization/signals) | Custom metric extraction |
| [Limits & constraints](https://docs.promptingcompany.com/guides/coding-agent-optimization/limits) | Execution model + all hard limits |
| [`workflows/writing-prompts.md`](workflows/writing-prompts.md) | Rules & examples for task prompts and goal descriptions (skill-local) |

## Install

```bash
cp -r skills/setup-experiment ~/.claude/skills/
```

See [`INSTALL.md`](INSTALL.md) for claude.ai setup.
