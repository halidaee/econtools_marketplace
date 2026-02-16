# bibtex-mcp

MCP server for local BibTeX file operations and citation scanning. Provides tools for parsing `.bib` files, detecting bare citations in `.qmd`/`.tex` documents, rekeying BibTeX entries, and generating proper citation commands.

## Setup

```bash
pip install bibtex-mcp
```

## Usage

Tools are used locally without network calls:
- Parse BibTeX files into structured indices
- Detect bare (written-out) citations in documents
- Rekey BibTeX entries to match project conventions
- Add entries to `.bib` files
- Generate replacement citation commands
