---
name: bibtex-janitor
description: Clean and standardize .bib files for AER/QJE economics journal submissions
---

# BibTeX Janitor

Cleans and standardizes BibTeX files for economics journal submissions (AER, QJE, etc.).

## Usage

```
/clean-bib path/to/references.bib
```

## What it does

1. **Journal Names**: Standardizes to full formal names (e.g., 'JPE' → 'Journal of Political Economy')
2. **Title Casing**: Applies Title Case and wraps acronyms in braces ({GDP}, {USA})
3. **Field Pruning**: Removes abstract, keywords, issn, file, mendeley-groups
4. **URL/DOI**: Keeps only for @techreport/@unpublished, removes from @article
5. **NBER Format**: Ensures @techreport with proper institution field
6. **Validation**: Checks for missing mandatory fields

## Requirements

```bash
pip install bibtexparser
```

## Implementation

### Core Functions

- **`load_bib(filepath)`**: Load and parse BibTeX files using bibtexparser
- **`save_bib(bib_db)`**: Convert parsed database back to properly formatted BibTeX
- **`apply_title_case(entry)`**: Apply title case with special handling for acronyms and proper names
- **`standardize_journal_names(entry)`**: Map journal abbreviations to full formal names
- **`prune_fields(entry)`**: Remove metadata fields (abstract, keywords, file, etc.)
- **`handle_url_doi(entry)`**: Conditionally keep URLs only for @techreport/@unpublished types
- **`ensure_nber_format(entry)`**: Convert NBER papers to @techreport with proper institution field
- **`validate_entry(entry)`**: Check for required fields by entry type
- **`clean_entry(entry)`**: Orchestrate all cleaning operations on a single entry
- **`clean_bib_file(filepath, in_place=False)`**: Apply all cleaning to entire file

### Supported Entry Types

- `@article`: Journal papers (removes URLs, standardizes journal names)
- `@techreport`: Working papers and technical reports (preserves URLs)
- `@book`: Books (validates publisher field)
- `@inproceedings` / `@incollection`: Conference papers (validates booktitle field)
