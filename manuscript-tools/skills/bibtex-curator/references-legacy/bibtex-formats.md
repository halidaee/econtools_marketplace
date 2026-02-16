# BibTeX Entry Formats

Key generation conventions, entry templates, author formatting rules, and common economics working paper series.

---

## A. Key Generation Convention

Based on the user's existing `.bib` files, keys follow this pattern:

**Format:** `{firstauthorlastname}{year}{firstsignificantwordoftitle}` — all lowercase

**Examples from existing `.bib` files:**
- `conley2010learning` — Conley and Udry (2010), "Learning about a New Technology"
- `suri2011selection` — Suri (2011), "Selection and Comparative Advantage"
- `bandiera2006social` — Bandiera and Rasul (2006), "Social Networks and Technology"
- `duflo2002role` — Duflo and Saez (2002), "The Role of Information"
- `qiao2020social` — Qiao, Bai, and Jin (2020), "Social Learning in the COVID-19 Pandemic"

**Rules:**
1. Use **first author's last name only** (even with multiple authors)
2. **Year** as 4 digits
3. **First significant word** of title (skip articles: "a", "an", "the", "on")
4. All **lowercase**, no underscores, no hyphens
5. Strip accents/diacritics: `lovasz` not `lov{\'a}sz`
6. Remove hyphens from names: `tahbazsalehi` not `tahbaz-salehi`
7. **Disambiguation**: append `a`, `b`, `c` for same author-year: `heckman1979a`, `heckman1979b`

**Before generating a new key:** Read the project's existing `.bib` file and observe the actual convention used. If it differs from above (e.g., uses underscores or full author list), match that convention instead.

---

## B. Entry Templates

### @article (journal article — most common in economics)

```bibtex
@article{key,
  title={Full Title in Title Case},
  author={Last1, First1 and Last2, First2},
  journal={Journal Name},
  volume={V},
  number={N},
  pages={start--end},
  year={YYYY},
  publisher={Publisher}
}
```

Required: `title`, `author`, `journal`, `year`
Optional: `volume`, `number`, `pages`, `publisher`, `doi`

### @techreport (working paper with institutional series)

```bibtex
@techreport{key,
  title={Full Title},
  author={Last1, First1 and Last2, First2},
  institution={NBER},
  type={Working Paper},
  number={w12345},
  year={YYYY}
}
```

Required: `title`, `author`, `institution`, `year`
Optional: `type`, `number`, `url`

### @unpublished (manuscript / working paper without series)

```bibtex
@unpublished{key,
  title={Full Title},
  author={Last1, First1 and Last2, First2},
  note={Working paper, University Name},
  year={YYYY}
}
```

Required: `title`, `author`, `note`, `year`
Optional: `url`

### @incollection (chapter in edited volume / handbook)

```bibtex
@incollection{key,
  title={Chapter Title},
  author={Last1, First1},
  booktitle={Handbook of Economics},
  editor={EditorLast, EditorFirst},
  volume={V},
  pages={start--end},
  year={YYYY},
  publisher={Publisher}
}
```

Required: `title`, `author`, `booktitle`, `year`, `publisher`
Optional: `editor`, `volume`, `pages`, `chapter`

### @book

```bibtex
@book{key,
  title={Book Title},
  author={Last1, First1},
  year={YYYY},
  publisher={Publisher}
}
```

Required: `title`, `author`, `year`, `publisher`
Optional: `edition`, `volume`, `address`

### @inproceedings (conference paper)

```bibtex
@inproceedings{key,
  title={Paper Title},
  author={Last1, First1 and Last2, First2},
  booktitle={Proceedings of Conference Name},
  pages={start--end},
  year={YYYY},
  organization={Organizer}
}
```

Required: `title`, `author`, `booktitle`, `year`
Optional: `pages`, `organization`, `publisher`

---

## C. Author Name Formatting

**BibTeX format:** `Last, First and Last, First`

- Multiple authors joined with literal ` and ` (not `&`)
- Preserve LaTeX accent escapes: `Lov{\\'a}sz, L{\\'a}szl{\\'o}`
- Hyphenated names preserved in entry: `Tahbaz-Salehi, Alireza`
- Name particles: `de Finetti, Bruno` (lowercase particle is part of last name)
- Jr/Sr suffixes: `Author, Jr., First` (comma after Jr/Sr)

**When creating entries from API results:**
- CrossRef returns `{given: "Timothy G", family: "Conley"}` → `Conley, Timothy G`
- Semantic Scholar returns `name: "Timothy G. Conley"` → parse as `Conley, Timothy G.`
- Multiple authors: join with ` and `

---

## D. Common Economics Working Paper Series

| Institution | BibTeX type | `type` field | `number` format | `institution` field |
|---|---|---|---|---|
| NBER | `@techreport` | `Working Paper` | `w` + digits (e.g., `w28150`) | `National Bureau of Economic Research` |
| CEPR | `@techreport` | `Discussion Paper` | digits | `Centre for Economic Policy Research` |
| IZA | `@techreport` | `Discussion Paper` | digits | `Institute of Labor Economics` |
| World Bank | `@techreport` | `Policy Research Working Paper` | digits | `The World Bank` |
| IMF | `@techreport` | `Working Paper` | `WP/YY/NNN` | `International Monetary Fund` |
| Cowles Foundation | `@techreport` | `Discussion Paper` | digits | `Cowles Foundation, Yale University` |
| Econometrica R&R | `@unpublished` | — | — | note: `Working paper, University` |
| SSRN preprint | `@unpublished` | — | — | note: `Available at SSRN` |

**Choosing entry type for working papers:**
- Has an institutional series (NBER, CEPR, etc.) → `@techreport`
- No series, just a manuscript → `@unpublished`
- If unclear, prefer `@unpublished` with descriptive `note` field
