# BibTeX Janitor

Clean and standardize BibTeX files for economics journal submissions (AER, QJE, JPE, etc.).

## Overview

BibTeX Janitor is a specialized cleaning tool designed to prepare BibTeX bibliographies for submission to top-tier economics journals. It implements a comprehensive set of standardization rules to ensure consistency, remove metadata that journals don't accept, and apply proper formatting conventions.

### Key Features

1. **Journal Name Standardization** - Maps common abbreviations to full formal names (e.g., 'JPE' → 'Journal of Political Economy')
2. **Title Case Formatting** - Applies Chicago Manual of Style title case with special handling for acronyms and proper names
3. **Field Pruning** - Removes metadata fields that journals typically reject (abstract, keywords, file paths, etc.)
4. **URL/DOI Handling** - Intelligently keeps URLs only for unpublished/technical reports, removes from published articles
5. **NBER Format Consistency** - Ensures NBER working papers use @techreport with proper institution field
6. **Entry Validation** - Checks for required fields by entry type

## Installation

```bash
pip install bibtexparser
```

## Usage

### Command Line

```bash
python clean_bib.py references.bib
```

Creates a backup at `references.bib.backup` and modifies the file in place.

### Programmatic Usage

```python
from clean_bib import clean_bib_file

# Get cleaned BibTeX as string without modifying file
result = clean_bib_file('references.bib', in_place=False)

# Clean file in place
clean_bib_file('references.bib', in_place=True)
```

## Cleaning Operations

### 1. Journal Name Standardization

Converts common journal abbreviations to full formal names:

- JPE → Journal of Political Economy
- QJE → Quarterly Journal of Economics
- AER → American Economic Review
- REStat → Review of Economics and Statistics
- JFE → Journal of Financial Economics
- And 12+ other top economics journals

### 2. Title Case Formatting

Applies proper title case with special rules:

- First word always capitalized
- Articles, prepositions, conjunctions lowercase (unless first word)
- Acronyms wrapped in braces: {GDP}, {USA}, {NBER}
- Proper names preserved: {Keynesian}, {Bayesian}, {Ricardian}
- Existing braces protected: {Already Braced Content} preserved as-is

**Example:**
```
Input:  "the effect of GDP on economic growth in USA"
Output: "The Effect of {GDP} on Economic Growth in {USA}"
```

### 3. Field Pruning

Removes these metadata fields:
- abstract
- keywords
- issn
- file
- mendeley-groups
- mendeley-tags
- annotation
- note

### 4. URL/DOI Handling

- **@article**: URLs and DOI dates removed (journals have their own databases)
- **@techreport/@unpublished**: URLs and DOI dates preserved (no other source)
- **All types**: DOI field preserved when present

### 5. NBER Format Consistency

Detects NBER working papers by:
- URL containing "nber.org"
- Journal field containing "NBER"
- Institution field containing "NBER" or "National Bureau"

Converts to standardized format:
```bibtex
@techreport{paper2023,
  author = {Author Name},
  title = {Paper Title},
  institution = {National Bureau of Economic Research},
  type = {Working Paper},
  number = {12345},
  year = {2023},
}
```

### 6. Validation

Checks each entry for required fields:

**All entries require:**
- author or editor
- year
- title

**By entry type:**
- @article: journal
- @techreport: institution
- @book: publisher
- @inproceedings / @incollection: booktitle

## Supported Entry Types

### @article
Journal articles. URLs removed, journal names standardized.

```bibtex
@article{author2023,
  author = {Author, First},
  title = {Paper Title},
  journal = {Journal of Economics},
  year = {2023},
  volume = {50},
  number = {3},
  pages = {123--145},
}
```

### @techreport
Working papers and technical reports. Useful for NBER papers.

```bibtex
@techreport{nber2023,
  author = {Author, First},
  title = {Working Paper Title},
  institution = {National Bureau of Economic Research},
  type = {Working Paper},
  number = {12345},
  year = {2023},
  url = {https://www.nber.org/papers/w12345},
}
```

### @book
Books and monographs.

```bibtex
@book{author2020,
  author = {Author, First},
  title = {Book Title},
  publisher = {Publisher Name},
  year = {2020},
}
```

### @inproceedings / @incollection
Conference papers and book chapters.

```bibtex
@inproceedings{author2022,
  author = {Author, First},
  title = {Paper Title},
  booktitle = {Conference Proceedings},
  year = {2022},
}
```

## Examples

### Example 1: Cleaning a Basic Article

**Input:**
```bibtex
@article{smith2020,
  author = {Smith, John},
  title = {the effect of policy on growth},
  journal = {AER},
  year = {2020},
  abstract = {This paper studies..},
  keywords = {policy, growth},
  url = {https://example.com/paper.pdf},
}
```

**Output:**
```bibtex
@article{smith2020,
  author = {Smith, John},
  title = {The Effect of Policy on Growth},
  journal = {American Economic Review},
  year = {2020},
}
```

### Example 2: Converting NBER Papers

**Input:**
```bibtex
@article{jones2023,
  author = {Jones, Mary},
  title = {labor markets and AI},
  journal = {NBER Working Paper},
  number = {30000},
  year = {2023},
  url = {https://www.nber.org/papers/w30000},
}
```

**Output:**
```bibtex
@techreport{jones2023,
  author = {Jones, Mary},
  title = {Labor Markets and {AI}},
  institution = {National Bureau of Economic Research},
  type = {Working Paper},
  number = {30000},
  year = {2023},
  url = {https://www.nber.org/papers/w30000},
}
```

## Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Test coverage includes:
- BibTeX file parsing and writing
- Journal name standardization
- Title case formatting with acronym/proper name handling
- Field pruning
- URL/DOI conditional handling
- NBER format conversion
- Entry validation
- Full end-to-end integration test

## Implementation

### Core Functions

- `load_bib(filepath)` - Load and parse BibTeX files
- `save_bib(bib_db)` - Convert parsed database back to BibTeX
- `apply_title_case(entry)` - Apply title case with brace protection
- `standardize_journal_names(entry)` - Map journal abbreviations
- `prune_fields(entry)` - Remove unwanted metadata fields
- `handle_url_doi(entry)` - Conditional URL/DOI handling
- `ensure_nber_format(entry)` - Convert NBER papers to @techreport
- `validate_entry(entry)` - Check required fields
- `clean_entry(entry)` - Orchestrate all cleaning operations
- `clean_bib_file(filepath, in_place)` - Clean entire BibTeX file

## Journal Support

Standardizes names for these journals and their common abbreviations:

- American Economic Review (AER)
- Journal of Political Economy (JPE)
- Quarterly Journal of Economics (QJE)
- Econometrica
- Review of Economics and Statistics (REStat)
- Journal of the European Economic Association (JEEA)
- Journal of Economic Literature (JEL)
- Review of Economic Studies (ReStud)
- Journal of Finance (JF)
- Journal of Financial Economics (JFE)
- CEPR
- IZA
- NBER

## Error Handling

Validation warnings are printed but don't prevent file processing. Missing required fields are reported for manual review.

Example output:
```
Validation Warnings:
  - [paper1] Missing required field: author or editor
  - [paper2] Article missing required field: journal

2 validation warnings (see above)
```

## Contributing

Run tests before submitting changes:

```bash
python -m pytest tests/ -v
```

## License

MIT

## Support

For issues or questions about BibTeX format, see:
- [BibTeX Reference](https://www.ctan.org/pkg/bibtex)
- [Chicago Manual of Style - Titles and Capitalization](https://www.chicagomanualofstyle.org/)
- [AER Author Guide](https://www.aeaweb.org/journals/aer)
