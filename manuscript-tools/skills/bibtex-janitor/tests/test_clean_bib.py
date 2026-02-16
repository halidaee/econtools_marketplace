import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from clean_bib import load_bib, save_bib, standardize_journal_names, apply_title_case, prune_fields, handle_url_doi, ensure_nber_format, validate_entry

def test_load_and_save_bib():
    """Test that we can load and save a bib file without corruption."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample.bib"
    bib_db = load_bib(fixture_path)

    assert len(bib_db.entries) == 1
    assert bib_db.entries[0]['ID'] == 'test2023'

    # Save to temp and verify it's valid
    output = save_bib(bib_db)
    assert '@article{test2023' in output

def test_standardize_journal_names():
    """Test journal name standardization."""
    entry = {
        'ID': 'test2023',
        'ENTRYTYPE': 'article',
        'journal': 'JPE'
    }

    standardize_journal_names(entry)
    assert entry['journal'] == 'Journal of Political Economy'

    # Test another variant
    entry2 = {'journal': 'Journal of Pol. Econ.'}
    standardize_journal_names(entry2)
    assert entry2['journal'] == 'Journal of Political Economy'

    # Test QJE
    entry3 = {'journal': 'QJE'}
    standardize_journal_names(entry3)
    assert entry3['journal'] == 'Quarterly Journal of Economics'

    # Test AER
    entry4 = {'journal': 'AER'}
    standardize_journal_names(entry4)
    assert entry4['journal'] == 'American Economic Review'

    # Test Econometrica (already full)
    entry5 = {'journal': 'Econometrica'}
    standardize_journal_names(entry5)
    assert entry5['journal'] == 'Econometrica'

def test_apply_title_case():
    entry = {'title': 'the effect of GDP on keynesian models in USA'}
    apply_title_case(entry)
    assert entry['title'] == 'The Effect of {GDP} on {Keynesian} Models in {USA}'

    entry2 = {'title': 'testing {GDP} growth'}
    apply_title_case(entry2)
    assert entry2['title'] == 'Testing {GDP} Growth'

    entry3 = {'title': 'the {McDonald}s effect'}
    apply_title_case(entry3)
    assert entry3['title'] == 'The {McDonald}s Effect'

    entry4 = {'title': 'VAR models and DSGE estimation'}
    apply_title_case(entry4)
    assert entry4['title'] == '{VAR} Models and {DSGE} Estimation'

def test_prune_fields():
    entry = {
        'ID': 'test2023', 'ENTRYTYPE': 'article', 'author': 'Test, Author',
        'title': 'Test Article', 'journal': 'Journal of Testing', 'year': '2023',
        'abstract': 'This is an abstract that should be removed.',
        'keywords': 'test, keywords', 'issn': '1234-5678',
        'file': '/path/to/file.pdf', 'mendeley-groups': 'My Research',
    }
    prune_fields(entry)
    assert 'author' in entry and 'title' in entry and 'journal' in entry and 'year' in entry
    assert 'abstract' not in entry and 'keywords' not in entry and 'issn' not in entry
    assert 'file' not in entry and 'mendeley-groups' not in entry

def test_handle_url_doi_for_articles():
    entry = {
        'ENTRYTYPE': 'article', 'author': 'Test, Author', 'title': 'Published Article',
        'journal': 'Journal of Economics', 'year': '2023',
        'url': 'https://example.com/paper.pdf', 'urldate': '2023-01-01', 'doi': '10.1234/test.2023',
    }
    handle_url_doi(entry)
    assert 'url' not in entry and 'urldate' not in entry and 'doi' in entry

def test_handle_url_doi_for_techreports():
    entry = {
        'ENTRYTYPE': 'techreport', 'author': 'Test, Author', 'title': 'NBER Working Paper',
        'institution': 'NBER', 'year': '2023', 'url': 'https://www.nber.org/papers/w12345', 'urldate': '2023-01-01',
    }
    handle_url_doi(entry)
    assert 'url' in entry and 'urldate' in entry

def test_handle_url_doi_for_unpublished():
    entry = {'ENTRYTYPE': 'unpublished', 'author': 'Test, Author', 'title': 'Working Paper', 'year': '2023', 'url': 'https://example.com/wp.pdf'}
    handle_url_doi(entry)
    assert 'url' in entry

def test_ensure_nber_format():
    entry = {
        'ID': 'acemoglu2023', 'ENTRYTYPE': 'article', 'author': 'Acemoglu, Daron',
        'title': 'Test Paper', 'journal': 'NBER Working Paper', 'year': '2023', 'number': '12345',
    }
    ensure_nber_format(entry)
    assert entry['ENTRYTYPE'] == 'techreport'
    assert entry['institution'] == 'National Bureau of Economic Research'
    assert entry['type'] == 'Working Paper'
    assert 'journal' not in entry

def test_ensure_nber_format_with_url():
    entry = {
        'ID': 'test2023', 'ENTRYTYPE': 'unpublished', 'author': 'Test, Author',
        'title': 'Test Paper', 'year': '2023', 'url': 'https://www.nber.org/papers/w12345',
    }
    ensure_nber_format(entry)
    assert entry['ENTRYTYPE'] == 'techreport'
    assert entry['institution'] == 'National Bureau of Economic Research'
    assert 'number' in entry

def test_ensure_nber_format_already_correct():
    entry = {
        'ID': 'test2023', 'ENTRYTYPE': 'techreport', 'author': 'Test, Author',
        'title': 'Test Paper', 'institution': 'National Bureau of Economic Research',
        'type': 'Working Paper', 'year': '2023', 'number': '12345',
    }
    original = entry.copy()
    ensure_nber_format(entry)
    assert entry == original

def test_validate_entry_complete():
    entry = {'ID': 'test2023', 'ENTRYTYPE': 'article', 'author': 'Test, Author',
             'title': 'Test Article', 'journal': 'Journal of Testing', 'year': '2023'}
    errors = validate_entry(entry)
    assert len(errors) == 0

def test_validate_entry_missing_author():
    entry = {'ID': 'test2023', 'ENTRYTYPE': 'article', 'title': 'Test Article',
             'journal': 'Journal of Testing', 'year': '2023'}
    errors = validate_entry(entry)
    assert len(errors) == 1 and 'author' in errors[0].lower()

def test_validate_entry_missing_year():
    entry = {'ID': 'test2023', 'ENTRYTYPE': 'article', 'author': 'Test, Author',
             'title': 'Test Article', 'journal': 'Journal of Testing'}
    errors = validate_entry(entry)
    assert len(errors) == 1 and 'year' in errors[0].lower()

def test_validate_entry_techreport_missing_institution():
    entry = {'ID': 'test2023', 'ENTRYTYPE': 'techreport', 'author': 'Test, Author',
             'title': 'Test Report', 'year': '2023'}
    errors = validate_entry(entry)
    assert len(errors) == 1 and 'institution' in errors[0].lower()
