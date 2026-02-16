# Citation MCPs

Three Model Context Protocol (MCP) servers for bibliographic operations, used by the `bibtex-curator` skill.

## MCPs

| MCP | Tools | Description |
|-----|-------|-------------|
| **semantic-scholar-mcp** | `search`, `get_paper`, `get_bibtex` | Search Semantic Scholar API for papers, retrieve metadata and BibTeX citations |
| **crossref-mcp** | `search`, `get_metadata`, `get_bibtex`, `find_published_version` | Search CrossRef, get paper metadata/BibTeX, find published versions of working papers |
| **bibtex-mcp** | `parse_bib`, `scan_bare_citations`, `rekey_entry`, `add_entry`, `suggest_replacement` | Parse .bib files, scan documents for bare citations, rekey entries, generate citation commands |

## Installation

### For Users

**Requirements:** Python 3.11+ (that's it!)

From the `manuscript-tools/mcps` directory:

```bash
# Register MCPs with Claude Code (automatically installs them)
claude mcp add semantic-scholar file://$(pwd)/semantic-scholar-mcp
claude mcp add crossref file://$(pwd)/crossref-mcp
claude mcp add bibtex file://$(pwd)/bibtex-mcp
```

Claude Code handles the installation automatically. No pip or pixi needed!

### For Developers

**Requirements:** Python 3.11+ and [pixi](https://pixi.sh/)

For development/testing, install locally with pixi:

```bash
# From manuscript-tools root directory
pixi install
pixi run install-mcps  # Installs all MCPs in editable mode with dev deps
```

Or without pixi:
```bash
# From mcps/ directory
pip install -e ./semantic-scholar-mcp[dev]
pip install -e ./crossref-mcp[dev]
pip install -e ./bibtex-mcp[dev]
```

This is only needed if you're modifying the MCPs or running tests locally.

## Testing

### With pixi (developers)

```bash
pixi run test           # Run all tests (71 total)
pixi run test-semantic  # 25 tests
pixi run test-crossref  # 22 tests
pixi run test-bibtex    # 24 tests
```

### Without pixi (requires pytest installed)

```bash
# Install test dependencies first
pip install pytest pytest-cov respx

# Run tests
pytest semantic-scholar-mcp/tests/
pytest crossref-mcp/tests/
pytest bibtex-mcp/tests/
```

## Configuration

### CrossRef MCP (Required)

CrossRef requires a `mailto` parameter for polite pool access (50 req/s vs 1 req/s):

**Option 1: Environment variable**
```bash
export CROSSREF_MAILTO="your.email@domain.com"
```

**Option 2: Config file**
```bash
mkdir -p ~/.config/crossref-mcp
echo '{"mailto": "your.email@domain.com"}' > ~/.config/crossref-mcp/config.json
```

### Semantic Scholar MCP (Optional)

For higher rate limits, register for an API key at https://www.semanticscholar.org/product/api and add:

```bash
mkdir -p ~/.config/semantic-scholar-mcp
echo "YOUR_API_KEY" > ~/.config/semantic-scholar-mcp/api_key
```

Without an API key, you get 100 requests per 5 minutes.

## Usage

These MCPs are designed to be used by the `bibtex-curator` skill. See `../skills/bibtex-curator/SKILL.md` for the orchestration workflow.

You can also invoke tools directly:

```python
# Example: Search for a paper
from semantic_scholar_mcp.client import SemanticScholarClient
client = SemanticScholarClient()
results = client.search("Conley Udry pineapple")

# Example: Parse a .bib file
from bibtex_mcp.client import BibTexClient
client = BibTexClient()
index = client.parse_bib("references.bib")

# Example: Get BibTeX for a DOI
from crossref_mcp.client import CrossRefClient
client = CrossRefClient(mailto="your.email@domain.com")
bibtex = client.get_bibtex("10.1257/aer.100.1.35")
```

## Development

Each MCP is a standalone Python package with:
- `src/{mcp_name}/` — source code
- `tests/` — pytest unit tests
- `pyproject.toml` — package metadata
- `README.md`, `LICENSE`, `CHANGELOG.md`

All three use:
- **FastMCP** framework for MCP server implementation
- **httpx** for HTTP requests (semantic-scholar, crossref)
- **pybtex** for BibTeX parsing (bibtex-mcp only)
- **respx** for testing HTTP mocks

## Troubleshooting

**Issue: Tests fail with import errors**
```bash
# Reinstall MCPs in editable mode
pixi run install-mcps
```

**Issue: CrossRef MCP fails with "mailto is required"**
```bash
# Set the mailto configuration (see Configuration section above)
export CROSSREF_MAILTO="your.email@domain.com"
```

**Issue: Can't find pixi command**
```bash
# Use the absolute path (adjust for your home directory)
~/.pixi/bin/pixi run test
```

## Version History

- **2.0.0** (2025-02-15) — Initial release with three MCPs
  - Migrated from standalone `citation-plugin` project
  - Integrated with `bibtex-curator` skill
  - 71 tests passing (25 + 22 + 24)
