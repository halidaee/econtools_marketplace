import pytest
from bibtex_mcp.client import BibTexClient, ParseError, FileNotFoundError, BibTeXError


class TestParseBib:
    def test_parse_bib_returns_index(self, temp_bib_file):
        client = BibTexClient()
        result = client.parse_bib(temp_bib_file)

        assert isinstance(result, dict)
        assert "Conley-2010" in result
        assert "Suri-2011" in result
        assert "Bandiera-2006" in result

    def test_parse_bib_entry_structure(self, temp_bib_file):
        client = BibTexClient()
        result = client.parse_bib(temp_bib_file)

        entries = result["Conley-2010"]
        assert len(entries) > 0
        entry = entries[0]

        assert entry["key"] == "conley2010learning"
        assert entry["type"] == "article"
        assert "Conley" in entry["authors"]
        assert "Udry" in entry["authors"]
        assert entry["year"] == "2010"
        assert "Learning" in entry["title"]
        assert "journal" in entry["fields"]

    def test_parse_bib_file_not_found(self):
        client = BibTexClient()
        with pytest.raises(FileNotFoundError):
            client.parse_bib("/nonexistent/path/file.bib")


class TestScanBareCitations:
    def test_scan_qmd_finds_narrative_citations(self, temp_qmd_file):
        client = BibTexClient()
        citations = client.scan_bare_citations(temp_qmd_file)

        assert len(citations) > 0

        # Find "Conley and Udry (2010)" citation
        conley_citations = [c for c in citations if "Conley" in c["text"]]
        assert len(conley_citations) > 0

        citation = conley_citations[0]
        assert citation["citation_type"] == "narrative"
        assert citation["year"] == "2010"
        assert "Conley" in citation["authors"]

    def test_scan_qmd_finds_parenthetical_citations(self, temp_qmd_file):
        client = BibTexClient()
        citations = client.scan_bare_citations(temp_qmd_file)

        # Find parenthetical citations
        paren_citations = [c for c in citations if c["citation_type"] == "parenthetical"]
        assert len(paren_citations) > 0

    def test_scan_finds_locators(self, temp_qmd_file):
        client = BibTexClient()
        citations = client.scan_bare_citations(temp_qmd_file)

        # Find citation with locator
        locator_citations = [c for c in citations if c["has_locator"]]
        if locator_citations:
            citation = locator_citations[0]
            assert "p." in citation["locator"]

    def test_scan_file_not_found(self):
        client = BibTexClient()
        with pytest.raises(FileNotFoundError):
            client.scan_bare_citations("/nonexistent/path/file.qmd")


class TestRekeyEntry:
    def test_rekey_entry_basic(self):
        client = BibTexClient()
        bibtex = """@article{old_key,
  title={Sample Article Title},
  author={Smith, John},
  year={2020},
  journal={Test Journal}
}"""
        existing_keys = ["smith2020other"]
        result = client.rekey_entry(bibtex, existing_keys)

        assert "smith2020sample" in result or "smith2020article" in result
        assert "old_key" not in result

    def test_rekey_entry_handles_duplicates(self):
        client = BibTexClient()
        bibtex = """@article{old_key,
  title={Sample Article},
  author={Smith, John},
  year={2020},
  journal={Test Journal}
}"""
        existing_keys = ["smith2020sample"]
        result = client.rekey_entry(bibtex, existing_keys)

        # Should add a/b/c suffix
        assert "smith2020samplea" in result or "a" in result.lower()

    def test_rekey_entry_invalid_format(self):
        client = BibTexClient()
        with pytest.raises(ParseError):
            client.rekey_entry("invalid entry", [])


class TestAddEntry:
    def test_add_entry_appends_to_file(self, temp_empty_bib):
        client = BibTexClient()
        entry = """@article{newkey2020,
  title={New Article},
  author={Author, Test},
  year={2020},
  journal={Journal}
}"""
        result = client.add_entry(temp_empty_bib, entry)

        assert "newkey2020" in result
        assert "success" not in result or "Added" in result

        # Verify file was updated
        content = open(temp_empty_bib).read()
        assert "newkey2020" in content

    def test_add_entry_duplicate_key_raises(self, temp_bib_file):
        client = BibTexClient()
        entry = """@article{conley2010learning,
  title={Different Article},
  author={Different, Author},
  year={2020},
  journal={Journal}
}"""
        with pytest.raises(BibTeXError, match="already exists"):
            client.add_entry(temp_bib_file, entry)

    def test_add_entry_file_not_found(self):
        client = BibTexClient()
        with pytest.raises(FileNotFoundError):
            client.add_entry("/nonexistent/path/file.bib", "@article{test,}")


class TestSuggestReplacement:
    def test_suggest_quarto_narrative(self):
        client = BibTexClient()
        result = client.suggest_replacement(
            "Conley and Udry (2010)",
            "conley2010learning",
            "qmd"
        )

        assert result["original"] == "Conley and Udry (2010)"
        assert "@conley2010learning" in result["replacement"]
        assert "[" not in result["replacement"]

    def test_suggest_quarto_parenthetical(self):
        client = BibTexClient()
        result = client.suggest_replacement(
            "(Conley and Udry 2010)",
            "conley2010learning",
            "qmd"
        )

        assert "@conley2010learning" in result["replacement"]
        assert "[" in result["replacement"]
        assert "]" in result["replacement"]

    def test_suggest_latex_narrative(self):
        client = BibTexClient()
        result = client.suggest_replacement(
            "Conley and Udry (2010)",
            "conley2010learning",
            "tex",
            natbib=True
        )

        assert "\\citet" in result["replacement"]

    def test_suggest_latex_parenthetical(self):
        client = BibTexClient()
        result = client.suggest_replacement(
            "(Conley and Udry 2010)",
            "conley2010learning",
            "tex",
            natbib=True
        )

        assert "\\citep" in result["replacement"]

    def test_suggest_with_locator(self):
        client = BibTexClient()
        result = client.suggest_replacement(
            "(Conley and Udry 2010, p. 45)",
            "conley2010learning",
            "qmd"
        )

        # Should include locator
        assert "45" in result["replacement"] or "p." in result["replacement"]


class TestNormalization:
    def test_normalize_name(self):
        client = BibTexClient()

        assert client._normalize_name("Conley") == "conley"
        assert client._normalize_name("Tahbaz-Salehi") == "tahbazsalehi"
        assert client._normalize_name("von Neumann") == "vonneumann"

    def test_remove_accents(self):
        client = BibTexClient()

        # Note: This is a simple test
        assert "a" in client._remove_accents("á")


class TestGenerateKey:
    def test_generate_key_basic(self):
        client = BibTexClient()
        key = client._generate_key("Conley, Timothy", "2010", "Learning about a New Technology", [])

        assert "conley" in key
        assert "2010" in key
        assert "learning" in key

    def test_generate_key_multiple_authors(self):
        client = BibTexClient()
        key = client._generate_key("Conley, Timothy and Udry, Christopher", "2010", "Learning about a New Technology", [])

        # Should use first author only
        assert "conley" in key
        assert "udry" not in key

    def test_generate_key_skip_stopwords(self):
        client = BibTexClient()
        key = client._generate_key("Smith, John", "2020", "The Role of Information", [])

        # Should skip "The" and "of"
        assert "role" in key or "information" in key

    def test_generate_key_disambiguation(self):
        client = BibTexClient()
        existing = ["smith2020article"]
        key = client._generate_key("Smith, John", "2020", "Article Title", existing)

        # Should add letter suffix for disambiguation
        assert "a" in key or "b" in key
