import httpx
import pytest
import respx

from crossref_mcp.client import (
    CrossRefClient,
    RateLimitError,
    NotFoundError,
    APIError,
)
from .conftest import (
    SEARCH_RESPONSE,
    SEARCH_EMPTY_RESPONSE,
    GET_METADATA_RESPONSE,
    CONLEY_BIBTEX,
)

BASE = "https://api.crossref.org"


class TestSearch:
    @respx.mock
    def test_search_returns_works(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        results = client.search(query="Conley Udry pineapple")

        assert len(results) == 1
        assert results[0]["title"] == "Learning about a New Technology: Pineapple in Ghana"
        assert results[0]["year"] == 2010
        assert "confidence_score" in results[0]

    @respx.mock
    def test_search_sends_correct_params(self):
        route = respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        client.search(
            query="Conley Udry",
            author="Conley",
            title="Pineapple",
            year=2010,
            rows=3,
        )

        request = route.calls[0].request
        assert "query.bibliographic=Conley+Udry" in str(request.url) or "query.bibliographic=Conley%20Udry" in str(request.url)
        assert "query.author=Conley" in str(request.url)
        assert "query.title=Pineapple" in str(request.url)
        assert "filter=" in str(request.url)
        assert "rows=3" in str(request.url)
        assert "mailto=test%40example.com" in str(request.url)

    @respx.mock
    def test_search_empty_results(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_EMPTY_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        results = client.search(query="nonexistent paper xyz")
        assert results == []

    @respx.mock
    def test_search_with_work_type_filter(self):
        route = respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        client.search(query="test", work_type="journal-article")

        request = route.calls[0].request
        assert "type%3Ajournal-article" in str(request.url) or "type:journal-article" in str(request.url)

    @respx.mock
    def test_confidence_score_with_author_match(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        results = client.search(query="test", author="Conley")

        # Author match +3
        assert results[0]["confidence_score"] >= 3

    @respx.mock
    def test_confidence_score_with_year_match(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        results = client.search(query="test", year=2010)

        # Year match +2
        assert results[0]["confidence_score"] >= 2

    @respx.mock
    def test_confidence_score_has_doi(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        results = client.search(query="test")

        # Has DOI +1
        assert results[0]["confidence_score"] >= 1

    @respx.mock
    def test_confidence_score_journal_article(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        results = client.search(query="test")

        # Is journal-article +1
        assert results[0]["confidence_score"] >= 1


class TestGetMetadata:
    @respx.mock
    def test_get_metadata_by_doi(self):
        respx.get(f"{BASE}/works/10.1257/aer.100.1.35").mock(
            return_value=httpx.Response(200, json=GET_METADATA_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        result = client.get_metadata("10.1257/aer.100.1.35")

        assert result["title"][0] == "Learning about a New Technology: Pineapple in Ghana"
        assert result["DOI"] == "10.1257/aer.100.1.35"

    @respx.mock
    def test_get_metadata_sends_mailto(self):
        route = respx.get(f"{BASE}/works/10.1257/aer.100.1.35").mock(
            return_value=httpx.Response(200, json=GET_METADATA_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        client.get_metadata("10.1257/aer.100.1.35")

        request = route.calls[0].request
        assert "mailto=test%40example.com" in str(request.url)


class TestGetBibtex:
    @respx.mock
    def test_get_bibtex_from_transform_endpoint(self):
        respx.get(f"{BASE}/works/10.1257/aer.100.1.35/transform/application/x-bibtex").mock(
            return_value=httpx.Response(200, text=CONLEY_BIBTEX)
        )
        client = CrossRefClient(mailto="test@example.com")
        result = client.get_bibtex("10.1257/aer.100.1.35")

        assert isinstance(result, str)
        assert "@article{" in result
        assert "Conley" in result

    @respx.mock
    def test_get_bibtex_fallback_to_doi_org(self):
        # Mock the transform endpoint to fail
        respx.get(f"{BASE}/works/10.1257/aer.100.1.35/transform/application/x-bibtex").mock(
            return_value=httpx.Response(406)
        )
        # Mock the doi.org endpoint
        respx.get("https://doi.org/10.1257/aer.100.1.35").mock(
            return_value=httpx.Response(200, text=CONLEY_BIBTEX)
        )
        client = CrossRefClient(mailto="test@example.com")
        result = client.get_bibtex("10.1257/aer.100.1.35")

        assert "@article{" in result

    @respx.mock
    def test_get_bibtex_raises_on_failure(self):
        respx.get(f"{BASE}/works/10.1257/aer.100.1.35/transform/application/x-bibtex").mock(
            return_value=httpx.Response(406)
        )
        respx.get("https://doi.org/10.1257/aer.100.1.35").mock(
            return_value=httpx.Response(406)
        )
        client = CrossRefClient(mailto="test@example.com")
        with pytest.raises(ValueError, match="Could not retrieve BibTeX"):
            client.get_bibtex("10.1257/aer.100.1.35")


class TestFindPublishedVersion:
    @respx.mock
    def test_find_published_version_high_similarity(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_RESPONSE)
        )
        respx.get(
            f"{BASE}/works/10.1257/aer.100.1.35/transform/application/x-bibtex"
        ).mock(return_value=httpx.Response(200, text=CONLEY_BIBTEX))

        client = CrossRefClient(mailto="test@example.com")
        result = client.find_published_version(
            title="Learning about a New Technology: Pineapple in Ghana",
            author="Conley",
        )

        assert result is not None
        assert result["doi"] == "10.1257/aer.100.1.35"
        assert "bibtex" in result

    @respx.mock
    def test_find_published_version_no_results(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_EMPTY_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        result = client.find_published_version(
            title="Nonexistent paper xyz"
        )

        assert result is None

    @respx.mock
    def test_find_published_version_low_similarity(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(200, json=SEARCH_RESPONSE)
        )
        client = CrossRefClient(mailto="test@example.com")
        result = client.find_published_version(
            title="Completely different title that has no overlap whatsoever"
        )

        assert result is None


class TestErrorHandling:
    @respx.mock
    def test_rate_limit_raises(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(429, headers={"Retry-After": "30"})
        )
        client = CrossRefClient(mailto="test@example.com")
        with pytest.raises(RateLimitError) as exc_info:
            client.search(query="test")
        assert exc_info.value.retry_after == 30

    @respx.mock
    def test_rate_limit_without_retry_header(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(429)
        )
        client = CrossRefClient(mailto="test@example.com")
        with pytest.raises(RateLimitError) as exc_info:
            client.search(query="test")
        assert exc_info.value.retry_after is None

    @respx.mock
    def test_not_found_raises(self):
        respx.get(f"{BASE}/works/invalid-doi").mock(
            return_value=httpx.Response(404, json={"error": "Work not found"})
        )
        client = CrossRefClient(mailto="test@example.com")
        with pytest.raises(NotFoundError):
            client.get_metadata("invalid-doi")

    @respx.mock
    def test_server_error(self):
        respx.get(f"{BASE}/works").mock(
            return_value=httpx.Response(500)
        )
        client = CrossRefClient(mailto="test@example.com")
        with pytest.raises(APIError):
            client.search(query="test")

    def test_missing_mailto_raises(self):
        with pytest.raises(ValueError, match="mailto is required"):
            CrossRefClient(mailto=None)


class TestConfigLoading:
    def test_mailto_from_env(self, monkeypatch):
        monkeypatch.setenv("CROSSREF_MAILTO", "env@example.com")
        client = CrossRefClient()
        assert client.mailto == "env@example.com"
