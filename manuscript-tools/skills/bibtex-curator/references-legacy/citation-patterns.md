# Citation Detection Patterns

Regex patterns for detecting bare (written-out) citations and templates for replacing them with proper citation commands.

---

## A. Bare Citation Patterns to Detect

These patterns indicate a written-out citation that should be replaced with a proper `@key` (Quarto) or `\cite{key}` (LaTeX) command.

### Narrative citations (author is part of the sentence)

| # | Pattern | Example |
|---|---|---|
| 1 | `Author (Year)` — single author | `Suri (2011)` |
| 2 | `Author and Author (Year)` — two authors | `Conley and Udry (2010)` |
| 3 | `Author, Author, and Author (Year)` — three authors | `Duflo, Kremer, and Robinson (2011)` |
| 4 | `Author et al. (Year)` — 3+ abbreviated | `Banerjee et al. (2013)` |
| 5 | `Author et al. (Year, p. N)` — with page locator | `Banerjee et al. (2013, p. 45)` |
| 6 | `Author (Year, Year)` — multiple years | `Heckman (1976, 1979)` |
| 7 | `Author (forthcoming)` | `Mogstad (forthcoming)` |
| 8 | `Author's (Year)` — possessive | `Mogstad's (2012)` |

### Parenthetical citations (author inside parentheses)

| # | Pattern | Example |
|---|---|---|
| 9 | `(Author Year)` | `(Suri 2011)` |
| 10 | `(Author and Author Year)` | `(Conley and Udry 2010)` |
| 11 | `(Author et al. Year)` | `(Banerjee et al. 2013)` |
| 12 | `(Author Year; Author Year)` — multiple works | `(Suri 2011; Conley and Udry 2010)` |
| 13 | `(Author Year, p. N)` — with locator | `(Suri 2011, p. 45)` |
| 14 | `(see Author Year)` — with prefix | `(see Suri 2011)` |
| 15 | `(Author Year, among others)` — with suffix | `(Suri 2011, among others)` |

### Edge cases

| # | Pattern | Example | Note |
|---|---|---|---|
| 16 | Hyphenated last names | `Tahbaz-Salehi (2020)` | Hyphen is part of the name |
| 17 | Name particles | `de Finetti (1937)`, `Van der Waerden (1971)` | Lowercase particle before capitalized surname |
| 18 | Jr/Sr/III suffixes | `Autor Jr. (2003)` | Suffix before year |
| 19 | Institutional authors | `World Bank (2020)`, `NBER (2019)` | Multi-word "last name" |
| 20 | Year ranges | `(2010-2015)` | **NOT a citation** — exclude |
| 21 | Already-cited | `@conley2010learning`, `\citet{key}` | **Skip** — already proper |

### Master detection regexes

**Narrative (author outside parens, year in parens):**
```
[A-Z][a-zA-Z'-]+(?:[-\s]+[a-z]+)*(?:\s+(?:and|&)\s+[A-Z][a-zA-Z'-]+(?:[-\s]+[a-z]+)*)?(?:,\s+[A-Z][a-zA-Z'-]+(?:[-\s]+[a-z]+)*)*(?:\s+et\s+al\.?)?\s*\(\d{4}[a-z]?\b
```

**Parenthetical (everything inside parens):**
```
\([^)]*[A-Z][a-zA-Z'-]+(?:\s+(?:and|&)\s+[A-Z][a-zA-Z'-]+)?(?:\s+et\s+al\.?)?\s+\d{4}[a-z]?[^)]*\)
```

**Important:** These regexes are starting points. After matching, Claude must check context to confirm:
- Not preceded by `@` (already a Quarto citation)
- Not inside `\cite{}`, `\citet{}`, `\citep{}` etc. (already a LaTeX citation)
- Not in an acknowledgments section, author list, or bibliography
- Not a non-citation mention (e.g., "The World Bank (2020 fiscal year)")

---

## B. Replacement Templates

### For Quarto (`.qmd`) files

| Bare citation | Replacement | Notes |
|---|---|---|
| `Suri (2011)` — narrative | `@suri2011selection` | Author name becomes part of rendered output |
| `Conley and Udry (2010)` — narrative | `@conley2010learning` | Both names rendered automatically |
| `(Suri 2011)` — parenthetical | `[@suri2011selection]` | Square brackets = parenthetical |
| `(Suri 2011; Conley and Udry 2010)` — multiple | `[@suri2011selection; @conley2010learning]` | Semicolon-separated inside brackets |
| `(see Suri 2011)` — with prefix | `[see @suri2011selection]` | Prefix before `@` |
| `(Suri 2011, p. 45)` — with locator | `[@suri2011selection, p. 45]` | Locator after key |
| `(Suri 2011, among others)` — with suffix | `[@suri2011selection, among others]` | Suffix after key |
| Year-only after author already named | `[-@suri2011selection]` | Suppress author, show year only |

### For LaTeX (`.tex`) files with natbib

| Bare citation | Replacement | Notes |
|---|---|---|
| `Suri (2011)` — narrative | `\citet{suri2011selection}` | "cite-textual" |
| `(Suri 2011)` — parenthetical | `\citep{suri2011selection}` | "cite-parenthetical" |
| `(Suri 2011; Conley and Udry 2010)` — multiple | `\citep{suri2011selection, conley2010learning}` | Comma-separated keys |
| `(see Suri 2011)` — with prefix | `\citep[see][]{suri2011selection}` | `[prenote][postnote]{key}` |
| `(Suri 2011, p. 45)` — with locator | `\citep[p.~45]{suri2011selection}` | Postnote only |
| `Suri's (2011)` — possessive | `\citeauthor{suri2011selection}'s (\citeyear{suri2011selection})` | Compose from parts |
| Author name only | `\citeauthor{suri2011selection}` | Just the name |
| Year only | `\citeyear{suri2011selection}` | Just the year |

### Quarto vs. LaTeX detection

- `.qmd` file extension → Quarto syntax
- `.tex` file extension → LaTeX/natbib syntax
- Check for `natbib` in preamble; if `biblatex` instead, use `\textcite`/`\parencite` (rare in econ)
