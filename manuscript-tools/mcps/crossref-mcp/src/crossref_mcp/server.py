from __future__ import annotations

import json

from fastmcp import FastMCP

from .client import (
    CrossRefClient,
    RateLimitError,
    NotFoundError,
    APIError,
)

mcp = FastMCP("Crossref")

_client = CrossRefClient()  # Auto-loads mailto from env or config


def _error(code: str, message: str, **extra) -> str:
    return json.dumps({"error": code, "message": message, **extra})


@mcp.tool()
def search(
    query: str | None = None,
    author: str | None = None,
    title: str | None = None,
    year: int | None = None,
    work_type: str | None = None,
    rows: int = 5,
) -> str:
    """Search Crossref for scholarly works.

    Args:
        query: Free-text search query (e.g., "learning technology Ghana").
        author: Filter by author name (e.g., "Conley").
        title: Filter by title keywords.
        year: Filter by publication year (exact match).
        work_type: Filter by work type (e.g., "journal-article", "book").
        rows: Maximum number of results to return (default 5).

    Returns:
        JSON array of work objects with title, authors, year, journal, volume, issue, pages, DOI, type, and confidence_score.
    """
    if not query and not author and not title:
        return _error(
            "invalid_request",
            "At least one of query, author, or title is required.",
        )

    try:
        results = _client.search(
            query=query,
            author=author,
            title=title,
            year=year,
            work_type=work_type,
            rows=rows,
        )
        return json.dumps(results, indent=2)
    except RateLimitError as e:
        return _error("rate_limited", str(e), retry_after_seconds=e.retry_after)
    except APIError as e:
        return _error("api_error", str(e))


@mcp.tool()
def get_metadata(doi: str) -> str:
    """Retrieve full metadata for a work by DOI.

    Args:
        doi: Digital Object Identifier (e.g., "10.1257/aer.100.1.35").

    Returns:
        JSON object with complete work metadata from Crossref.
    """
    try:
        result = _client.get_metadata(doi)
        return json.dumps(result, indent=2)
    except NotFoundError as e:
        return _error("not_found", str(e))
    except RateLimitError as e:
        return _error("rate_limited", str(e), retry_after_seconds=e.retry_after)
    except APIError as e:
        return _error("api_error", str(e))


@mcp.tool()
def get_bibtex(doi: str) -> str:
    """Retrieve BibTeX citation for a work.

    Args:
        doi: Digital Object Identifier (e.g., "10.1257/aer.100.1.35").

    Returns:
        Raw BibTeX string, or a JSON error object if not found.
    """
    try:
        return _client.get_bibtex(doi)
    except NotFoundError as e:
        return _error("not_found", str(e))
    except ValueError as e:
        return _error("bibtex_unavailable", str(e))
    except RateLimitError as e:
        return _error("rate_limited", str(e), retry_after_seconds=e.retry_after)
    except APIError as e:
        return _error("api_error", str(e))


@mcp.tool()
def find_published_version(
    title: str, author: str | None = None, working_paper_year: int | None = None
) -> str:
    """Find the published journal version of a working paper.

    Uses title similarity matching to locate the published version, searching for journal articles.
    Only returns results if confidence is high (title similarity > 0.5) and a DOI is available.

    Args:
        title: Title of the working paper.
        author: Primary author name (optional, improves matching).
        working_paper_year: Year the working paper was released (optional).

    Returns:
        JSON object with best-match metadata and BibTeX if found, or null if no high-confidence match.
    """
    try:
        result = _client.find_published_version(title, author, working_paper_year)
        if result is None:
            return json.dumps(None)
        return json.dumps(result, indent=2)
    except RateLimitError as e:
        return _error("rate_limited", str(e), retry_after_seconds=e.retry_after)
    except APIError as e:
        return _error("api_error", str(e))


def main() -> None:
    """Run the Crossref MCP server."""
    mcp.run()


app = mcp

if __name__ == "__main__":
    main()
