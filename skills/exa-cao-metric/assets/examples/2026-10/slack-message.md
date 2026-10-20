*October baseline: how often coding agents choose Exa*

Coding agents chose Exa in 23% of responses (45 of 192): as their first pick, as the head-to-head winner, or as the main search in a build. Full report attached.

We ran the 50-prompt set on Claude Code and Codex: 16 use cases, each asked as tool selection, head-to-head and build, with and without an instruction to research the options first, plus the 2 usability prompts.

The three numbers we track each month (research mode):
• *Answers citing a page we publish:* 1% (1/96)
• *Builds using Exa as the main search:* 13% (4/32)
• *Head-to-head wins against a named rival:* 47% (15/32)
For context, 49% of research answers cite some Exa page, mostly the docs.

Findings:
• Builds go to the model provider's own search. Agents wire the search they can test with the key they already have. Exa was the main search in 4 of 64 builds.
• In tool selection, agents mostly don't consider Exa. Losing agents opened an Exa page in only 4 of 54 cases.
• Head-to-head losses happen after agents read Exa's docs (22 of 33). They pick a rival on one narrow need: exact-phrase matching, a total token budget, a news mode, or a source and price for each result.
• Exa won every head-to-head on company, people and topic discovery. Leaving out places, events and funding, it wins 58%.

Next month we rerun the same prompts and report these three numbers against this baseline, plus how often agents open an Exa page, since that moves before wins do. Each agent answers each prompt once, so we treat moves of 15 points or more as real.

Notes on the setup:
• Models: Claude Code on its default model (Opus 5.5) and Codex on its default (GPT-6.1 Sol).

Experiments: https://app.promptingco.com/exa/p/exa-search-docs/simulation/experiments

Action items (top priorities; the full ranked list is in the PDF):
1. Check search engines can find our existing Exa pages, and submit every new page. Live by Oct 16.
2. Ask Exa to confirm facts and approve naming competitors in page titles. Live by Oct 20.
3. Publish a comparison page: Exa vs Brave Search API for coding agents (2026). Live by Nov 9. Needs Exa OK.
4. Publish a page: How much Exa costs for common jobs (2026). Live by Nov 9. Needs Exa OK.
5. Write 4 short sections for Exa to add to its docs. Live by Nov 20. Needs Exa OK.
