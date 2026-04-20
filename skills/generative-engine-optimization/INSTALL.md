# Installation Guide

## Claude Code (CLI)

### 1. Copy the skill

```bash
cp -r skills/generative-engine-optimization ~/.claude/skills/
```

Claude Code picks up skills from `~/.claude/skills/` automatically. The skill activates when you trigger it by keyword (see `SKILL.md` for the full trigger list).

### 2. Enable web search (required for GEO simulation prompts)

The GEO simulation prompts workflow (Phase 1: Research) needs live web search to find neutral buyer-language sources on Reddit, Hacker News, and similar sites. Configure a web search MCP so Claude can run these searches:

**Option A — Brave Search MCP (recommended)**

```bash
# Install the MCP server
npm install -g @modelcontextprotocol/server-brave-search

# Add it to Claude Code
claude mcp add brave-search \
  --command npx \
  --args "-y @modelcontextprotocol/server-brave-search" \
  --env BRAVE_API_KEY=your_api_key_here
```

Get a free API key at [brave.com/search/api](https://brave.com/search/api).

**Option B — Use Claude Code's built-in web search**

If you are on a Claude Code plan that includes web search, no additional setup is needed — the GEO workflow will use it automatically.

### 3. Verify

Open a new Claude Code session and type:

```
generate GEO prompts for <your product name or URL>
```

Claude should begin Phase 1 research.

---

## claude.ai (Project Knowledge)

1. Open your Project in claude.ai
2. Go to **Project Knowledge → Add content**
3. Paste the contents of `SKILL.md`
4. (Optional) Also paste `workflows/geo-simulation-prompts.md` for the full GEO workflow detail

For web search during the GEO phase, ensure the Project has **Web search enabled** in its settings.

---

## MCP Server (self-hosted or remote)

If you want to serve this skill via an MCP server so teams can consume it programmatically:

### Using `mcp-server-markdown-skills` (community package)

```bash
npm install -g mcp-server-markdown-skills

# Point it at the skill directory
mcp-server-markdown-skills --skills-dir ./skills
```

Then add it to Claude Code or your MCP-compatible client:

```bash
claude mcp add geo-skills \
  --command npx \
  --args "mcp-server-markdown-skills --skills-dir /path/to/agent-skills/skills"
```

### Manual remote MCP

If you host your own MCP endpoint, add the skill content to your server's skill registry and expose it at a URL:

```bash
claude mcp add geo-skills --url https://your-mcp-server.example.com/mcp
```

---

## Uninstalling

```bash
rm -rf ~/.claude/skills/generative-engine-optimization
claude mcp remove brave-search   # if added
```
