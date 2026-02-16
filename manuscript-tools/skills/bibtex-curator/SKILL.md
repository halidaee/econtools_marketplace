---
name: bibtex-curator
description: Use when the user wants to fix bare/written-out citations in a Quarto or LaTeX document, convert plain-text citations to proper BibTeX citation commands, clean up a bibliography, or check if working papers have been published
---

# BibTeX Curator

Detect written-out citations in `.qmd`/`.tex` files, resolve them to BibTeX entries, replace with proper citation commands, and check working papers for published versions.

## Prerequisites

Requires 3 MCP servers (see `../../mcps/README.md` for installation):
- **semantic-scholar-mcp** — search academic papers, retrieve BibTeX
- **crossref-mcp** — search metadata, get BibTeX, find published versions
- **bibtex-mcp** — parse .bib files, scan documents, rekey entries, generate cite commands

## Constraints

- **NEVER** change the meaning of a citation (wrong paper is worse than a bare citation)
- **NEVER** delete existing proper citations (`@key`, `\cite{key}`, etc.)
- **MUST** preserve all surrounding text exactly
- **MUST** add new entries to the project's existing `.bib` file (don't create a new one)
- **MUST** match the project's existing BibTeX key convention (observe existing keys before generating new ones)

## Escalation Policy

**Ask the user when:**
- Multiple `.bib` entries match the same author-year
- API confidence score is 4–6 (ambiguous match)
- Author name could refer to different people (e.g., "Smith (2015)")
- Can't find the paper through any source
- A working paper's published version has a substantially different title (similarity < 0.8)

**Proceed automatically when:**
- Unique match found in `.bib` file
- High-confidence API match (score >= 7)
- Straightforward citation syntax replacement
- Working paper clearly published with same/near-identical title (similarity >= 0.8)

## Workflow

### Step 1: Locate Document and Bibliography

**Goal:** Identify what document to fix and where its bibliography file is

**Detect document type:**
- `.qmd` file → Quarto (uses `@key` syntax)
- `.tex` file → LaTeX (uses `\citet{key}` or `\citep{key}` syntax)

**Locate bibliography file:**
- For `.qmd`: Extract from `bibliography:` field in YAML frontmatter
- For `.tex`: Extract from `\bibliography{filename}` command
- If not found, ask user for the path to their `.bib` file

### Step 2: Scan for Bare Citations

**Goal:** Find all written-out citations (like "Author (Year)") that need to be converted to proper citation commands

Use **bibtex-mcp** tool:
```
bibtex-mcp.scan_bare_citations(path: document_path)
```

Returns array of citations with:
- `text` — matched citation text (e.g., "Conley and Udry (2010)")
- `line` — line number in document
- `authors` — extracted author last names
- `year` — extracted year
- `citation_type` — "narrative" or "parenthetical"
- `locator` — page/chapter reference if present
- `prefix`, `suffix` — additional text like "see" or "among others"

This gives us a to-do list of all citations that need fixing. Report to user: "Found N bare citations to resolve."

### Step 3: Parse Existing Bibliography

**Goal:** Index the existing `.bib` file so we can check if papers are already there before searching APIs

Use **bibtex-mcp** tool:
```
bibtex-mcp.parse_bib(path: bib_file_path)
```

Returns author-year index mapping strings like "Conley-2010" to arrays of matching entries. Each entry includes:
- `key` — BibTeX key (e.g., "conley2010learning")
- `type` — entry type (article, techreport, unpublished, etc.)
- `authors` — array of author last names
- `year`, `title`, `fields`

This lets us quickly check "is Conley (2010) already in the .bib?" before doing expensive API searches.

### Step 4: Resolve Each Citation

**Goal:** For each bare citation, figure out which paper it refers to and get its proper BibTeX key

For each bare citation detected in Step 2, resolve in priority order:

#### Priority 1: Existing .bib Match

Check if the citation's `authors` and `year` match any entry in the parsed bibliography index (from Step 3).

**If unique match found:**
- Use **bibtex-mcp** tool to generate replacement:
  ```
  bibtex-mcp.suggest_replacement(
    citation_text: original_text,
    key: matched_bib_key,
    doc_type: "qmd" or "tex",
    natbib: true
  )
  ```
- Replace the bare citation with the suggested command
- Continue to next citation

**If multiple matches found:**
- Show user the options with titles
- Ask which entry they meant
- Use selected key for replacement

**If no match found:**
- Proceed to Priority 2 (Project markdown search)

#### Priority 2: Project Markdown Search

**Goal:** Check if you've written about this paper in project notes/summaries before searching external APIs

Grep the project directory for markdown files mentioning the author + year:
```bash
grep -ri "Conley.*2010\|2010.*Conley" *.md --exclude=paper.qmd
```

Look for context like:
- Paper titles in headers or bullet points
- Journal names, DOIs, or working paper series
- Your own summaries or notes about the paper

**If context found:**
- Extract title/journal/DOI from the markdown context
- Ask user: "Found in your notes: '[title]'. Is this the paper you're citing?"
- If confirmed, search CrossRef/Semantic Scholar with the extracted title for validation
- Get BibTeX and proceed to Step 5 (Add Entry)

**If no useful context found:**
- Proceed to Priority 3 (API search)

#### Priority 3: API Search

**Goal:** Search external APIs when the paper isn't in your .bib or notes

**Try CrossRef first** (better for economics papers):
```
crossref-mcp.search(
  query: "{first_author} {title_keywords}",
  author: "{first_author}",
  year: {year},
  rows: 5
)
```

Each result includes a `confidence_score` (0-9) computed by the server:
- Author match: +3
- Year match: +2
- Title keywords: +2
- Has DOI: +1
- Is journal-article: +1

**If confidence >= 7:**
- Get BibTeX: `crossref-mcp.get_bibtex(doi: result.doi)`
- Proceed to Step 5 (Add Entry)

**If confidence 4-6:**
- Show user top 3 results with titles and confidence scores
- Ask which is correct (or none)
- Get BibTeX for selected result

**If confidence < 4 or no results:**
- Try Semantic Scholar:
  ```
  semantic-scholar-mcp.search(
    query: "{authors} {year} {title_keywords}",
    year: "{year}",
    limit: 5
  )
  ```
- Follow same confidence logic
- Get BibTeX: `semantic-scholar-mcp.get_bibtex(paper_id: result.paperId)`

**If still no match:**
- Ask user if they can provide more context (title, journal, DOI)
- Try API search again with additional info
- Or ask user to manually add the entry

### Step 5: Add New Entries to Bibliography

**Goal:** Add newly-found papers to the `.bib` file with properly formatted keys that match the project's convention

For entries found via API (in Step 4):

1. **Get raw BibTeX** (already done in Step 4)

2. **Rekey to match project convention**:
   ```
   bibtex-mcp.rekey_entry(
     bibtex: raw_bibtex_string,
     existing_keys: [list_of_all_keys_from_step_3],
     convention: "auto"
   )
   ```
   Returns BibTeX with key rewritten to match project's format (e.g., `conley2010learning`)

3. **Add to .bib file**:
   ```
   bibtex-mcp.add_entry(
     bib_path: bib_file_path,
     entry: rekeyed_bibtex
   )
   ```

4. **Generate citation command**:
   ```
   bibtex-mcp.suggest_replacement(
     citation_text: original_text,
     key: new_key,
     doc_type: "qmd" or "tex",
     natbib: true
   )
   ```

5. **Replace bare citation** in the document with the suggested command

### Step 6: Check Working Papers for Published Versions

**Goal:** Find if any unpublished papers in the `.bib` have since been published, so we can upgrade them to the published version

After resolving all citations, scan the `.bib` file for unpublished papers:

For each `@techreport` or `@unpublished` entry:
```
crossref-mcp.find_published_version(
  title: entry.title,
  author: entry.first_author,
  working_paper_year: entry.year
)
```

Returns published version with:
- Metadata (title, authors, journal, year, DOI)
- `bibtex` — BibTeX entry for published version
- Title similarity score

**If found and similarity >= 0.8:**
- Show user the working paper and published version
- Ask if they want to upgrade
- If yes, use `bibtex-mcp.rekey_entry()` and replace in .bib

**If found and similarity < 0.8:**
- Show both, note the title difference
- Ask user to verify it's the same paper
- Proceed if confirmed

**If not found:**
- No action (working paper remains as-is)

### Step 7: Final Report

**Goal:** Summarize what was accomplished

Report to user:
```
📊 Citation Curation Complete

Bare citations: X found, Y resolved
- Z resolved from existing .bib
- W resolved from CrossRef
- V resolved from Semantic Scholar
- U required user input

Working papers checked: N
- M upgraded to published versions
- P remain unpublished

Changes:
- Added Q new entries to bibliography.bib
- Replaced X bare citations with proper commands
```

## Example Session

```
User: "Fix the citations in paper.qmd"

Step 1: Found bibliography: references.bib

Step 2: Scan document
Found 5 bare citations:
   - Line 12: "Conley and Udry (2010)"
   - Line 45: "(Banerjee et al. 2013)"
   - ...

Step 3: Parsed references.bib → 47 entries indexed

Step 4: Resolve citations

   ✓ "Conley and Udry (2010)" → matched existing key `conley2010learning`
     Replaced with: @conley2010learning

   ✓ "Banerjee et al. (2013)" → not in .bib, searching APIs...
     CrossRef match (score 8): "The Miracle of Microfinance?"
     Added as `banerjee2013miracle`
     Replaced with: [@banerjee2013miracle]

   [... 3 more citations ...]

Step 6: Check working papers: 3 found
   ✓ "Mogstad (2012)" NBER → found published in AER 2015
     Upgraded to journal article

📊 Complete: 5/5 citations resolved, 1 working paper upgraded
```

## Notes on Citation Commands

### Quarto Syntax
- Narrative: `@key` → renders as "Author (Year)"
- Parenthetical: `[@key]` → renders as "(Author Year)"
- With locator: `[@key, p. 45]`
- Multiple: `[@key1; @key2]`
- Year-only: `[-@key]`

### LaTeX/natbib Syntax
- Narrative: `\citet{key}` → renders as "Author (Year)"
- Parenthetical: `\citep{key}` → renders as "(Author Year)"
- With locator: `\citep[p. 45]{key}`
- Multiple: `\citep{key1, key2}`
- Possessive: `\citeauthor{key}'s (\citeyear{key})`

The `bibtex-mcp.suggest_replacement()` tool handles these conversions automatically.

## Troubleshooting

**Issue: scan_bare_citations returns false positives**
- Check if citation is in acknowledgments or author list (tool should exclude these)
- Verify citation isn't already proper (`@key` or `\cite{}`)
- Some matches may be non-citation mentions (e.g., "World Bank (2020 fiscal year)") — skip these

**Issue: Can't find paper via any API**
- Ask user for DOI or full title
- Search with more specific query
- User may need to manually create entry

**Issue: Multiple .bib entries with same author-year**
- Show user all matching entries with titles
- Let user choose the correct one
- Never guess — wrong citation is worse than bare citation

## Reference Files (Legacy)

The `references-legacy/` directory contains the original implementation documentation:
- `citation-patterns.md` — regex patterns (now in `bibtex-mcp.scan_bare_citations()`)
- `api-lookups.md` — API instructions (now in `crossref-mcp` and `semantic-scholar-mcp` tools)
- `bibtex-formats.md` — key generation rules (now in `bibtex-mcp.rekey_entry()`)

These files are preserved for historical reference. The logic has been moved into the MCP servers for deterministic, testable implementation.
