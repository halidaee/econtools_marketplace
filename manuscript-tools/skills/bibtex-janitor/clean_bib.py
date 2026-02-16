#!/usr/bin/env python3
"""BibTeX cleaning and standardization for economics journals."""

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from pathlib import Path
import re

ACRONYMS = {
    'gdp', 'gnp', 'cpi', 'ppi', 'var', 'arma', 'arima', 'garch',
    'dsge', 'iv', 'ols', 'gls', 'gmm', 'ml', 'mle', 'mcmc',
    'usa', 'uk', 'eu', 'oecd', 'imf', 'fed', 'ecb',
    'nber', 'cepr', 'iza', 'covid', 'aids', 'nato',
}

PROPER_NAMES = {
    'keynesian', 'bayesian', 'ricardian', 'malthusian', 'smithian',
    'walrasian', 'marshallian', 'fisherian', 'friedman', 'samuelson',
    'gaussian', 'poisson', 'bernoulli', 'markov',
}

JUNK_FIELDS = {
    'abstract', 'keywords', 'issn', 'file', 'mendeley-groups',
    'mendeley-tags', 'annotation', 'note',
}

# Journal name mappings for top economics journals
JOURNAL_MAPPINGS = {
    # JPE variants
    'jpe': 'Journal of Political Economy',
    'j pol econ': 'Journal of Political Economy',
    'j. pol. econ.': 'Journal of Political Economy',
    'journal of pol. econ.': 'Journal of Political Economy',
    'journal of political economy': 'Journal of Political Economy',

    # QJE variants
    'qje': 'Quarterly Journal of Economics',
    'q j econ': 'Quarterly Journal of Economics',
    'quarterly journal of economics': 'Quarterly Journal of Economics',

    # AER variants
    'aer': 'American Economic Review',
    'amer econ rev': 'American Economic Review',
    'american economic review': 'American Economic Review',

    # Econometrica (standard)
    'econometrica': 'Econometrica',

    # REStat variants
    'restat': 'Review of Economics and Statistics',
    'rev econ stat': 'Review of Economics and Statistics',
    'review of economics and statistics': 'Review of Economics and Statistics',

    # JEEA variants
    'jeea': 'Journal of the European Economic Association',
    'journal of the european economic association': 'Journal of the European Economic Association',

    # JEL variants
    'jel': 'Journal of Economic Literature',
    'journal of economic literature': 'Journal of Economic Literature',

    # ReStud variants
    'restud': 'Review of Economic Studies',
    'rev econ stud': 'Review of Economic Studies',
    'review of economic studies': 'Review of Economic Studies',

    # JF variants
    'jf': 'Journal of Finance',
    'j finance': 'Journal of Finance',
    'journal of finance': 'Journal of Finance',

    # JFE variants
    'jfe': 'Journal of Financial Economics',
    'journal of financial economics': 'Journal of Financial Economics',
}

def apply_title_case(entry):
    """Apply title case and wrap acronyms/proper names in braces."""
    if 'title' not in entry:
        return

    title = entry['title']
    braced_pattern = r'\{[^}]+\}'
    braced_content = re.findall(braced_pattern, title)
    placeholders = {}

    for i, content in enumerate(braced_content):
        placeholder = f'__BRACED_{i}__'
        placeholders[placeholder] = content
        title = title.replace(content, placeholder, 1)

    words = title.split()
    result = []

    for i, word in enumerate(words):
        if word.startswith('__BRACED_'):
            result.append(word)
            continue

        word_clean = re.sub(r'[^\w]', '', word)
        if word_clean.upper() == word_clean and len(word_clean) >= 2 and word_clean.isalpha():
            if word_clean.lower() in ACRONYMS:
                word = re.sub(word_clean, f'{{{word_clean}}}', word)
                result.append(word)
                continue

        if word_clean.lower() in PROPER_NAMES:
            capitalized = word_clean.capitalize()
            word = re.sub(word_clean, f'{{{capitalized}}}', word, flags=re.IGNORECASE)
            result.append(word)
            continue

        if i == 0:
            result.append(word.capitalize())
        elif word.lower() in ['a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'of', 'in']:
            result.append(word.lower())
        else:
            result.append(word.capitalize())

    title = ' '.join(result)

    for placeholder, content in placeholders.items():
        title = title.replace(placeholder, content)

    entry['title'] = title

def load_bib(filepath):
    """Load a BibTeX file and return the parsed database."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return bibtexparser.load(f)

def save_bib(bib_db):
    """Convert BibTeX database to string."""
    writer = BibTexWriter()
    writer.indent = '  '
    writer.order_entries_by = None
    return writer.write(bib_db)

def standardize_journal_names(entry):
    """Standardize journal names to full formal names."""
    if 'journal' not in entry:
        return

    journal = entry['journal'].strip()
    journal_lower = journal.lower()

    if journal_lower in JOURNAL_MAPPINGS:
        entry['journal'] = JOURNAL_MAPPINGS[journal_lower]

def prune_fields(entry):
    """Remove junk fields that journals don't want."""
    for field in JUNK_FIELDS:
        entry.pop(field, None)

def handle_url_doi(entry):
    """Conditionally handle URL and DOI fields."""
    entry_type = entry.get('ENTRYTYPE', '').lower()
    if entry_type in ['techreport', 'unpublished']:
        return
    if entry_type == 'article':
        entry.pop('url', None)
        entry.pop('urldate', None)

def ensure_nber_format(entry):
    """Ensure NBER working papers are formatted correctly."""
    is_nber = False
    url = entry.get('url', '')
    if 'nber.org' in url.lower():
        is_nber = True
    journal = entry.get('journal', '')
    if 'nber' in journal.lower():
        is_nber = True
    institution = entry.get('institution', '')
    if 'nber' in institution.lower() or 'national bureau' in institution.lower():
        is_nber = True

    if not is_nber:
        return

    entry['ENTRYTYPE'] = 'techreport'
    entry['institution'] = 'National Bureau of Economic Research'
    entry['type'] = 'Working Paper'
    entry.pop('journal', None)

    if 'number' not in entry and url:
        match = re.search(r'[/w](\d{4,5})', url)
        if match:
            entry['number'] = match.group(1)

def validate_entry(entry):
    """Validate that entry has required fields. Returns list of error messages."""
    errors = []
    entry_type = entry.get('ENTRYTYPE', '').lower()
    entry_id = entry.get('ID', 'unknown')

    if 'author' not in entry and 'editor' not in entry:
        errors.append(f"[{entry_id}] Missing required field: author or editor")
    if 'year' not in entry:
        errors.append(f"[{entry_id}] Missing required field: year")
    if 'title' not in entry:
        errors.append(f"[{entry_id}] Missing required field: title")

    if entry_type == 'article':
        if 'journal' not in entry:
            errors.append(f"[{entry_id}] Article missing required field: journal")
    elif entry_type == 'techreport':
        if 'institution' not in entry:
            errors.append(f"[{entry_id}] Techreport missing required field: institution")
    elif entry_type == 'book':
        if 'publisher' not in entry:
            errors.append(f"[{entry_id}] Book missing required field: publisher")
    elif entry_type in ['inproceedings', 'incollection']:
        if 'booktitle' not in entry:
            errors.append(f"[{entry_id}] {entry_type} missing required field: booktitle")

    return errors

def clean_entry(entry):
    """Apply all cleaning operations to a single entry."""
    ensure_nber_format(entry)
    standardize_journal_names(entry)
    apply_title_case(entry)
    prune_fields(entry)
    handle_url_doi(entry)
    return validate_entry(entry)

def clean_bib_file(filepath, in_place=False):
    """Clean a BibTeX file with all standardization rules."""
    bib_db = load_bib(filepath)
    all_errors = []
    for entry in bib_db.entries:
        errors = clean_entry(entry)
        all_errors.extend(errors)
    output = save_bib(bib_db)
    if all_errors:
        print("\n⚠️  Validation Warnings:")
        for error in all_errors:
            print(f"  - {error}")
        print()
    if in_place:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ Cleaned {len(bib_db.entries)} entries in {filepath}")
        if all_errors:
            print(f"⚠️  {len(all_errors)} validation warnings (see above)")
    else:
        return output

if __name__ == '__main__':
    import sys
    import shutil

    if len(sys.argv) != 2:
        print("Usage: clean_bib.py <file.bib>")
        print("\nCleans and standardizes a BibTeX file for journal submission.")
        print("Creates a backup at <file.bib.backup> before modifying.")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    backup_path = filepath.with_suffix('.bib.backup')
    shutil.copy2(filepath, backup_path)
    print(f"📦 Created backup: {backup_path}")
    clean_bib_file(filepath, in_place=True)
