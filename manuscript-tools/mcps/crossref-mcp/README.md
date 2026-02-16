# CrossRef MCP

A Model Context Protocol (MCP) server for the [CrossRef API](https://www.crossref.org/documentation/retrieve-metadata/). Search scholarly metadata, retrieve paper details, get BibTeX citations, and find published versions of working papers.

## Installation

Install via the parent plugin - see [../README.md](../README.md) for full instructions.

Quick reference:
```bash
claude mcp add crossref file://$(pwd)/crossref-mcp
```

## Tools

### `search`

Search CrossRef for scholarly works.

**Parameters:**
- `query` (optional): Free-text search query (e.g., "learning technology Ghana")
- `author` (optional): Filter by author name (e.g., "Conley")
- `title` (optional): Filter by title keywords
- `year` (optional): Filter by publication year (exact match)
- `work_type` (optional): Filter by work type (e.g., "journal-article", "book")
- `rows` (optional): Maximum number of results to return (default: 5)

At least one of `query`, `author`, or `title` is required.

**Returns:** JSON array of work objects with title, authors, year, journal, volume, issue, pages, DOI, type, and confidence score.

**Example:**
```python
# Search for papers by author and keywords
search(query="learning technology", author="Conley", rows=10)

# Search by title
search(title="Learning about a New Technology")
```

### `get_metadata`

Retrieve full metadata for a work by DOI.

**Parameters:**
- `doi` (required): Digital Object Identifier (e.g., "10.1257/aer.100.1.35")

**Returns:** JSON object with complete work metadata from CrossRef.

**Example:**
```python
# Get metadata for a specific paper
get_metadata(doi="10.1257/aer.100.1.35")
```

### `get_bibtex`

Retrieve BibTeX citation for a work.

**Parameters:**
- `doi` (required): Digital Object Identifier (e.g., "10.1257/aer.100.1.35")

**Returns:** Raw BibTeX string, or error if not found.

**Example:**
```python
# Get BibTeX citation
get_bibtex(doi="10.1257/aer.100.1.35")
```

### `find_published_version`

Find the published journal version of a working paper.

Uses title similarity matching to locate the published version, searching only for journal articles. Returns results only if confidence is high (title similarity > 0.5) and a DOI is available.

**Parameters:**
- `title` (required): Title of the working paper
- `author` (optional): Primary author name (improves matching)
- `working_paper_year` (optional): Year the working paper was released

**Returns:** JSON object with best-match metadata and BibTeX if found, or `null` if no high-confidence match.

**Example:**
```python
# Find published version of a working paper
find_published_version(
    title="Learning about a New Technology: Pineapple in Ghana",
    author="Conley",
    working_paper_year=2008
)
```

## Configuration

**REQUIRED:** CrossRef requires a `mailto` parameter for polite pool access (50 req/s vs 1 req/s without).

**Option 1: Environment variable**
```bash
export CROSSREF_MAILTO="your.email@domain.com"
```

**Option 2: Config file**
```bash
mkdir -p ~/.config/crossref-mcp
echo '{"mailto": "your.email@domain.com"}' > ~/.config/crossref-mcp/config.json
```

## Development

See parent [README.md](../README.md) for development setup with pixi.

Quick reference for testing:
```bash
pixi run test-crossref
```
