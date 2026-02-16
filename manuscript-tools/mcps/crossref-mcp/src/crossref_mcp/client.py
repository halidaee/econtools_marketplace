from __future__ import annotations

import httpx
import json
from pathlib import Path


class CrossRefError(Exception):
    """Base error for Crossref API."""


class RateLimitError(CrossRefError):
    """429 Too Many Requests."""

    def __init__(self, retry_after: int | None = None):
        self.retry_after = retry_after
        msg = "Rate limited"
        if retry_after:
            msg += f" (retry after {retry_after}s)"
        super().__init__(msg)


class NotFoundError(CrossRefError):
    """404 Resource not found."""


class APIError(CrossRefError):
    """Other API errors."""


class CrossRefClient:
    BASE_URL = "https://api.crossref.org"

    def __init__(self, mailto: str | None = None, timeout: float = 30.0):
        if mailto is None:
            mailto = self._load_mailto()

        if not mailto:
            raise ValueError(
                "mailto is required for Crossref API. "
                "Set CROSSREF_MAILTO environment variable or "
                "create ~/.config/crossref-mcp/config.json with mailto field."
            )

        self.mailto = mailto
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=timeout,
        )

    @staticmethod
    def _load_mailto() -> str | None:
        """Load mailto from environment or config file."""
        import os

        # Try environment variable first
        mailto = os.environ.get("CROSSREF_MAILTO")
        if mailto:
            return mailto

        # Try config file
        config_file = Path.home() / ".config" / "crossref-mcp" / "config.json"
        if config_file.exists():
            try:
                config = json.loads(config_file.read_text())
                return config.get("mailto")
            except (json.JSONDecodeError, IOError):
                pass

        return None

    def _handle_response(self, resp: httpx.Response) -> dict:
        if resp.status_code == 429:
            retry_after_raw = resp.headers.get("Retry-After")
            retry_after = int(retry_after_raw) if retry_after_raw else None
            raise RateLimitError(retry_after)
        if resp.status_code == 404:
            raise NotFoundError(f"Not found: {resp.url}")
        if resp.status_code >= 400:
            raise APIError(f"API error {resp.status_code}: {resp.text}")
        return resp.json()

    def _compute_confidence_score(
        self,
        result: dict,
        query_author: str | None = None,
        query_title: str | None = None,
        query_year: int | None = None,
    ) -> int:
        """Compute confidence score for a search result.

        Rubric:
        - author match: +3
        - year match: +2
        - title keywords overlap: +2
        - has DOI: +1
        - is journal-article: +1
        """
        score = 0

        # Author match
        if query_author:
            authors = result.get("author", [])
            author_names = " ".join(
                f"{a.get('family', '')} {a.get('given', '')}".strip() for a in authors
            )
            if query_author.lower() in author_names.lower():
                score += 3

        # Year match
        if query_year:
            pub_year = result.get("published", {})
            if isinstance(pub_year, dict):
                year = pub_year.get("date-parts")
                if year and isinstance(year, list) and year[0]:
                    if year[0][0] == query_year:
                        score += 2
            elif isinstance(pub_year, str):
                try:
                    if int(pub_year[:4]) == query_year:
                        score += 2
                except (ValueError, IndexError):
                    pass

        # Title keywords overlap
        if query_title:
            result_title = result.get("title", [""])[0] if result.get("title") else ""
            if result_title:
                query_words = set(query_title.lower().split())
                result_words = set(result_title.lower().split())
                # Remove common stopwords
                stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
                query_words -= stopwords
                result_words -= stopwords
                if query_words and result_words:
                    overlap = len(query_words & result_words)
                    if overlap >= 2:
                        score += 2

        # Has DOI
        if result.get("DOI"):
            score += 1

        # Is journal-article
        if result.get("type") == "journal-article":
            score += 1

        return score

    def search(
        self,
        query: str | None = None,
        *,
        author: str | None = None,
        title: str | None = None,
        year: int | None = None,
        work_type: str | None = None,
        rows: int = 5,
    ) -> list[dict]:
        """Search Crossref for works.

        Args:
            query: Free-text search query.
            author: Filter by author name.
            title: Filter by title.
            year: Filter by publication year.
            work_type: Filter by work type (e.g., "journal-article", "book").
            rows: Maximum number of results to return.

        Returns:
            List of work objects with computed confidence scores.
        """
        params = {
            "mailto": self.mailto,
            "rows": rows,
        }

        if query:
            params["query.bibliographic"] = query
        if author:
            params["query.author"] = author
        if title:
            params["query.title"] = title
        if year:
            params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"
        if work_type:
            if year:
                params["filter"] += f",type:{work_type}"
            else:
                params["filter"] = f"type:{work_type}"

        resp = self._client.get("/works", params=params)
        data = self._handle_response(resp)

        results = []
        for item in data.get("message", {}).get("items", []):
            # Compute confidence score
            item["confidence_score"] = self._compute_confidence_score(
                item, query_author=author, query_title=title, query_year=year
            )

            # Extract relevant fields
            extracted = {
                "title": item.get("title", [""])[0] if item.get("title") else "",
                "authors": item.get("author", []),
                "year": item.get("published", {}).get("date-parts", [[None]])[0][0]
                if item.get("published", {}).get("date-parts")
                else None,
                "journal": item.get("container-title", [""])[0]
                if item.get("container-title")
                else "",
                "volume": item.get("volume"),
                "issue": item.get("issue"),
                "pages": item.get("page"),
                "doi": item.get("DOI"),
                "type": item.get("type"),
                "confidence_score": item["confidence_score"],
            }
            results.append(extracted)

        return results

    def get_metadata(self, doi: str) -> dict:
        """Retrieve full metadata for a work by DOI.

        Args:
            doi: Digital Object Identifier.

        Returns:
            Full work metadata object.
        """
        params = {"mailto": self.mailto}
        resp = self._client.get(f"/works/{doi}", params=params)
        data = self._handle_response(resp)
        return data.get("message", {})

    def get_bibtex(self, doi: str) -> str:
        """Retrieve BibTeX citation for a work.

        Args:
            doi: Digital Object Identifier.

        Returns:
            BibTeX string.
        """
        # Try Crossref transform endpoint first
        try:
            headers = {"Accept": "application/x-bibtex"}
            resp = self._client.get(
                f"/works/{doi}/transform/application/x-bibtex",
                headers=headers,
            )
            if resp.status_code == 200:
                return resp.text
        except Exception:
            pass

        # Fallback: try doi.org content negotiation
        try:
            doi_client = httpx.Client(timeout=30.0)
            headers = {"Accept": "application/x-bibtex"}
            resp = doi_client.get(f"https://doi.org/{doi}", headers=headers)
            if resp.status_code == 200:
                return resp.text
            doi_client.close()
        except Exception:
            pass

        raise ValueError(f"Could not retrieve BibTeX for {doi}")

    def find_published_version(
        self, title: str, author: str | None = None, working_paper_year: int | None = None
    ) -> dict | None:
        """Find published version of a working paper.

        Args:
            title: Title of the working paper.
            author: Primary author name.
            working_paper_year: Year the working paper was published.

        Returns:
            Best match metadata + bibtex if found and confidence is high, else None.
        """
        # Search for journal articles matching the title
        results = self.search(
            title=title,
            author=author,
            work_type="journal-article",
            rows=10,
        )

        if not results:
            return None

        # Compute title similarity (normalized token overlap)
        def title_similarity(title1: str, title2: str) -> float:
            """Compute Jaccard similarity of title tokens."""
            words1 = set(title1.lower().split())
            words2 = set(title2.lower().split())
            # Remove common stopwords
            stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
            words1 -= stopwords
            words2 -= stopwords
            if not words1 or not words2:
                return 0.0
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            return intersection / union if union > 0 else 0.0

        best_match = None
        best_similarity = 0.0

        for result in results:
            sim = title_similarity(title, result["title"])
            if sim > best_similarity:
                best_similarity = sim
                best_match = result

        # Only return if similarity is high enough (>0.5) and has DOI
        if best_similarity > 0.5 and best_match and best_match.get("doi"):
            try:
                bibtex = self.get_bibtex(best_match["doi"])
                best_match["bibtex"] = bibtex
            except Exception:
                pass
            return best_match

        return None
