import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from clean_bib import clean_bib_file

def test_integration_full_cleaning():
    fixture_path = Path(__file__).parent / "fixtures" / "messy.bib"
    fixture_path.write_text("""
@article{test2023,
  author = {Test, Author},
  title = {the effect of GDP on economic growth in USA},
  journal = {JPE},
  year = {2023},
  abstract = {This is a long abstract that should be removed.},
  keywords = {economics, growth},
  url = {https://example.com/paper.pdf},
  urldate = {2023-01-01},
}

@article{nber_paper,
  author = {Smith, John},
  title = {testing NBER working papers},
  journal = {NBER Working Paper},
  year = {2023},
  number = {12345},
  url = {https://www.nber.org/papers/w12345},
}
""")
    result = clean_bib_file(fixture_path, in_place=False)
    assert 'Journal of Political Economy' in result
    assert 'The Effect of {GDP} on Economic Growth in {USA}' in result
    assert 'abstract' not in result and 'keywords' not in result
    assert '@techreport{nber_paper' in result
    assert 'institution = {National Bureau of Economic Research}' in result
