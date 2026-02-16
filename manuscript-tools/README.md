# manuscript-tools

Academic manuscript skills for figures, tables, notation, proofs, bibliography management, and visual synchronization.

## MCPs

This plugin includes 3 MCP servers for citation and bibliography operations:

| MCP | Tools | Description |
|-----|-------|-------------|
| **semantic-scholar-mcp** | `search`, `get_paper`, `get_bibtex` | Search Semantic Scholar API for papers and citations |
| **crossref-mcp** | `search`, `get_metadata`, `get_bibtex`, `find_published_version` | Search CrossRef, retrieve metadata, find published versions |
| **bibtex-mcp** | `parse_bib`, `scan_bare_citations`, `rekey_entry`, `add_entry`, `suggest_replacement` | Local BibTeX operations and citation scanning |

See `mcps/README.md` for installation and usage instructions.

## Skills

| Skill | Description |
|-------|-------------|
| **aer-figures** | AER-compliant figure formatting and validation |
| **aer-tables** | AER-compliant table formatting and validation |
| **bibtex-curator** | BibTeX reference curation and management |
| **bibtex-janitor** | BibTeX cleanup with Python tooling (`clean_bib.py`) and tests |
| **notation-guardian** | Mathematical notation consistency checking |
| **palette-designer** | Color palette design with auto-preview hooks |
| **proof-checker** | Mathematical proof verification |
| **visual-sync** | Visual consistency synchronization across manuscript elements |

## Installation

Register this plugin in the Claude Plugins marketplace at `~/Documents/Github/Claude_Plugins/`.
