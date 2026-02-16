from __future__ import annotations

import json

from fastmcp import FastMCP

from .client import BibTexClient, ParseError, FileNotFoundError, BibTeXError

mcp = FastMCP("BibTeX")

_client = BibTexClient()


def _error(code: str, message: str, **extra) -> str:
    return json.dumps({"error": code, "message": message, **extra})


@mcp.tool()
def parse_bib(path: str) -> str:
    """Parse a .bib file and return a structured index of all entries.

    Args:
        path: Path to the .bib file

    Returns:
        JSON object mapping author-year keys to arrays of entries. Each entry contains key, type, authors, year, title, and fields.
    """
    try:
        result = _client.parse_bib(path)
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return _error("file_not_found", str(e))
    except ParseError as e:
        return _error("parse_error", str(e))


@mcp.tool()
def scan_bare_citations(path: str) -> str:
    """Scan a .qmd or .tex file for bare (written-out) citations.

    Uses regex patterns to detect citations like "Author (Year)" or "(Author Year)".
    Automatically excludes text preceded by @ or inside \\cite{} commands, and excludes
    matches in acknowledgments and bibliography sections.

    Args:
        path: Path to the document file (.qmd or .tex)

    Returns:
        JSON array of detected citations, each containing text, line, column, authors, year,
        citation_type, has_locator, locator, prefix, suffix, and is_possessive.
    """
    try:
        result = _client.scan_bare_citations(path)
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return _error("file_not_found", str(e))
    except Exception as e:
        return _error("scan_error", str(e))


@mcp.tool()
def rekey_entry(bibtex: str, existing_keys: list[str], convention: str = "auto") -> str:
    """Rewrite the BibTeX key of an entry to match a project's key convention.

    Format: {firstauthorlastname}{year}{firstsignificantwordoftitle} — all lowercase.
    Example: "conley2010learning" for Conley and Udry (2010), "Learning about a New Technology"

    Args:
        bibtex: A raw BibTeX entry string (as returned by CrossRef or Semantic Scholar)
        existing_keys: All keys currently in the project's .bib file (for dedup/disambiguation)
        convention: Key convention ("auto" to infer from existing_keys, or template string)

    Returns:
        The BibTeX entry string with the key rewritten
    """
    try:
        result = _client.rekey_entry(bibtex, existing_keys, convention)
        return result
    except ParseError as e:
        return _error("parse_error", str(e))
    except Exception as e:
        return _error("rekey_error", str(e))


@mcp.tool()
def add_entry(bib_path: str, entry: str) -> str:
    """Add a BibTeX entry to a .bib file.

    Checks for duplicate keys before adding. Appends to end of file with consistent formatting.

    Args:
        bib_path: Path to the .bib file
        entry: The BibTeX entry string to add

    Returns:
        Confirmation with the key that was added
    """
    try:
        result = _client.add_entry(bib_path, entry)
        return json.dumps({"status": "success", "message": result})
    except FileNotFoundError as e:
        return _error("file_not_found", str(e))
    except ParseError as e:
        return _error("parse_error", str(e))
    except BibTeXError as e:
        return _error("bibtex_error", str(e))


@mcp.tool()
def suggest_replacement(citation_text: str, key: str, doc_type: str, natbib: bool = True) -> str:
    """Given a bare citation and a resolved BibTeX key, return the proper citation command.

    Handles narrative vs. parenthetical citations, multi-author, locators, prefixes/suffixes, possessive forms.

    Args:
        citation_text: The bare citation text as detected (e.g., "Conley and Udry (2010)")
        key: The resolved BibTeX key (e.g., "conley2010learning")
        doc_type: "qmd" for Quarto or "tex" for LaTeX
        natbib: For .tex files, whether to use natbib commands (\\citet/\\citep) vs biblatex (\\textcite/\\parencite)

    Returns:
        JSON object containing original, replacement, and notes
    """
    try:
        result = _client.suggest_replacement(citation_text, key, doc_type, natbib)
        return json.dumps(result, indent=2)
    except Exception as e:
        return _error("replacement_error", str(e))


def main() -> None:
    """Run the BibTeX MCP server."""
    mcp.run()


app = mcp

if __name__ == "__main__":
    main()
