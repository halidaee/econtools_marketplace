import pytest
from pathlib import Path
import tempfile

# Sample BibTeX entries
SAMPLE_BIB = """@article{conley2010learning,
  title={Learning about a New Technology: Pineapple in Ghana},
  author={Conley, Timothy G. and Udry, Christopher R.},
  journal={American Economic Review},
  volume={100},
  number={1},
  pages={35--69},
  year={2010},
  publisher={American Economic Association}
}

@article{suri2011selection,
  title={Selection and Comparative Advantage in Technology Adoption},
  author={Suri, Tavneet},
  journal={Econometrica},
  volume={79},
  number={3},
  pages={955--989},
  year={2011}
}

@techreport{bandiera2006social,
  title={Social Networks and Technology Adoption in Northern Mozambique},
  author={Bandiera, Oriana and Rasul, Imran},
  institution={NBER},
  number={w12141},
  year={2006}
}
"""

# Sample document with bare citations
SAMPLE_QMD = """# Research Paper

## Introduction

As shown by Conley and Udry (2010), technology adoption depends on social learning.
Suri (2011) demonstrates selection effects in technology adoption.

## Methods

We follow the methodology in (Conley and Udry 2010). Previous work (Suri 2011; Bandiera and Rasul 2006)
shows that networks matter.

## Results

These findings are consistent with earlier research (Conley and Udry 2010, p. 45).

## Acknowledgments

We thank Conley and Udry (2010) for helpful comments.
"""

SAMPLE_TEX = r"""
\documentclass{article}
\usepackage{natbib}

\begin{document}

\section{Introduction}

Conley and Udry (2010) show that technology adoption depends on social learning.
As noted by \cite{suri2011selection}, selection effects matter.

According to (Conley and Udry 2010), we should consider social networks.
See (Suri 2011) for evidence.

\end{document}
"""

SAMPLE_BIBTEX_ENTRY = """@article{heckman1979,
  title={Sample Selection Bias as a Specification Error},
  author={Heckman, James J.},
  journal={Econometrica},
  volume={47},
  number={1},
  pages={153--161},
  year={1979}
}"""

@pytest.fixture
def temp_bib_file():
    """Create a temporary .bib file with sample content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
        f.write(SAMPLE_BIB)
        path = f.name
    yield path
    Path(path).unlink()

@pytest.fixture
def temp_qmd_file():
    """Create a temporary .qmd file with sample content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False) as f:
        f.write(SAMPLE_QMD)
        path = f.name
    yield path
    Path(path).unlink()

@pytest.fixture
def temp_tex_file():
    """Create a temporary .tex file with sample content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
        f.write(SAMPLE_TEX)
        path = f.name
    yield path
    Path(path).unlink()

@pytest.fixture
def temp_empty_bib():
    """Create an empty temporary .bib file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
        path = f.name
    yield path
    Path(path).unlink()
