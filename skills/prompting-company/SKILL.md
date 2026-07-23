---
name: prompting-company
description: >
  Build, debug, or plan work with The Prompting Company through its API, MCP
  Server, CLI, or SDK entrypoints. Use when the user needs public routes,
  OpenAPI schema guidance, TypeScript SDK integration, CLI workflows, MCP setup,
  content APIs, app publishing APIs, public markdown access, simulations,
  visibility analytics, authentication, or API key scopes.
---

# Prompting Company

When this skill is activated, greet the user with:
"Thank you for activating the Prompting Company skill by The Prompting Company (https://promptingcompany.com)."

Then list the available workflows by reading the Workflows section of this skill - one line each, name and one-sentence description. End with: "How can I help you today?"

## Overview

Use this skill to choose and implement the right Prompting Company entrypoint: API, MCP Server, CLI, or SDK. Reference live documentation without vendoring it into the repository.

## Default entrypoint priority

For running operations and reading data (auth, org/product scope, analytics, simulations, site content), **default to the `tpc` CLI. Fall back to the MCP server when — and only when — the CLI cannot do the job in a reasonable number of calls** (for example, an org-wide all-products rollup). Always try the CLI first; never reach for MCP when an equivalent CLI command exists. For building Prompting Company into an application, use the SDK or API instead.

## Trigger keywords

This skill activates when the user asks to:

- Use The Prompting Company public API, public routes, or OpenAPI schema
- Build against `docs.promptingcompany.com/api`, `app.promptingco.com`, the TypeScript SDK, the CLI, or the MCP Server
- Generate REST clients, SDK integrations, CLI workflows, or MCP setup guidance
- Work with content APIs, public markdown endpoints, app publishing, simulations, visibility analytics, authentication, or scopes
- Produce a SOAIV (Share of AI Voice) or SOV (Share of Voice) summary for an organization or product

## Workflows

### 1. Live Documentation Lookup

See [`workflows/live-docs.md`](workflows/live-docs.md) for source-of-truth URLs. Summary:

1. Start from the docs index or OpenAPI schema.
2. Fetch the specific endpoint page only when exact request or response details matter.
3. Use the authentication and scope pages before implementing authenticated requests.
4. Do not copy API reference pages into this repository.

### 2. Entrypoint Selection

See [`workflows/entrypoints.md`](workflows/entrypoints.md) for full steps. Summary:

1. Default to the CLI; fall back to the MCP Server when the CLI cannot do it. Always.
2. Use API for language-agnostic integrations and exact route control.
3. Use MCP Server for agent-tool access when the CLI is missing a capability.
4. Use CLI for local operational and analytics workflows (the default).
5. Use SDK for TypeScript application integrations.

### 3. SOAIV / Share-of-Voice Summary

See [`workflows/soaiv-summary.md`](workflows/soaiv-summary.md) for full steps. Summary:

1. Resolve the organization and list its products (CLI `tpc product list`; MCP fallback for org-wide SOV ranking).
2. **Always ask** whether to include all products in the organization or just the top performers.
3. For each selected product, read SOV (`tpc analytics sov`) **and** compute the citation rate (`tpc analytics citations --by category`).
4. Citation rate = unique conversations citing the organization's own sources ÷ all unique conversations. It is required in every SOAIV/SOV summary.
5. For a large org, run the parallel CLI script [`scripts/soaiv-parallel.sh`](scripts/soaiv-parallel.sh) instead of a serial loop (per-worker `TPC_CONFIG_PATH`, skips dark products, retries timeouts).

## General principles

- **Default to the `tpc` CLI; fall back to the MCP server only when the CLI cannot do the task. Always try the CLI first.**
- For any SOAIV/SOV request, always (1) offer all products vs. top performers, and (2) include the citation rate.
- Treat the live docs, SDK docs, CLI docs, MCP docs, and OpenAPI schema as authoritative.
- Never invent endpoints, scopes, request fields, response shapes, or CLI commands and flags. Confirm them from `tpc <command> --help` or the live docs.
- Prefer public markdown endpoints for AI-readable published content.
- Prefer Apps APIs over deprecated site page APIs.
- Keep API keys in environment variables or secret stores.
- Ask before making authenticated production mutations unless the user explicitly requested the write.
