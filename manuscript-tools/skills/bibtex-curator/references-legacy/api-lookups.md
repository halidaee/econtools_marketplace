# API Lookups for Citation Resolution

How to find papers programmatically using CrossRef and Semantic Scholar APIs, plus the resolution strategy and working paper publication check.

---

## A. CrossRef REST API

No authentication required. Include `mailto` for polite pool (higher rate limits).

### Search by bibliographic query (author + title keywords + year)

```bash
curl -s "https://api.crossref.org/works?query.bibliographic=Mogstad+Wiswall+2012&rows=5&mailto=user@example.com"
```

### Search by title only

```bash
curl -s "https://api.crossref.org/works?query.title=Selection+comparative+advantage+technology+adoption&rows=3&mailto=user@example.com"
```

### Search by author + title

```bash
curl -s "https://api.crossref.org/works?query.author=Conley+Udry&query.title=learning+technology+pineapple&rows=3&mailto=user@example.com"
```

### Lookup by DOI

```bash
curl -s "https://api.crossref.org/works/10.1257/aer.100.1.35"
```

### Filter for journal articles only

```bash
curl -s "https://api.crossref.org/works?query.bibliographic=Mogstad+Wiswall&filter=type:journal-article&rows=5&mailto=user@example.com"
```

### Key response fields

Parse with `python3 -c "import sys,json; ..."` or `jq`:

```
message.items[].title[0]                        # paper title
message.items[].author[]                        # [{given, family}, ...]
message.items[].container-title[0]              # journal name
message.items[].published-print.date-parts[0][0]  # year (published print)
message.items[].published-online.date-parts[0][0] # year (published online)
message.items[].volume                          # volume number
message.items[].issue                           # issue number
message.items[].page                            # page range (e.g., "35-69")
message.items[].DOI                             # DOI string
message.items[].type                            # "journal-article", "posted-content", "report"
message.items[].score                           # relevance score (higher = better)
message.items[].relation.is-preprint-of[]       # links to published version (if preprint)
```

### Converting CrossRef result to BibTeX entry

```python
# Pseudocode for extracting fields from a CrossRef item
item = result["message"]["items"][0]
authors = " and ".join(f"{a['family']}, {a.get('given', '')}" for a in item["author"])
year = item.get("published-print", item.get("published-online", {})).get("date-parts", [[None]])[0][0]
journal = item.get("container-title", [""])[0]
pages = item.get("page", "").replace("-", "--")
```

### Rate limits

- No auth needed; include `mailto=email` for polite pool
- Polite pool: ~50 requests/second
- Without mailto: lower rate, may be throttled

---

## B. Semantic Scholar API

### Search by keyword

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=Mogstad+Wiswall+2012&limit=5&fields=title,authors,year,venue,externalIds,publicationTypes"
```

### Lookup by DOI

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1257/aer.100.1.35?fields=title,authors,year,venue,externalIds,publicationTypes"
```

### Key response fields

```
data[].title                    # paper title
data[].authors[].name           # "First Last" format
data[].year                     # publication year (integer)
data[].venue                    # journal/venue name
data[].externalIds.DOI          # DOI if available
data[].externalIds.ArXiv        # arXiv ID if available
data[].publicationTypes[]       # ["JournalArticle"], ["Conference"], etc.
```

### Rate limits

- 100 requests per 5 minutes without API key
- Register at semanticscholar.org for higher limits

---

## C. Resolution Strategy

For each bare citation detected in the document:

### Step 1: Extract author(s) and year

From the matched text, extract:
- Last name(s) of all authors mentioned
- Year (4-digit number)
- Whether it's "et al." (meaning more authors exist)

### Step 2: Search project `.bib` file

Parse all `@type{key, ...}` entries. For each entry, extract author last names and year. Match against the bare citation:

- **Unique match** (one entry with matching author(s) + year) → use that key, proceed to replacement
- **Multiple matches** (e.g., two papers by "Heckman 1979") → ask user to choose
- **No match** → proceed to step 3

### Step 3: Search project markdown files

```bash
# Grep .md files for author name + year
grep -rl "Mogstad.*2012\|2012.*Mogstad" /path/to/project/*.md
```

If found, read the markdown file and look for:
- Paper title (often in heading or bold)
- Journal name
- Other authors
- URL or DOI

Use whatever information is found to create a BibTeX entry per `bibtex-formats.md`, then validate/complete via CrossRef (step 4).

### Step 4: Search CrossRef API

Query with author name(s) + year. Score each result:

| Criterion | Points |
|---|---|
| Author last name(s) match exactly | +3 |
| Year matches exactly | +2 |
| Title contains expected keywords | +2 |
| Has DOI | +1 |
| Type is `journal-article` | +1 |
| **Maximum possible** | **9** |

**Decision thresholds:**
- Score **>= 7**: Accept automatically. Create BibTeX entry, add to `.bib`, replace citation.
- Score **4–6**: Show the user the top result with title, authors, journal, year. Ask "Is this the right paper?"
- Score **< 4**: Show user the top 3 results. Ask them to pick one or provide more info.

### Step 5: Fall back to Semantic Scholar

If CrossRef returns no results or all scores < 4:
- Query Semantic Scholar with same search terms
- Apply same scoring system
- Semantic Scholar is better for recent/unpublished papers

### Step 6: Fall back to WebSearch

As last resort:
- Search for `"Author1 Author2 Year paper"` or `"Author1 Author2 title keywords"`
- Extract citation info from search results (often Google Scholar or journal pages)
- Use found info to query CrossRef for structured metadata

---

## D. Working Paper → Published Version Check

After all citations are resolved, check if any working papers now have published versions.

### Which entries to check

Scan the `.bib` file for entries that are:
- `@techreport` or `@unpublished`
- `@article` or `@misc` entries missing a `journal` field
- Any entry with "working paper" or "mimeo" in the `note` field

### How to check

For each candidate entry:

```bash
# Query CrossRef for journal articles matching this paper
curl -s "https://api.crossref.org/works?query.bibliographic={URL-encoded-title}+{first-author-lastname}&filter=type:journal-article&rows=3&mailto=user@example.com"
```

### Match criteria

A result is a published version if:
1. **Title similarity**: Same title or minor variation (articles may drop subtitles, change "and" to "&", etc.)
2. **Author match**: At least first author's last name matches
3. **Year**: Published year >= working paper year (papers take time to publish)
4. **Has journal**: `container-title` field is populated with a real journal name

### What to do when found

**Always show the user** the proposed update before making it:

```
Found published version of working paper:
  Current:   @techreport{mogstad2012linearity, "Linearity in Returns...", NBER, 2012}
  Published: @article in Journal of Labor Economics, 2014, vol 32(1), pp 1-34

Update entry to published version? [Y/n]
```

If approved, update the entry:
- Change type from `@techreport`/`@unpublished` to `@article`
- Add `journal`, `volume`, `number`, `pages` fields
- Update `year` to publication year
- Remove `institution`, `type`, `number` (WP series fields)
- Keep the same key (don't rename — would break all existing citations)
