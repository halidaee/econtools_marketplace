# Namespace Migration Reference

## Overview

All research skills have been migrated from standalone skills (`~/.claude/skills/`) to organized plugins. Skills are now invoked using plugin namespace prefixes.

## Migration Date
February 15, 2026

---

## Analytics Toolkit (4 skills)

| Old Command | New Command |
|-------------|-------------|
| `/r-parallel` | `/analytics-toolkit:r-parallel` |
| `/r-style` | `/analytics-toolkit:r-style` |
| `/renv-manager` | `/analytics-toolkit:renv-manager` |
| `/dependency-tracker` | `/analytics-toolkit:dependency-tracker` |

**Purpose**: R workflow optimization for economics research

---

## Manuscript Tools (8 skills)

| Old Command | New Command |
|-------------|-------------|
| `/palette-designer` | `/manuscript-tools:palette-designer` |
| `/visual-sync` | `/manuscript-tools:visual-sync` |
| `/aer-figures` | `/manuscript-tools:aer-figures` |
| `/aer-tables` | `/manuscript-tools:aer-tables` |
| `/bibtex-janitor` | `/manuscript-tools:bibtex-janitor` |
| `/bibtex-curator` | `/manuscript-tools:bibtex-curator` |
| `/notation-guardian` | `/manuscript-tools:notation-guardian` |
| `/proof-checker` | `/manuscript-tools:proof-checker` |

**Purpose**: Economics manuscript preparation and formatting

---

## Unchanged Skills

These skills remain standalone (not research-specific):

- `/keybindings-help` - Claude Code configuration utility

---

## Installation Commands

```bash
# Add the marketplace
/plugin marketplace add ~/Documents/Github/Claude_Plugins

# Install plugins
/plugin install analytics-toolkit@research-tools
/plugin install manuscript-tools@research-tools
```

---

## Rollback

If needed, original skills are archived at:
```
~/.claude/skills-migration-archive-20260215_194909/
```

To rollback:
1. Uninstall plugins: `/plugin uninstall <plugin>@research-tools`
2. Remove marketplace: `/plugin marketplace remove research-tools`
3. Restart Claude Code (original skills still in `~/.claude/skills/`)

---

## Token Savings

**Before**: ~15-20k tokens loaded in every session (13 skills)

**After**:
- Base load: ~500 tokens (skill descriptions only)
- On-demand: ~7-10k tokens per plugin when invoked
- **Savings**: 12-15k tokens per message when plugins not needed

---

## Special Notes

### Skills with Supporting Files

- **r-parallel**: Has `references/` directory (preserved)
- **palette-designer**: Has `hooks/hooks.json` (paths updated to use `${CLAUDE_PLUGIN_ROOT}`)
- **bibtex-janitor**: Has Python implementation (`clean_bib.py`) and tests (preserved)

### Git Repository

All plugins are version controlled at:
```
~/Documents/Github/Claude_Plugins/
```

Initial commit: `1a41994`
