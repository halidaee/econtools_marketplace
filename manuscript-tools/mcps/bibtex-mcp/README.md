# BibTeX MCP

A Model Context Protocol (MCP) server for local BibTeX file operations. Parse `.bib` files, scan documents for bare citations, rekey entries to match project conventions, and generate proper citation commands. All operations are local - no network calls.

## Installation

Install via the parent plugin - see [../README.md](../README.md) for full instructions.

Quick reference:
```bash
claude mcp add bibtex file://$(pwd)/bibtex-mcp
```

## Tools

### `parse_bib`

Parse a `.bib` file and return a structured index of all entries.

**Parameters:**
- `path` (required): Path to the `.bib` file

**Returns:** JSON object mapping author-year keys to arrays of entries. Each entry contains key, type, authors, year, title, and fields.

**Example:**
```python
# Parse a BibTeX file
parse_bib(path="references.bib")
```

### `scan_bare_citations`

Scan a `.qmd` or `.tex` file for bare (written-out) citations.

Uses regex patterns to detect citations like "Author (Year)" or "(Author Year)". Automatically excludes text preceded by `@` or inside `\cite{}` commands, and excludes matches in acknowledgments and bibliography sections.

**Parameters:**
- `path` (required): Path to the document file (`.qmd` or `.tex`)

**Returns:** JSON array of detected citations, each containing text, line, column, authors, year, citation_type, has_locator, locator, prefix, suffix, and is_possessive.

**Example:**
```python
# Scan a Quarto document for bare citations
scan_bare_citations(path="paper.qmd")

# Scan a LaTeX document
scan_bare_citations(path="paper.tex")
```

### `rekey_entry`

Rewrite the BibTeX key of an entry to match a project's key convention.

Default format: `{firstauthorlastname}{year}{firstsignificantwordoftitle}` — all lowercase.
Example: `conley2010learning` for Conley and Udry (2010), "Learning about a New Technology"

**Parameters:**
- `bibtex` (required): A raw BibTeX entry string (as returned by CrossRef or Semantic Scholar)
- `existing_keys` (required): All keys currently in the project's `.bib` file (for dedup/disambiguation)
- `convention` (optional): Key convention ("auto" to infer from existing_keys, or template string; default: "auto")

**Returns:** The BibTeX entry string with the key rewritten.

**Example:**
```python
# Rekey a BibTeX entry to match existing conventions
rekey_entry(
    bibtex='@article{Smith2020,\n  title={Example},\n  author={Smith, J.},\n  year={2020}\n}',
    existing_keys=["conley2010learning", "udry2012technology"]
)
# Returns: @article{smith2020example, ...}
```

### `add_entry`

Add a BibTeX entry to a `.bib` file.

Checks for duplicate keys before adding. Appends to end of file with consistent formatting.

**Parameters:**
- `bib_path` (required): Path to the `.bib` file
- `entry` (required): The BibTeX entry string to add

**Returns:** JSON confirmation with the key that was added.

**Example:**
```python
# Add a new entry to a .bib file
add_entry(
    bib_path="references.bib",
    entry='@article{conley2010learning,\n  title={Learning about a New Technology},\n  author={Conley, T. and Udry, C.},\n  year={2010}\n}'
)
```

### `suggest_replacement`

Given a bare citation and a resolved BibTeX key, return the proper citation command.

Handles narrative vs. parenthetical citations, multi-author, locators, prefixes/suffixes, and possessive forms.

**Parameters:**
- `citation_text` (required): The bare citation text as detected (e.g., "Conley and Udry (2010)")
- `key` (required): The resolved BibTeX key (e.g., "conley2010learning")
- `doc_type` (required): "qmd" for Quarto or "tex" for LaTeX
- `natbib` (optional): For `.tex` files, whether to use natbib commands (`\citet`/`\citep`) vs biblatex (`\textcite`/`\parencite`); default: `true`

**Returns:** JSON object containing original text, replacement command, and notes.

**Example:**
```python
# Get replacement for a Quarto document
suggest_replacement(
    citation_text="Conley and Udry (2010)",
    key="conley2010learning",
    doc_type="qmd"
)
# Returns: {"original": "Conley and Udry (2010)", "replacement": "@conley2010learning", ...}

# Get replacement for LaTeX with natbib
suggest_replacement(
    citation_text="(Conley and Udry, 2010)",
    key="conley2010learning",
    doc_type="tex",
    natbib=True
)
# Returns: {"original": "(Conley and Udry, 2010)", "replacement": "\\citep{conley2010learning}", ...}
```

## Configuration

No configuration needed - all operations are local.

## Development

See parent [README.md](../README.md) for development setup with pixi.

Quick reference for testing:
```bash
pixi run test-bibtex
```
