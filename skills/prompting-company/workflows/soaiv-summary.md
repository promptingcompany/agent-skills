---
name: soaiv-summary
description: >
  Produce a Share-of-AI-Voice (SOAIV) / Share-of-Voice (SOV) summary for a
  Prompting Company organization or product. CLI-first, MCP fallback. Always
  offers all-products vs. top-performers and always includes the citation rate.
---

# SOAIV / Share-of-Voice Summary

SOAIV ("Share of AI Voice") and SOV ("Share of Voice") refer to the same metric here — use this workflow for either term.

## Entrypoint priority

Default to the `tpc` CLI. Fall back to the MCP server only when the CLI cannot do the job in a reasonable number of calls (notably an org-wide all-products SOV rollup, which the CLI has no single command for). Never start with MCP when a CLI command exists. Confirm every command and flag from `tpc <command> --help`; do not invent flags.

## Definitions

- **SOV / SOAIV** (per product, default 30-day window): `mentions / runs`.
  - `mentions` = unique conversations that mention the brand.
  - `runs` = all unique conversations (tracked-prompt simulation runs) = the denominator.
- **Citation rate** (required in every summary): `unique conversations that cite the organization's own sources / all unique conversations`.
  - **Numerator** = the `self` category's `mentions` from `tpc analytics citations --by category` (already deduplicated to unique conversations; do not sum per-source rows). If there is no `self` row, the numerator is 0.
  - **Denominator** = `runs` from `tpc analytics sov`.
  - Per product: `self_mentions(p) / runs(p)`. Org-level rollup: `Σ self_mentions / Σ runs` across the selected products.

## Step 1 — Resolve the organization and list products

1. Set the org scope: `tpc org switch <org-slug>` (list options with `tpc org list`).
2. List the catalog: `tpc --format json product list`.
3. Ranking by performance ("top performers") needs SOV for every product. The CLI has no org-wide SOV command, so for the ranking use the MCP fallback in one call:
   - `getReport { reportType: "products", organizationSlug: "<org-slug>", sortKey: "latest_sov" }` → returns `latest_sov`, `mom_sov_growth`, `mom_ai_traffic_growth`, and `status_label` for every product.

## Step 2 — ASK the scope (ALWAYS)

Before producing any summary, ask the user — with `AskUserQuestion` — whether to include:

- **All products** in the organization, or
- **Top performers only** (e.g., top 10 by latest SOV).

Do not assume. This step is mandatory for every SOAIV/SOV request.

## Step 3 — Gather metrics per selected product (CLI-first)

First capture the user's current active product (`tpc product`) so you can restore it, because switching products mutates local CLI config.

For each selected product:

1. `tpc product switch <slug>`
2. SOV: `tpc analytics sov --last 30d --json` → read `sov`, `mentions`, `runs`.
3. Citations: `tpc analytics citations --last 30d --by category --json` → find the row where `key == "self"` → read its `mentions` (unique conversations citing the org's own sources). No `self` row ⇒ 0.
4. Citation rate = `100 * self_mentions / runs` (guard against `runs == 0`).

After the loop, restore scope: `tpc product switch <original-slug>`.

### Parallel bulk (CLI-first, preferred for large orgs)

A naive sequential loop is slow for a large org (e.g. nvidia-com has 183 products; a serial run takes ~45 min) because each product needs 3 round-trips and the `citations --by category` call is a cold backend aggregation (5–25s, occasionally a multi-minute timeout for the biggest products).

Use [`scripts/soaiv-parallel.sh`](../scripts/soaiv-parallel.sh) instead. It keeps the run **CLI-first** and parallelizes safely:

- Each worker gets its **own config copy** via `TPC_CONFIG_PATH` and switches *that* copy to its product, so concurrent workers never clobber each other's active-product. **The user's real `~/.tpc/config.json` is never touched** (no scope to restore).
- It **skips the citations call for `runs==0` products** (the bulk of a big org), **retries** failed calls with backoff, and **never records a failed call as `0`** — unrecoverable rows are marked `err` (sov failed) or `cit_err` (citations failed). After the parallel pass it runs a **sequential repair phase** over those flagged rows (no contention, extra patience), so a single invocation self-heals to complete data.

```bash
ORG=nvidia-com OUT=/tmp/nvidia_soaiv.tsv \
  skills/prompting-company/scripts/soaiv-parallel.sh
# smoke test first:  ORG=nvidia-com LIMIT=20 ./scripts/soaiv-parallel.sh
```

Output is a TSV (`slug, name, sov, mentions, runs, self_mentions, citation_rate_pct, status`) plus an org-level citation-rate rollup that **excludes any unresolved rows and prints a WARNING listing them**.

**Concurrency is the critical knob (measured):** the analytics backend returns `500: Failed to fetch share of voice` once ~6 requests from one account run at once. So `CONCURRENCY` defaults to **3** and must stay **≤4** — higher just produces 500s that the retry/repair phases then have to clean up. A full ~180-product org runs in ~12 min at concurrency 3.

**One genuine artifact to know:** a product whose `citations --by category` returns **zero category rows** has no categorized citations at all (seen on NVIDIA Token Cost — high SOV, empty leaderboard); the script flags it `cit_err` rather than guessing — a real `0`, not a recoverable error.

### MCP fallback

If the CLI is unavailable, the MCP `getReport` tool covers the same data:

- All products' SOV + MoM in one call: `getReport { reportType: "products", organizationSlug }` (SOV ranking only — no citation rate).
- Per-product citation rate: `getReport { reportType: "citations", organizationSlug, productSlug, groupBy: "category" }` → `self` row `mentions` (numerator); `getReport { reportType: "sov", ... }` → `runs` (denominator). Or `getReport { reportType: "citation_events", ... }` for row-level totals.

## Step 4 — Output

- **Org snapshot** (when org-wide): product count and status mix (healthy / at_risk / stalled).
- **Main table**, one row per product, columns: `Product | SOV % | MoM SOV | Citation rate % | AI traffic MoM | Status`. The **Citation rate column is required** — never omit it.
- **Movers** (when org-wide): biggest SOV gains/losses and AI-traffic surges (MoM).
- **Coverage gaps** (when org-wide): products at 0% SOV, and high-SOV products with no published content.
- Offer to drill into a specific product (per-prompt/topic SOV, citations leaderboard, AI-traffic breakdown).

## Quality check

Before finishing, confirm:

- You defaulted to the CLI and used MCP only as a fallback.
- You asked all-products vs. top-performers before summarizing.
- Every product row includes a citation rate computed as `self_mentions / runs`.
- You restored the user's original active product if you switched it.
- Every metric came from a real `tpc` command or MCP report — nothing invented.
