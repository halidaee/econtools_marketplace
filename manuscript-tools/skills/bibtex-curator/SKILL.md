---
name: bibtex-curator
description: Use when the user wants to fix bare/written-out citations in a Quarto or LaTeX document, convert plain-text citations to proper BibTeX citation commands, clean up a bibliography, or check if working papers have been published
---

# BibTeX Curator

Detect written-out citations in `.qmd`/`.tex` files, resolve them to BibTeX entries, replace with proper citation commands, and check working papers for published versions.

## Constraints

- **NEVER** change the meaning of a citation (wrong paper is worse than a bare citation)
- **NEVER** delete existing proper citations (`@key`, `\cite{key}`, etc.)
- **MUST** preserve all surrounding text exactly
- **MUST** add new entries to the project's existing `.bib` file (don't create a new one)
- **MUST** match the project's existing BibTeX key convention (observe existing keys before generating new ones)

## Escalation Policy

**Ask the user when:**
- Multiple `.bib` entries match the same author-year
- CrossRef returns ambiguous results (confidence score 4–6 per `references/api-lookups.md`)
- Author name could refer to different people (e.g., "Smith (2015)")
- Can't find the paper through any source
- A working paper's published version has a substantially different title

**Proceed automatically when:**
- Unique match found in `.bib` file
- High-confidence API match (score >= 7)
- Straightforward citation syntax replacement
- Working paper clearly published with same/near-identical title

## Workflow

1. **Detect document type**: `.qmd` = Quarto (`@key` syntax), `.tex` = LaTeX/natbib (`\citet`/`\citep` syntax)
2. **Locate `.bib` file**: Check `bibliography:` in YAML frontmatter (Quarto) or `\bibliography{}` command (LaTeX)
3. **Index `.bib` entries**: Read the `.bib` file, index all entries by author last name(s) + year
4. **Scan for bare citations**: Use patterns from `references/citation-patterns.md` to find written-out citations
5. **Resolve each citation** in priority order:
   - **(i) `.bib` match**: If author-year matches an existing entry → replace with proper cite command using that key
   - **(ii) Project markdown search**: Grep `.md` files for author names + year → extract context (title, journal) → create BibTeX entry per `references/bibtex-formats.md` → validate via CrossRef → add to `.bib` → replace
   - **(iii) API search**: Query CrossRef/Semantic Scholar per `references/api-lookups.md` → create entry → add to `.bib` → replace
6. **Check working papers**: After all citations resolved, scan `.bib` for `@techreport`/`@unpublished` entries → check for published versions per `references/api-lookups.md` section D
7. **Report**: N bare citations found, N resolved automatically, N required user input, N working papers checked, N upgraded to published version
