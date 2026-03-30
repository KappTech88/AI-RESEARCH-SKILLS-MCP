# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python MCP server exposing 91 expert-level AI research skills (from Orchestra Research, MIT License) as 8 tools for Claude Desktop. Uses stdio transport with asyncio. The entire server is a single file: `servers/server.py` (~390 lines).

## Setup & Run

```powershell
# First-time setup
cd D:\claude-desktop-connectors\ai-research-skills-mcp
python -m venv venv
venv\Scripts\activate
pip install mcp pyyaml

# Verify dependencies
venv\Scripts\python.exe -c "import mcp, yaml; print('OK')"
```

Or run `setup.bat` (does the above plus prints Claude Desktop config instructions).

The server runs inside Claude Desktop via stdio — there is no standalone test harness or test suite.

## Architecture

**Single-file server** (`servers/server.py`):
1. **Startup**: `build_index()` scans `skills/*/SKILL.md`, parses YAML frontmatter, builds in-memory `SKILL_INDEX` dict (slug -> metadata).
2. **Runtime**: `@server.call_tool()` dispatches 8 tools by name. Content is read from disk on demand (lazy). Search and recommend operate over the in-memory index.
3. **Transport**: MCP stdio via `mcp.server.stdio.stdio_server`.

**Key data structures**:
- `CATEGORY_MAP` (dict): Hardcoded mapping of 91 skill slugs to 22 category strings.
- `SKILL_INDEX` (dict): Built at startup. Maps slug -> `{name, description, tags, version, dependencies, references, examples, scripts, templates, lines}`.
- `ROUTING_TABLE` (inline dict in `research_routing_table` handler): Maps 21 research phases to skill slugs.

**Skill data** (`skills/<slug>/`):
- `SKILL.md` — YAML frontmatter (name, description, version, tags, dependencies, author, license) + markdown body with expert guidance.
- Optional subdirs: `references/`, `examples/`, `scripts/`, `templates/` containing supporting files.

## 8 MCP Tools

| Tool | Input | Purpose |
|------|-------|---------|
| `research_list_categories` | none | Browse 22 categories with skill counts |
| `research_list_skills` | `category?` | List skills, optional category filter |
| `research_search_skills` | `query` | Keyword search (name, description, tags, slug) |
| `research_read_skill` | `skill_slug` | Load full SKILL.md content |
| `research_read_reference` | `skill_slug`, `filename` | Read file from references/examples/scripts/templates |
| `research_get_metadata` | `skill_slug` | JSON metadata without full content |
| `research_recommend` | `task` | Pattern-matched task-based recommendations (top 10) |
| `research_routing_table` | none | Full research lifecycle phase -> skills mapping |

## Adding a New Skill

1. Create `skills/<new-slug>/SKILL.md` with YAML frontmatter matching the existing schema.
2. Add the slug -> category mapping in `CATEGORY_MAP` in `server.py`.
3. Optionally add the slug to `patterns` dict (in `research_recommend` handler) and `routing` dict (in `research_routing_table` handler).
4. Restart the MCP server (quit and reopen Claude Desktop).

## Key Conventions

- All paths resolved relative to `server.py` via `Path(__file__).parent.parent`.
- `CATEGORY_MAP` is the single source of truth for skill-to-category mapping — it is not derived from skill metadata.
- Search scoring: exact slug match = 100, partial slug = 80, name match = 60, description/tags = 40.
- Recommend scoring: keyword in searchable text = +5, keyword in slug = +10, pattern match = +30.
- Tool handlers return `[types.TextContent(type="text", text=...)]`.
- YAML frontmatter parsed with `yaml.safe_load`; errors return empty dict (silent fallback).

## Dependencies

Only `mcp` and `pyyaml` are required. The `google-auth` packages in `setup.bat` are unused leftovers from the gmail-multi MCP template.
