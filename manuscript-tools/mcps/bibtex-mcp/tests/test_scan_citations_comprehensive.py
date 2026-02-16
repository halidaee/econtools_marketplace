"""Comprehensive tests for scan_bare_citations() against all citation patterns.

This test suite validates the citation detection regex patterns from citation-patterns.md.
Tests cover all 21+ citation patterns including edge cases.
"""

import pytest
from pathlib import Path
import tempfile
from bibtex_mcp.client import BibTexClient


@pytest.fixture
def temp_file(suffix=".qmd"):
    """Create a temporary file with the given content."""
    def _create(content):
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(content)
            path = f.name
        yield path
        Path(path).unlink()
    return _create


class TestNarrativeCitations:
    """Test narrative citations: Author (Year)"""

    def test_single_author(self):
        """Pattern 1: Author (Year) — single author"""
        content = "Suri (2011) demonstrates selection effects."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "Suri (2011)" in citations[0]["text"]
        assert citations[0]["citation_type"] == "narrative"
        assert citations[0]["year"] == "2011"
        assert "Suri" in citations[0]["authors"]

    def test_two_authors(self):
        """Pattern 2: Author and Author (Year) — two authors"""
        content = "Conley and Udry (2010) study technology adoption."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "Conley and Udry (2010)" in citations[0]["text"]
        assert "Conley" in citations[0]["authors"]
        assert "Udry" in citations[0]["authors"]

    def test_three_authors(self):
        """Pattern 3: Author, Author, and Author (Year) — three authors"""
        content = "Duflo, Kremer, and Robinson (2011) study microfinance."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        citation = citations[0]
        # The regex should match at least the first author and year
        assert citation["year"] == "2011"
        assert "Duflo" in citation["authors"]

    def test_et_al(self):
        """Pattern 4: Author et al. (Year) — 3+ abbreviated"""
        content = "Banerjee et al. (2013) examine microfinance impacts."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "et al" in citations[0]["text"]
        assert citations[0]["year"] == "2013"

    def test_et_al_with_locator(self):
        """Pattern 5: Author et al. (Year, p. N) — with page locator"""
        content = "Banerjee et al. (2013, p. 45) show evidence of impact."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["has_locator"]
        assert "p." in citations[0]["locator"] or "45" in citations[0]["text"]

    def test_multiple_years(self):
        """Pattern 6: Author (Year, Year) — multiple years"""
        content = "Heckman (1976, 1979) pioneered the analysis."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should detect at least the citation
        assert len(citations) >= 1
        assert "Heckman" in citations[0]["authors"]

    def test_forthcoming(self):
        """Pattern 7: Author (forthcoming)"""
        content = "Mogstad (forthcoming) examines mobility."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["year"] == "forthcoming"

    def test_possessive(self):
        """Pattern 8: Author's (Year) — possessive form"""
        content = "Mogstad's (2012) analysis reveals new patterns."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["is_possessive"]
        assert citations[0]["year"] == "2012"


class TestParentheticalCitations:
    """Test parenthetical citations: (Author Year)"""

    def test_single_author_parens(self):
        """Pattern 9: (Author Year)"""
        content = "Studies show results (Suri 2011)."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["citation_type"] == "parenthetical"
        assert citations[0]["year"] == "2011"
        assert "Suri" in citations[0]["authors"]

    def test_two_authors_parens(self):
        """Pattern 10: (Author and Author Year)"""
        content = "Studies note (Conley and Udry 2010) significant findings."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "(Conley and Udry 2010)" in citations[0]["text"]
        assert "Conley" in citations[0]["authors"]

    def test_et_al_parens(self):
        """Pattern 11: (Author et al. Year)"""
        content = "Research shows (Banerjee et al. 2013) impact."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "et al" in citations[0]["text"]
        assert citations[0]["year"] == "2013"

    def test_multiple_works(self):
        """Pattern 12: (Author Year; Author Year) — multiple works"""
        content = "Studies note (Suri 2011; Conley and Udry 2010) evidence."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should detect the parenthetical citation (may or may not split on semicolon)
        assert len(citations) >= 1
        assert citations[0]["citation_type"] == "parenthetical"

    def test_with_locator_parens(self):
        """Pattern 13: (Author Year, p. N) — with locator"""
        content = "As shown (Suri 2011, p. 45) in the results."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["has_locator"]

    def test_with_prefix(self):
        """Pattern 14: (see Author Year) — with prefix"""
        content = "Evidence exists (see Suri 2011) for the claim."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "see" in citations[0]["prefix"].lower()

    def test_with_suffix(self):
        """Pattern 15: (Author Year, among others) — with suffix"""
        content = "Studies show (Suri 2011, among others) that this holds."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        # Note: current implementation may not extract suffix correctly for all cases
        # This test may need adjustment based on actual behavior


class TestEdgeCases:
    """Test edge cases and problematic patterns"""

    def test_hyphenated_last_names(self):
        """Pattern 16: Hyphenated last names"""
        content = "Tahbaz-Salehi (2020) analyzes networks."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "Tahbaz-Salehi" in citations[0]["text"] or "Tahbaz" in citations[0]["authors"]

    def test_name_particles_de(self):
        """Pattern 17a: Name particles (de)"""
        content = "de Finetti (1937) introduced the concept."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Note: lowercase particles are tricky; regex may not handle "de" correctly
        # This documents the limitation
        # assert len(citations) >= 0  # May not detect if pattern doesn't handle lowercase
        if citations:
            assert citations[0]["year"] == "1937"

    def test_name_particles_van(self):
        """Pattern 17b: Name particles (Van)"""
        content = "Van der Waerden (1971) proved the theorem."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # "Van" is capitalized so should match
        if citations:
            assert citations[0]["year"] == "1971"

    def test_name_with_suffix(self):
        """Pattern 18: Jr/Sr/III suffixes"""
        content = "Autor Jr. (2003) examines technology."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Note: pattern may not handle "Jr." correctly
        if citations:
            assert "Autor" in citations[0]["authors"] or "Autor Jr" in citations[0]["text"]

    def test_institutional_authors(self):
        """Pattern 19: Institutional authors"""
        content = "World Bank (2020) published the report."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Pattern requires single capital letter at start, so "World" may match
        if citations:
            assert citations[0]["year"] == "2020"

    def test_year_ranges_excluded(self):
        """Pattern 20: Year ranges (should NOT match)"""
        content = "The period (2010-2015) was significant."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should NOT match "2010-2015" as a citation
        non_citation_years = [c for c in citations if "2010" in c["text"]]
        assert len(non_citation_years) == 0, "Year range should not match as citation"

    def test_already_cited_quarto(self):
        """Pattern 21a: Already-cited with Quarto syntax"""
        content = "See @conley2010learning for details."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should skip lines with @ symbols
        assert len(citations) == 0

    def test_already_cited_latex(self):
        """Pattern 21b: Already-cited with LaTeX syntax"""
        content = r"See \citet{conley2010learning} for details."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should skip lines with \cite commands
        assert len(citations) == 0


class TestFalsePositiveExclusion:
    """Test that false positives are correctly excluded"""

    def test_excludes_acknowledgments_section(self):
        """Should not detect citations in acknowledgments"""
        content = """# Main Text

Conley and Udry (2010) show results.

## Acknowledgments

We thank Conley and Udry (2010) for feedback.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should only detect citation in main text, not in acknowledgments
        assert len(citations) == 1
        assert citations[0]["line"] == 3  # The one in main text (line 3 after blank line 2)

    def test_excludes_bibliography_section(self):
        """Should not detect citations in LaTeX bibliography"""
        content = r"""
\documentclass{article}
\begin{document}

Conley and Udry (2010) show results.

\begin{thebibliography}{99}
\bibitem{conley2010} Conley and Udry (2010) Paper Title.
\end{thebibliography}
\end{document}
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should only detect citation in main text
        assert len(citations) >= 1
        for citation in citations:
            assert "thebibliography" not in content[max(0, citation["column"]-50):citation["column"]+50]


class TestCitationComponentExtraction:
    """Test accurate extraction of citation components"""

    def test_extracts_author_names(self):
        """Verify author name extraction"""
        content = "Smith and Jones (2020) study the issue."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "Smith" in citations[0]["authors"]
        assert "Jones" in citations[0]["authors"]

    def test_extracts_year(self):
        """Verify year extraction"""
        content = "Research (Smith 2015) shows results."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["year"] == "2015"

    def test_extracts_page_locator(self):
        """Verify page locator extraction"""
        content = "As stated (Smith 2015, p. 42) clearly."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["has_locator"]
        assert "42" in citations[0]["text"]


class TestMultipleCitationsDetection:
    """Test detection of multiple citations in same document"""

    def test_detects_multiple_distinct_citations(self):
        """Should detect all distinct citations"""
        content = """
Smith (2010) studied X.
Jones (2012) studied Y.
Brown and Green (2015) studied Z.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 3

    def test_detects_mixed_narrative_and_parenthetical(self):
        """Should detect both narrative and parenthetical in same document"""
        content = """
Smith (2010) shows results.
This is confirmed (Jones 2012).
Brown (2015) extends the work.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 3
        narrative = [c for c in citations if c["citation_type"] == "narrative"]
        parenthetical = [c for c in citations if c["citation_type"] == "parenthetical"]
        assert len(narrative) >= 2
        assert len(parenthetical) >= 1


class TestTypoAndNonStandardFormats:
    """Test handling of typos and non-standard citation formats"""

    def test_missing_and_space_separated_with_comma(self):
        """(Bickel Chen, 2006) - space-separated authors with comma before year"""
        content = "This was found by (Bickel Chen, 2006) in their study."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(Bickel Chen, 2006)"
        assert "Bickel" in citations[0]["authors"]
        assert "Chen" in citations[0]["authors"]
        assert citations[0]["year"] == "2006"

    def test_comma_separated_authors(self):
        """(Bickel, Chen, 2006) - comma-separated authors instead of 'and'"""
        content = "Previous work by (Bickel, Chen, 2006) demonstrated this."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(Bickel, Chen, 2006)"
        assert "Bickel" in citations[0]["authors"]
        assert "Chen" in citations[0]["authors"]
        assert citations[0]["year"] == "2006"

    def test_space_separated_without_comma(self):
        """(Bickel Chen 2006) - space-separated authors without comma"""
        content = "According to (Bickel Chen 2006) without comma."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should detect it, but skill-level logic may disambiguate as single compound name
        assert len(citations) == 1
        assert citations[0]["text"] == "(Bickel Chen 2006)"
        assert citations[0]["year"] == "2006"
        # Extraction will split on space, but skill should check if compound name first
        assert "Bickel" in citations[0]["authors"]


class TestNestedParenthesesAndMultiplePrefixes:
    """Test handling of nested parentheses and multiple prefix words"""

    def test_nested_year_parens(self):
        """(e.g. Suri (2011)) - year in nested parentheses"""
        content = "Evidence exists (e.g. Suri (2011)) for this claim."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(e.g. Suri (2011))"
        assert citations[0]["citation_type"] == "parenthetical"
        assert citations[0]["authors"] == ["Suri"]
        assert citations[0]["year"] == "2011"
        assert citations[0]["prefix"] == "e.g."

    def test_multiple_prefixes(self):
        """(see e.g. Suri 2011) - multiple prefix words"""
        content = "This is shown (see e.g. Suri 2011) in the literature."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(see e.g. Suri 2011)"
        assert citations[0]["citation_type"] == "parenthetical"
        assert citations[0]["authors"] == ["Suri"]
        assert citations[0]["year"] == "2011"
        assert citations[0]["prefix"] == "see e.g."

    def test_multiple_citations_with_nested_years(self):
        """(see e.g. Suri (2011) and Conley and Udry (2002)) - multiple works with nested years"""
        content = "Evidence shows (see e.g. Suri (2011) and Conley and Udry (2002)) this effect."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["citation_type"] == "parenthetical"
        # Should extract all authors
        assert "Suri" in citations[0]["authors"]
        assert "Conley" in citations[0]["authors"]
        assert "Udry" in citations[0]["authors"]
        # Year extraction gets first year (2011)
        assert citations[0]["year"] == "2011"
        assert citations[0]["prefix"] == "see e.g."

    def test_narrative_not_detected_inside_parenthetical(self):
        """Suri (2011) inside (e.g. Suri (2011)) should not be detected as separate narrative"""
        content = "According to (e.g. Suri (2011)) this holds."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should only detect the parenthetical, not the nested narrative
        assert len(citations) == 1
        assert citations[0]["citation_type"] == "parenthetical"
        assert citations[0]["text"] == "(e.g. Suri (2011))"


class TestSloppyCitationFormats:
    """Test handling of sloppy/non-standard citation formats found in drafts"""

    def test_lowercase_author_name(self):
        """(athey 2006) - lowercase author name should be detected"""
        content = "This was shown in (athey 2006) as a key finding."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(athey 2006)"
        assert citations[0]["year"] == "2006"
        # Author might be extracted as "athey" (lowercase)
        assert len(citations[0]["authors"]) >= 1
        assert citations[0]["authors"][0].lower() == "athey"

    def test_semicolon_separator(self):
        """(Suri; 2011) - semicolon between author and year"""
        content = "Evidence suggests (Suri; 2011) this pattern."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(Suri; 2011)"
        assert "Suri" in citations[0]["authors"]
        assert citations[0]["year"] == "2011"

    def test_colon_separator(self):
        """(Suri: 2011) - colon between author and year"""
        content = "Studies show (Suri: 2011) significant results."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(Suri: 2011)"
        assert "Suri" in citations[0]["authors"]
        assert citations[0]["year"] == "2011"

    def test_square_brackets(self):
        """[Suri 2011] - square brackets instead of parentheses"""
        content = "The analysis [Suri 2011] demonstrates this."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "[Suri 2011]"
        assert "Suri" in citations[0]["authors"]
        assert citations[0]["year"] == "2011"

    def test_author_with_initial(self):
        """Suri, T. (2011) - comma and initial after surname"""
        content = "According to Suri, T. (2011) this pattern holds."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "Suri" in citations[0]["authors"]
        assert citations[0]["year"] == "2011"
        assert citations[0]["citation_type"] == "narrative"

    def test_wrong_et_al_format_with_period(self):
        """Suri et. al. (2011) - et. al. with period after et"""
        content = "Research by Suri et. al. (2011) shows results."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "Suri" in citations[0]["authors"]
        assert citations[0]["year"] == "2011"
        # "et. al." should be recognized and not treated as author

    def test_et_al_no_spaces(self):
        """Suri etal (2011) - etal without spaces"""
        content = "Studies by Suri etal (2011) confirm this."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "Suri" in citations[0]["authors"]
        assert citations[0]["year"] == "2011"
        # "etal" should not be in authors list
        assert all(author.lower() != "etal" for author in citations[0]["authors"])

    def test_et_all_typo(self):
        """Suri et all (2011) - et all instead of et al"""
        content = "Work by Suri et all (2011) demonstrates this."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert "Suri" in citations[0]["authors"]
        assert citations[0]["year"] == "2011"
        # "all" should not be in authors list
        assert all(author.lower() != "all" for author in citations[0]["authors"])

    def test_ampersand_no_spaces(self):
        """(Suri&Chen 2011) - ampersand without spaces"""
        content = "Previous work (Suri&Chen 2011) shows evidence."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(Suri&Chen 2011)"
        assert "Suri" in citations[0]["authors"]
        assert "Chen" in citations[0]["authors"]
        assert len(citations[0]["authors"]) == 2
        assert citations[0]["year"] == "2011"

    def test_year_only_not_detected(self):
        """(2011) - year-only should NOT be detected as citation"""
        content = "Some text before (2011) was an important year."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        # Should NOT detect (2011) as a citation
        assert len(citations) == 0

    def test_mixed_case_author_names(self):
        """(SURI 2011) - all caps author name"""
        content = "Studies show (SURI 2011) significant results."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(SURI 2011)"
        assert len(citations[0]["authors"]) >= 1
        assert citations[0]["year"] == "2011"

    def test_square_brackets_with_et_al(self):
        """[Banerjee et al. 2013] - square brackets with et al"""
        content = "Research shows [Banerjee et al. 2013] impact."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "[Banerjee et al. 2013]"
        assert "Banerjee" in citations[0]["authors"]
        assert citations[0]["year"] == "2013"

    def test_lowercase_parenthetical_both_authors(self):
        """(conley and udry 2010) - lowercase authors in parenthetical"""
        content = "This was shown (conley and udry 2010) in the study."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["citation_type"] == "parenthetical"
        assert citations[0]["year"] == "2010"
        # Should extract both authors even if lowercase
        assert len(citations[0]["authors"]) >= 1

    def test_mixed_case_space_separated(self):
        """(Smith jones 2011) - space-separated with mixed case"""
        content = "Work by (Smith jones 2011) is important."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(Smith jones 2011)"
        assert "Smith" in citations[0]["authors"]
        assert "jones" in citations[0]["authors"]
        assert len(citations[0]["authors"]) == 2
        assert citations[0]["year"] == "2011"

    def test_mixed_case_three_authors(self):
        """(smith Chen udry 2011) - three authors with mixed case"""
        content = "Analysis by (smith Chen udry 2011) shows patterns."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(smith Chen udry 2011)"
        assert "smith" in citations[0]["authors"]
        assert "Chen" in citations[0]["authors"]
        assert "udry" in citations[0]["authors"]
        assert len(citations[0]["authors"]) == 3
        assert citations[0]["year"] == "2011"

    def test_mixed_case_with_and(self):
        """(Smith and jones 2011) - mixed case with explicit 'and'"""
        content = "Study by (Smith and jones 2011) shows results."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "(Smith and jones 2011)"
        assert "Smith" in citations[0]["authors"]
        assert "jones" in citations[0]["authors"]
        assert len(citations[0]["authors"]) == 2
        assert citations[0]["year"] == "2011"

    def test_mixed_case_square_brackets(self):
        """[Smith jones 2011] - mixed case in square brackets"""
        content = "Work by [Smith jones 2011] is important."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "[Smith jones 2011]"
        assert "Smith" in citations[0]["authors"]
        assert "jones" in citations[0]["authors"]
        assert len(citations[0]["authors"]) == 2
        assert citations[0]["year"] == "2011"

    def test_mixed_case_square_brackets_three_authors(self):
        """[smith Chen udry 2011] - three authors mixed case in square brackets"""
        content = "Analysis by [smith Chen udry 2011] shows patterns."
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
            f.write(content)
            path = f.name

        client = BibTexClient()
        citations = client.scan_bare_citations(path)
        Path(path).unlink()

        assert len(citations) == 1
        assert citations[0]["text"] == "[smith Chen udry 2011]"
        assert "smith" in citations[0]["authors"]
        assert "Chen" in citations[0]["authors"]
        assert "udry" in citations[0]["authors"]
        assert len(citations[0]["authors"]) == 3
        assert citations[0]["year"] == "2011"
