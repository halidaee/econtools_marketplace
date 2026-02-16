# Migration Complete: Citation MCPs → manuscript-tools Plugin

**Date**: 2026-02-15

## Summary

Successfully migrated three citation MCP servers from standalone `citation-plugin` project to `manuscript-tools` Claude plugin and rewrote the `bibtex-curator` skill to orchestrate MCP tools.

## Migration Phases Completed

✅ **Phase 1: Directory Structure** — Created `mcps/` directory, moved all three MCPs, created `pixi.toml` and `mcps/README.md`

✅ **Phase 2: Skill Rewrite** — Transformed `bibtex-curator/SKILL.md` from 445 lines of manual instructions to ~350 lines of MCP orchestration

✅ **Phase 3: Reference Files** — Archived `references/` → `references-legacy/` with TODO for rigorous testing

✅ **Phase 4: Plugin Metadata** — Updated `plugin.json` to v2.0.0, added MCPs array, updated README

✅ **Phase 5: Testing** — Verified all 71 tests passing (25 + 22 + 24) with pixi

✅ **Phase 6: Cleanup** — Original `citation-plugin/` archived as `citation-plugin-archive/`

## Verification Status

### Tests
All 71 tests passing across three MCPs:
- `semantic-scholar-mcp`: 25 tests ✓
- `crossref-mcp`: 22 tests ✓
- `bibtex-mcp`: 24 tests ✓

### MCPs Migrated
1. **semantic-scholar-mcp** — Tools: `search`, `get_paper`, `get_bibtex`
2. **crossref-mcp** — Tools: `search`, `get_metadata`, `get_bibtex`, `find_published_version`
3. **bibtex-mcp** — Tools: `parse_bib`, `scan_bare_citations`, `rekey_entry`, `add_entry`, `suggest_replacement`

### Skill Updated
- **bibtex-curator** — Completely rewritten to use MCP tools instead of manual LLM instructions
- Original approach: Load 400+ lines of regex patterns, API instructions, BibTeX templates into context
- New approach: Call 12 deterministic MCP tools with orchestration logic

### Legacy Preserved
- Original skill documentation archived in `references-legacy/`
- Original project archived at `/Users/halidaee/citation-plugin-archive/`
- Git history preserved in archive

## Installation for Users

From `manuscript-tools/mcps/` directory:

```bash
claude mcp add semantic-scholar file://$(pwd)/semantic-scholar-mcp
claude mcp add crossref file://$(pwd)/crossref-mcp
claude mcp add bibtex file://$(pwd)/bibtex-mcp
```

## Installation for Developers

From `manuscript-tools/` directory:

```bash
pixi install
pixi run install-mcps
pixi run test
```

## Configuration Required

### CrossRef MCP
```bash
export CROSSREF_MAILTO="your.email@domain.com"
```

### Semantic Scholar MCP (Optional)
For higher rate limits:
```bash
mkdir -p ~/.config/semantic-scholar-mcp
echo "YOUR_API_KEY" > ~/.config/semantic-scholar-mcp/api_key
```

## Known Issues / TODOs

⚠️ **Rigorous testing needed**: The `bibtex-mcp.scan_bare_citations()` implementation has basic coverage (24 tests) but needs comprehensive testing against all 20+ citation patterns documented in `references-legacy/citation-patterns.md`.

See `skills/bibtex-curator/references-legacy/README.md` for details.

## Architecture Improvements

### Before Migration
- **Context cost**: ~445 lines of instructions + 400 lines of reference files loaded every invocation
- **Reliability**: LLM must manually apply regex, parse JSON, compute scores, format BibTeX
- **Testability**: No automated tests for citation detection or key generation
- **Reusability**: Logic embedded in skill, not reusable by other skills

### After Migration
- **Context cost**: ~350 lines of orchestration logic, no reference files needed
- **Reliability**: Deterministic regex engine, structured API clients, server-side confidence scoring
- **Testability**: 71 tests covering all MCP functionality
- **Reusability**: MCPs can be used by `bibtex-janitor` and other skills
- **Maintainability**: Each MCP is independently versioned and tested

## Git Commits

1. `feat: migrate MCPs to manuscript-tools plugin (Phases 1-3)` — Directory structure, skill rewrite, reference archival
2. `feat: update plugin metadata for MCP integration (Phase 4)` — plugin.json v2.0.0, README
3. `test: verify all MCPs in new location (Phase 5)` — 71 tests passing

## Related Documentation

- `mcps/README.md` — Installation and usage instructions
- `skills/bibtex-curator/SKILL.md` — Updated workflow using MCPs
- `skills/bibtex-curator/references-legacy/README.md` — Original implementation notes
- `/Users/halidaee/citation-plugin-archive/PLAN.md` — Original architecture plan
