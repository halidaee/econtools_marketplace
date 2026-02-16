# Legacy Reference Files

These files documented the original LLM-based implementation of bibtex-curator (before MCPs). The logic has been moved into three MCP servers:

- **citation-patterns.md** → `bibtex-mcp.scan_bare_citations()` + `bibtex-mcp.suggest_replacement()`
- **api-lookups.md** → `crossref-mcp` and `semantic-scholar-mcp` tools
- **bibtex-formats.md** → `bibtex-mcp.rekey_entry()` key generation

## Status: Historical Reference

These files are preserved for:
- Understanding the original design decisions
- Comparing LLM-based vs MCP-based approaches
- Reference when debugging edge cases

## TODO: Rigorous Testing Needed

⚠️ **IMPORTANT**: The `bibtex-mcp.scan_bare_citations()` implementation needs more rigorous testing against all patterns documented in `citation-patterns.md`.

Current test coverage is basic (24 tests). Need to verify:
- All 20+ citation patterns from citation-patterns.md are detected
- Edge cases: possessive forms, name particles, hyphenated names, institutional authors
- False positive filtering: year ranges, acknowledgments, bibliography sections
- Locator extraction: pages, chapters, multiple formats
- Prefix/suffix handling: "see", "among others", etc.

**Action**: Review citation-patterns.md line-by-line and create comprehensive test cases for each pattern variant.

## Migration Date

Migrated to MCPs: 2025-02-15
