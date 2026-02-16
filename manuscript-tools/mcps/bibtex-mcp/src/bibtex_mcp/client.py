from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

from pybtex.database import parse_file


class BibTeXError(Exception):
    """Base error for BibTeX operations."""


class ParseError(BibTeXError):
    """Error parsing a file."""


class FileNotFoundError(BibTeXError):
    """File not found."""


class BibTexClient:
    # Citation detection patterns
    # Narrative: Author (Year) or Author (Year, p. N) or Author et al. (Year)
    # Handles: "Smith (2010)", "Smith and Jones (2010)", "Smith, Jones, and Brown (2010)"
    NARRATIVE_PATTERN = r"[A-Z][a-zA-Z'-]+(?:[-\s]+[a-z]+)*(?:(?:,\s+and|\s+and|,|\s+&)\s+[A-Z][a-zA-Z'-]+(?:[-\s]+[a-z]+)*)*(?:\s+et\s+al\.?)?\s*\((?:forthcoming|\d{4}[a-z]?)(?:,\s*(?:p+\.?|pp\.?|ch\.?)\s*\d+(?:\-\d+)?)?[^)]*\)"
    # Parenthetical: (Author Year) or (Author and Author Year) or (Author, Author, 2006) etc
    # Now supports: and, &, comma-separated, or space-separated authors (may need skill-level disambiguation)
    # Allows optional prefix like "(see Author Year)"
    PARENTHETICAL_PATTERN = r"\([^)]*?[A-Z][a-zA-Z'-]+(?:(?:\s+and\s+|\s+&\s+|,\s+|\s+(?=[A-Z]))[A-Z][a-zA-Z'-]+)*(?:\s+et\s+al\.?)?\s*,?\s*(?:forthcoming|\d{4}[a-z]?)[^)]*\)"

    # Stopwords to skip in title
    STOPWORDS = {"a", "an", "the", "on", "in", "at", "to", "for"}

    @staticmethod
    def _remove_accents(text: str) -> str:
        """Remove accents from text."""
        nfd = unicodedata.normalize("NFD", text)
        return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize a name for key generation."""
        # Remove accents
        name = BibTexClient._remove_accents(name)
        # Remove hyphens
        name = name.replace("-", "").replace(" ", "")
        # Lowercase
        return name.lower()

    def parse_bib(self, path: str) -> dict[str, list[dict]]:
        """Parse a .bib file and return a structured index.

        Args:
            path: Path to the .bib file

        Returns:
            Object mapping author-year keys to arrays of entries. Each entry contains:
            - key: The BibTeX key
            - type: Entry type
            - authors: Array of author last names
            - year: Publication year
            - title: Title
            - fields: All BibTeX fields as key-value pairs
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            bib_data = parse_file(str(file_path))
        except Exception as e:
            raise ParseError(f"Error parsing {path}: {e}")

        # Index by author-year
        index: dict[str, list[dict]] = {}

        for key, entry in bib_data.entries.items():
            authors = []
            if "author" in entry.persons:
                for person in entry.persons["author"]:
                    # Get last name
                    last_names = person.last_names
                    if last_names:
                        authors.append(last_names[0])

            year = entry.fields.get("year", "")
            author_year_key = f"{authors[0] if authors else 'unknown'}-{year}"

            entry_dict = {
                "key": key,
                "type": entry.type,
                "authors": authors,
                "year": year,
                "title": entry.fields.get("title", ""),
                "fields": dict(entry.fields),
            }

            if author_year_key not in index:
                index[author_year_key] = []
            index[author_year_key].append(entry_dict)

        return index

    def scan_bare_citations(self, path: str) -> list[dict]:
        """Scan a .qmd or .tex file for bare citations.

        Args:
            path: Path to the document file

        Returns:
            Array of detected citations, each containing:
            - text: The matched text
            - line: Line number
            - column: Column offset
            - authors: Extracted author last name(s)
            - year: Extracted year
            - citation_type: "narrative" or "parenthetical"
            - has_locator: Whether a page/chapter locator is present
            - locator: The locator text if present
            - prefix: Any prefix text
            - suffix: Any suffix text
            - is_possessive: Whether the citation uses possessive form
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content = file_path.read_text()
        lines = content.split("\n")
        citations = []

        in_acknowledgments = False
        in_bibliography = False

        for line_num, line in enumerate(lines, 1):
            # Check for acknowledgments section start (Markdown)
            if re.search(r"##\s+.*[Aa]cknowledg", line):
                in_acknowledgments = True
                # Continue past the heading itself
                continue

            # Check for acknowledgments section end (next ## heading that is NOT acknowledgments)
            if in_acknowledgments and re.search(r"##\s+", line):
                in_acknowledgments = False
                # Don't continue - process this heading line normally

            # Check for bibliography section (LaTeX)
            if re.search(r"\\begin\{thebibliography\}", line):
                in_bibliography = True
                continue

            if re.search(r"\\end\{thebibliography\}", line):
                in_bibliography = False
                continue

            # Skip lines in acknowledgments or bibliography
            if in_acknowledgments or in_bibliography:
                continue

            # Skip lines that already have citations
            if "@" in line or "\\cite" in line:
                continue

            # Find narrative citations
            for match in re.finditer(self.NARRATIVE_PATTERN, line):
                text = match.group(0)
                # Exclude year ranges like "Something (2010-2015)"
                if re.search(r"\(\d{4}\-\d{4}\)", text):
                    continue

                # Extract components - get all authors (handle "A, B, and C" format)
                # First, extract text before year
                year_paren_idx = text.find("(")
                author_text = text[:year_paren_idx].strip()

                authors = []
                # Extract author names - look for capitalized words
                # This handles various formats: "Smith", "Smith and Jones", "Smith, Jones, and Brown"
                for author_match in re.finditer(r"[A-Z][a-zA-Z'-]+(?:[-\s]+[a-z]+)*", author_text):
                    potential_author = author_match.group(0).strip()
                    # Clean up "and" suffix (e.g., "Conley and" -> "Conley")
                    if potential_author.endswith(" and"):
                        potential_author = potential_author[:-4].strip()
                    # Skip conjunctions and "et al"
                    if potential_author.lower() not in ["et", "al", "and", "&"]:
                        if potential_author not in authors:
                            authors.append(potential_author)

                year_match = re.search(r"\((\d{4}|forthcoming)", text)

                year = year_match.group(1) if year_match else ""

                # Check for possessive
                is_possessive = "'s" in text

                # Check for locator
                locator_match = re.search(r"(p+\.\s*\d+|pp\.\s*\d+-\d+|ch\.\s*\d+)", text, re.IGNORECASE)
                locator = locator_match.group(0) if locator_match else ""

                citations.append({
                    "text": text,
                    "line": line_num,
                    "column": match.start(),
                    "authors": authors,
                    "year": year,
                    "citation_type": "narrative",
                    "has_locator": bool(locator),
                    "locator": locator,
                    "prefix": "",
                    "suffix": "",
                    "is_possessive": is_possessive,
                })

            # Find parenthetical citations
            for match in re.finditer(self.PARENTHETICAL_PATTERN, line):
                text = match.group(0)
                content = text[1:-1]  # Remove outer parens

                # Exclude year ranges like (2010-2015)
                if re.match(r"^\d{4}\-\d{4}$", content.strip()):
                    continue

                # Extract prefix
                prefix_match = re.match(r"^(see|e\.g\.|i\.e\.|cf\.)\s+", content, re.IGNORECASE)
                prefix = prefix_match.group(1) if prefix_match else ""

                # Extract authors - handle multiple authors separated by and/&/commas/spaces
                # Remove "et al" first to avoid parsing it as an author
                content_clean = re.sub(r"\s+et\s+al\.?", "", content)

                # Split on "and", "&", commas, or space before capital letter
                # This handles: "Smith and Jones", "Smith, Jones,", "Smith Jones," (space-separated)
                parts = re.split(r"(?:\s+and\s+|\s+&\s+|,\s+|\s+(?=[A-Z]))", content_clean)
                authors = []
                for part in parts:
                    part = part.strip()
                    # Extract capitalized words (could be compound names)
                    for author_match in re.finditer(r"[A-Z][a-zA-Z'-]+(?:[-\s]+[a-z]+)*", part):
                        potential_author = author_match.group(0).strip()
                        # Skip the year and other non-author content
                        if not re.match(r"^\d{4}|forthcoming", potential_author) and potential_author.lower() not in ["et", "al"]:
                            if potential_author not in authors:
                                authors.append(potential_author)
                                # Only take the first capitalized sequence from each author section
                                break

                # Extract year
                year_match = re.search(r"(\d{4}|forthcoming)", content)
                year = year_match.group(1) if year_match else ""

                # Extract suffix
                suffix_match = re.search(r";\s*(.+)$", content)
                suffix = suffix_match.group(1).strip() if suffix_match else ""

                # Extract locator
                locator_match = re.search(r"(p+\.\s*\d+|pp\.\s*\d+-\d+|ch\.\s*\d+)", content, re.IGNORECASE)
                locator = locator_match.group(0) if locator_match else ""

                citations.append({
                    "text": text,
                    "line": line_num,
                    "column": match.start(),
                    "authors": authors,
                    "year": year,
                    "citation_type": "parenthetical",
                    "has_locator": bool(locator),
                    "locator": locator,
                    "prefix": prefix,
                    "suffix": suffix,
                    "is_possessive": False,
                })

        return citations

    def rekey_entry(
        self,
        bibtex: str,
        existing_keys: list[str],
        convention: str = "auto",
    ) -> str:
        """Rewrite the BibTeX key of an entry to match a project's convention.

        Args:
            bibtex: A raw BibTeX entry string
            existing_keys: All keys currently in the project's .bib file
            convention: Key convention ("auto" or template like "{firstauthor}{year}{titleword}")

        Returns:
            The BibTeX entry string with the key rewritten
        """
        # Parse the BibTeX entry
        lines = bibtex.strip().split("\n")
        first_line = lines[0]

        # Extract current key
        match = re.match(r"@(\w+)\{(\w+)", first_line)
        if not match:
            raise ParseError("Invalid BibTeX entry format")

        entry_type = match.group(1)
        old_key = match.group(2)

        # Extract fields from entry
        entry_text = "\n".join(lines[1:]).rstrip("}")

        # Simple field extraction (handles single-line values)
        author = ""
        year = ""
        title = ""

        author_match = re.search(r"author\s*=\s*\{([^}]+)\}", entry_text)
        if author_match:
            author = author_match.group(1)

        year_match = re.search(r"year\s*=\s*\{?(\d{4})\}?", entry_text)
        if year_match:
            year = year_match.group(1)

        title_match = re.search(r"title\s*=\s*\{([^}]+)\}", entry_text)
        if title_match:
            title = title_match.group(1)

        # Generate new key
        new_key = self._generate_key(author, year, title, existing_keys)

        # Replace the key in the first line
        new_first_line = f"@{entry_type}{{{new_key},"
        new_bibtex = new_first_line + "\n" + "\n".join(lines[1:])

        return new_bibtex

    def _generate_key(self, author: str, year: str, title: str, existing_keys: list[str]) -> str:
        """Generate a BibTeX key from author, year, and title."""
        # Extract first author's last name
        author_part = ""
        if author:
            # Handle "Last, First and Last2, First2" format
            first_author = author.split(" and ")[0].split(",")[0]
            author_part = self._normalize_name(first_author)

        year_part = year

        # Extract first significant title word
        title_part = ""
        if title:
            words = title.lower().split()
            for word in words:
                word_clean = word.strip(".,;:")
                if word_clean not in self.STOPWORDS:
                    title_part = word_clean
                    break

        # Combine
        base_key = f"{author_part}{year_part}{title_part}"

        # Check for duplicates
        if base_key not in existing_keys:
            return base_key

        # Disambiguate with a/b/c
        for suffix in ["a", "b", "c", "d", "e", "f"]:
            candidate = f"{base_key}{suffix}"
            if candidate not in existing_keys:
                return candidate

        return base_key

    def add_entry(self, bib_path: str, entry: str) -> str:
        """Add a BibTeX entry to a .bib file.

        Args:
            bib_path: Path to the .bib file
            entry: The BibTeX entry string to add

        Returns:
            Confirmation with the key that was added
        """
        file_path = Path(bib_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {bib_path}")

        # Extract the key from the entry
        match = re.search(r"@\w+\{(\w+)", entry)
        if not match:
            raise ParseError("Invalid BibTeX entry format")

        new_key = match.group(1)

        # Read existing file
        content = file_path.read_text()
        existing_keys = re.findall(r"@\w+\{(\w+)", content)

        if new_key in existing_keys:
            raise BibTeXError(f"Key already exists: {new_key}")

        # Append entry
        with open(file_path, "a") as f:
            if content and not content.endswith("\n"):
                f.write("\n")
            f.write("\n" + entry + "\n")

        return f"Added entry with key: {new_key}"

    def suggest_replacement(
        self,
        citation_text: str,
        key: str,
        doc_type: str,
        natbib: bool = True,
    ) -> dict:
        """Given a bare citation and a resolved BibTeX key, return the proper citation command.

        Args:
            citation_text: The bare citation text as detected
            key: The resolved BibTeX key
            doc_type: "qmd" or "tex"
            natbib: For .tex files, whether to use natbib commands

        Returns:
            Object containing:
            - original: The bare citation text
            - replacement: The proper citation command
            - notes: Any caveats
        """
        is_possessive = "'s" in citation_text
        is_narrative = not citation_text.strip().startswith("(")

        # Extract locator if present
        locator_match = re.search(r"(p+\.\s*\d+|pp\.\s*\d+-\d+|ch\.\s*\d+)", citation_text, re.IGNORECASE)
        locator = locator_match.group(0) if locator_match else ""

        # Extract prefix
        prefix_match = re.search(r"^\((see|e\.g\.|i\.e\.|cf\.)\s+", citation_text, re.IGNORECASE)
        prefix = prefix_match.group(1) if prefix_match else ""

        # Extract suffix
        suffix_match = re.search(r",\s*([^)]+)\)$", citation_text)
        suffix = suffix_match.group(1) if suffix_match else ""

        if doc_type == "qmd":
            return self._suggest_quarto_replacement(citation_text, key, is_possessive, locator, prefix, suffix)
        else:  # tex
            return self._suggest_latex_replacement(citation_text, key, is_narrative, is_possessive, locator, prefix, suffix, natbib)

    def _suggest_quarto_replacement(self, citation_text: str, key: str, is_possessive: bool, locator: str, prefix: str, suffix: str) -> dict:
        """Generate Quarto citation replacement."""
        is_narrative = not citation_text.strip().startswith("(")

        if is_possessive:
            # For possessive, we can't use @key directly in Quarto
            replacement = f"{key}'s "
            notes = "Possessive form: create a composed citation or use manual format"
        elif is_narrative:
            replacement = f"@{key}"
            notes = ""
        else:
            # Parenthetical
            parts = ["@" + key]
            if locator:
                parts.append(locator)
            if suffix:
                parts.append(suffix)
            replacement = "[" + ", ".join(parts) + "]"
            if prefix:
                replacement = f"[{prefix} {replacement[1:]}"
            notes = ""

        return {
            "original": citation_text,
            "replacement": replacement,
            "notes": notes,
        }

    def _suggest_latex_replacement(self, citation_text: str, key: str, is_narrative: bool, is_possessive: bool, locator: str, prefix: str, suffix: str, natbib: bool) -> dict:
        """Generate LaTeX citation replacement."""
        if natbib:
            if is_possessive:
                replacement = f"\\citeauthor{{{key}}}'s (\\citeyear{{{key}}})"
                notes = "Possessive form requires composed command"
            elif is_narrative:
                replacement = f"\\citet{{{key}}}"
                notes = ""
            else:
                # Parenthetical
                if prefix or locator or suffix:
                    parts = []
                    if prefix:
                        parts.append(f"[{prefix}]")
                    else:
                        parts.append("[]")
                    if locator:
                        parts.append(f"[{locator}]")
                    elif suffix:
                        parts.append(f"[{suffix}]")
                    else:
                        parts.append("[]")
                    replacement = f"\\citep{{{key}}}" if not prefix else f"\\citep{{{key}}}"
                else:
                    replacement = f"\\citep{{{key}}}"
                notes = ""
        else:
            # biblatex
            replacement = f"\\textcite{{{key}}}" if is_narrative else f"\\parencite{{{key}}}"
            notes = "Using biblatex syntax (cite biblatex package)"

        return {
            "original": citation_text,
            "replacement": replacement,
            "notes": notes,
        }
